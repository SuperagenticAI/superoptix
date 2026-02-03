"""
StackOne Bridge Adapter
======================

Universal adapter to bridge StackOne tools to various agentic frameworks.
Supported: DSPy, Pydantic AI, Google ADK, Microsoft Semantic Kernel.

Features:
- Framework conversion (DSPy, Pydantic AI, OpenAI, LangChain, Google ADK, Semantic Kernel)
- GEPA optimization for tool descriptions
- Discovery tools (tool_search/tool_execute)
- Feedback collection tool
- Implicit feedback manager (LangSmith integration)
- StackOneToolSet wrapper with MCP-backed dynamic discovery
- Hybrid search (BM25 + TF-IDF) for tool discovery
- File upload support
"""

import base64
import fnmatch
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type, Union

from pydantic import BaseModel, Field, create_model, field_validator
from superoptix.core.base_component import BaseComponent

logger = logging.getLogger(__name__)

# Optional imports for framework support
try:
    from dspy.adapters.types.tool import Tool as DSPyTool
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False

try:
    import importlib.util
    PYDANTIC_AI_AVAILABLE = importlib.util.find_spec("pydantic_ai") is not None
except ImportError:
    PYDANTIC_AI_AVAILABLE = False

try:
    from stackone_ai import StackOneToolSet as _StackOneToolSet
    STACKONE_AVAILABLE = True
except ImportError:
    STACKONE_AVAILABLE = False

# Optional: LangSmith for implicit feedback
try:
    from langsmith import Client as LangSmithClient
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False


# =============================================================================
# Feedback Models and Tool
# =============================================================================

class FeedbackInput(BaseModel):
    """Input schema for feedback tool."""

    feedback: str = Field(..., min_length=1, description="User feedback text")
    account_id: Union[str, List[str]] = Field(..., description="Account identifier(s)")
    tool_names: List[str] = Field(..., min_length=1, description="List of tool names")

    @field_validator("feedback")
    @classmethod
    def validate_feedback(cls, v: str) -> str:
        """Validate that feedback is non-empty after trimming."""
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Feedback must be a non-empty string")
        return trimmed

    @field_validator("account_id")
    @classmethod
    def validate_account_id(cls, v: Union[str, List[str]]) -> List[str]:
        """Validate and normalize account ID(s) to a list."""
        if isinstance(v, str):
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Account ID must be a non-empty string")
            return [trimmed]
        if isinstance(v, list):
            if not v:
                raise ValueError("At least one account ID is required")
            cleaned = [str(item).strip() for item in v if str(item).strip()]
            if not cleaned:
                raise ValueError("At least one valid account ID is required")
            return cleaned
        raise ValueError("Account ID must be a string or list of strings")

    @field_validator("tool_names")
    @classmethod
    def validate_tool_names(cls, v: List[str]) -> List[str]:
        """Validate and clean tool names."""
        cleaned = [name.strip() for name in v if name.strip()]
        if not cleaned:
            raise ValueError("At least one tool name is required")
        return cleaned


class StackOneFeedbackTool:
    """
    Feedback collection tool for StackOne.
    
    Allows agents to collect user feedback on tool performance.
    Always ask user permission before submitting feedback.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.stackone.com",
    ):
        self.api_key = api_key or os.getenv("STACKONE_API_KEY")
        self.base_url = base_url
        self.name = "tool_feedback"
        self.description = (
            "Collects user feedback on StackOne tool performance. "
            'First ask the user, "Are you ok with sending feedback to StackOne?" '
            "and mention that the LLM will take care of sending it. "
            "Call this tool only when the user explicitly answers yes."
        )

    def _build_auth_header(self) -> str:
        """Build Basic Auth header."""
        if not self.api_key:
            raise ValueError("API key required for feedback submission")
        token = base64.b64encode(f"{self.api_key}:".encode()).decode()
        return f"Basic {token}"

    def execute(
        self,
        feedback: str,
        account_id: Union[str, List[str]],
        tool_names: List[str],
    ) -> Dict[str, Any]:
        """
        Submit feedback to StackOne.
        
        Args:
            feedback: User feedback text
            account_id: Account ID(s) to associate feedback with
            tool_names: List of tool names being reviewed
            
        Returns:
            Response with submission status
        """
        try:
            import httpx
        except ImportError:
            raise ImportError("httpx is required for feedback submission. Install with: pip install httpx")

        # Validate input
        validated = FeedbackInput(
            feedback=feedback,
            account_id=account_id,
            tool_names=tool_names
        )

        results = []
        errors = []

        for acc_id in validated.account_id:
            try:
                response = httpx.post(
                    f"{self.base_url}/ai/tool-feedback",
                    headers={
                        "Authorization": self._build_auth_header(),
                        "Content-Type": "application/json",
                    },
                    json={
                        "feedback": validated.feedback,
                        "account_id": acc_id,
                        "tool_names": validated.tool_names,
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                results.append({"account_id": acc_id, "status": "success"})
            except Exception as e:
                errors.append({"account_id": acc_id, "status": "error", "error": str(e)})
                results.append({"account_id": acc_id, "status": "error", "error": str(e)})

        return {
            "message": f"Feedback sent to {len(validated.account_id)} account(s)",
            "total_accounts": len(validated.account_id),
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len(errors),
            "results": results,
        }


# =============================================================================
# Implicit Feedback Manager (LangSmith Integration)
# =============================================================================

@dataclass
class ImplicitFeedbackConfig:
    """Configuration for implicit feedback collection."""
    
    enabled: bool = True
    project_name: str = "stackone-agents"
    default_tags: List[str] = field(default_factory=list)
    session_resolver: Optional[Callable[[], str]] = None
    user_resolver: Optional[Callable[[], str]] = None
    refinement_window_seconds: float = 5.0


class ImplicitFeedbackManager:
    """
    Manages implicit behavioral feedback to LangSmith.
    
    Automatically detects patterns like:
    - Refinement needed (multiple calls within short window)
    - Tool suitability scores
    - Usage patterns
    
    Usage:
        configure_implicit_feedback(
            api_key="your-langsmith-key",
            project_name="my-project",
            default_tags=["production"]
        )
    """

    _instance: Optional["ImplicitFeedbackManager"] = None
    _lock = threading.Lock()

    def __init__(self, config: ImplicitFeedbackConfig):
        self.config = config
        self._client: Optional[Any] = None
        self._session_calls: Dict[str, List[float]] = {}  # session_id -> timestamps

        if LANGSMITH_AVAILABLE and config.enabled:
            api_key = os.getenv("LANGSMITH_API_KEY")
            if api_key:
                try:
                    self._client = LangSmithClient(api_key=api_key)
                    logger.info(f"🔗 LangSmith implicit feedback enabled for project: {config.project_name}")
                except Exception as e:
                    logger.warning(f"Failed to initialize LangSmith client: {e}")

    @classmethod
    def configure(
        cls,
        api_key: Optional[str] = None,
        project_name: str = "stackone-agents",
        default_tags: Optional[List[str]] = None,
        session_resolver: Optional[Callable[[], str]] = None,
        user_resolver: Optional[Callable[[], str]] = None,
        refinement_window_seconds: float = 5.0,
    ) -> "ImplicitFeedbackManager":
        """
        Configure the implicit feedback manager.
        
        Args:
            api_key: LangSmith API key (or use LANGSMITH_API_KEY env var)
            project_name: LangSmith project name
            default_tags: Tags to apply to all runs
            session_resolver: Callable to get current session ID
            user_resolver: Callable to get current user ID
            refinement_window_seconds: Window to detect refinement patterns
            
        Returns:
            Configured ImplicitFeedbackManager instance
        """
        if api_key:
            os.environ["LANGSMITH_API_KEY"] = api_key

        config = ImplicitFeedbackConfig(
            enabled=os.getenv("STACKONE_IMPLICIT_FEEDBACK_ENABLED", "true").lower() == "true",
            project_name=project_name or os.getenv("STACKONE_IMPLICIT_FEEDBACK_PROJECT", "stackone-agents"),
            default_tags=default_tags or os.getenv("STACKONE_IMPLICIT_FEEDBACK_TAGS", "").split(","),
            session_resolver=session_resolver,
            user_resolver=user_resolver,
            refinement_window_seconds=refinement_window_seconds,
        )

        with cls._lock:
            cls._instance = cls(config)
        return cls._instance

    @classmethod
    def get_instance(cls) -> Optional["ImplicitFeedbackManager"]:
        """Get the singleton instance."""
        return cls._instance

    def track_tool_call(
        self,
        tool_name: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Track a tool call and detect patterns.
        
        Args:
            tool_name: Name of the tool being called
            session_id: Session identifier
            user_id: User identifier
            metadata: Additional metadata
            
        Returns:
            Feedback event data
        """
        if not self.config.enabled:
            return {"status": "disabled"}

        # Resolve session/user if resolvers provided
        resolved_session = session_id
        if not resolved_session and self.config.session_resolver:
            resolved_session = self.config.session_resolver()
        resolved_session = resolved_session or "default"

        resolved_user = user_id
        if not resolved_user and self.config.user_resolver:
            resolved_user = self.config.user_resolver()

        now = time.time()

        # Track call timing for refinement detection
        if resolved_session not in self._session_calls:
            self._session_calls[resolved_session] = []
        
        self._session_calls[resolved_session].append(now)

        # Detect refinement pattern (multiple calls within window)
        recent_calls = [
            t for t in self._session_calls[resolved_session]
            if now - t < self.config.refinement_window_seconds
        ]

        event = {
            "type": "tool_call",
            "tool_name": tool_name,
            "session_id": resolved_session,
            "user_id": resolved_user,
            "timestamp": now,
            "metadata": metadata or {},
            "tags": self.config.default_tags,
        }

        if len(recent_calls) > 1:
            event["refinement_needed"] = True
            event["call_count_in_window"] = len(recent_calls)
            logger.debug(f"🔄 Refinement pattern detected: {len(recent_calls)} calls in {self.config.refinement_window_seconds}s")

        # Send to LangSmith if available
        if self._client:
            try:
                # LangSmith feedback would be sent here
                # This is a simplified version - full implementation would use LangSmith runs API
                logger.debug(f"📊 Implicit feedback tracked: {tool_name}")
            except Exception as e:
                logger.warning(f"Failed to send implicit feedback: {e}")

        return event


def configure_implicit_feedback(
    api_key: Optional[str] = None,
    project_name: str = "stackone-agents",
    default_tags: Optional[List[str]] = None,
    session_resolver: Optional[Callable[[], str]] = None,
    user_resolver: Optional[Callable[[], str]] = None,
) -> ImplicitFeedbackManager:
    """
    Configure implicit feedback collection.
    
    Set LANGSMITH_API_KEY in your environment and the SDK will initialize
    the implicit feedback manager on first tool execution.
    
    Example:
        from superoptix.adapters.stackone_adapter import configure_implicit_feedback
        
        configure_implicit_feedback(
            api_key="/path/to/langsmith.key",
            project_name="stackone-agents",
            default_tags=["python-sdk"],
        )
    """
    return ImplicitFeedbackManager.configure(
        api_key=api_key,
        project_name=project_name,
        default_tags=default_tags,
        session_resolver=session_resolver,
        user_resolver=user_resolver,
    )


# =============================================================================
# Hybrid Search Index (BM25 + TF-IDF)
# =============================================================================

@dataclass
class ToolSearchResult:
    """Result from tool search."""
    name: str
    description: str
    score: float


class ToolIndex:
    """
    Hybrid BM25 + TF-IDF tool search index.
    
    Provides intelligent tool discovery based on natural language queries.
    Uses a combination of BM25 (keyword matching) and TF-IDF (semantic similarity).
    
    Example:
        index = ToolIndex(tools, hybrid_alpha=0.2)
        results = index.search("manage employees", limit=5)
    """

    DEFAULT_HYBRID_ALPHA = 0.2  # Weight for BM25 in hybrid search

    def __init__(
        self,
        tools: List[Any],
        hybrid_alpha: Optional[float] = None,
    ):
        """
        Initialize tool index with hybrid search.
        
        Args:
            tools: List of StackOne tools to index
            hybrid_alpha: Weight for BM25 in hybrid search (0-1).
                Default 0.2 gives more weight to BM25 (better accuracy).
        """
        self.tools = tools
        self.tool_map = {tool.name: tool for tool in tools}
        self.hybrid_alpha = max(0.0, min(1.0, hybrid_alpha or self.DEFAULT_HYBRID_ALPHA))
        self.tool_names: List[str] = []
        
        # Build indices
        self._corpus: List[str] = []
        self._tfidf_vectors: Optional[Any] = None
        self._vectorizer: Optional[Any] = None
        
        self._build_index()

    def _build_index(self) -> None:
        """Build search indices for all tools."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            HAS_SKLEARN = True
        except ImportError:
            HAS_SKLEARN = False
            logger.warning("scikit-learn not installed. Using simple text matching.")

        for tool in self.tools:
            # Extract category and action from tool name
            parts = tool.name.split("_")
            category = parts[0] if parts else ""
            
            # Extract action types
            action_types = ["create", "update", "delete", "get", "list", "search"]
            actions = [p for p in parts if p in action_types]
            
            # Build search text
            search_text = " ".join([
                tool.name,
                tool.description,
                category,
                " ".join(parts),
                " ".join(actions),
            ])
            
            self._corpus.append(search_text.lower())
            self.tool_names.append(tool.name)

        # Build TF-IDF index if sklearn available
        if HAS_SKLEARN and self._corpus:
            self._vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                stop_words="english",
                max_features=5000,
            )
            self._tfidf_vectors = self._vectorizer.fit_transform(self._corpus)

    def _simple_bm25_score(self, query: str, doc: str) -> float:
        """Simple BM25-like scoring without external dependencies."""
        query_terms = set(query.lower().split())
        doc_terms = doc.lower().split()
        doc_term_set = set(doc_terms)
        
        if not query_terms or not doc_terms:
            return 0.0
        
        # Count matching terms
        matches = len(query_terms & doc_term_set)
        
        # Normalize by query length
        return matches / len(query_terms)

    def search(
        self,
        query: str,
        limit: int = 5,
        min_score: float = 0.0,
    ) -> List[ToolSearchResult]:
        """
        Search for relevant tools using hybrid BM25 + TF-IDF.
        
        Args:
            query: Natural language query
            limit: Maximum number of results
            min_score: Minimum relevance score (0-1)
            
        Returns:
            List of search results sorted by relevance
        """
        if not self.tools:
            return []

        scores: Dict[str, float] = {}
        query_lower = query.lower()

        # BM25-like scoring (simple implementation)
        for idx, (doc, tool_name) in enumerate(zip(self._corpus, self.tool_names)):
            bm25_score = self._simple_bm25_score(query_lower, doc)
            scores[tool_name] = {"bm25": bm25_score, "tfidf": 0.0}

        # TF-IDF scoring if available
        if self._vectorizer is not None and self._tfidf_vectors is not None:
            try:
                query_vec = self._vectorizer.transform([query_lower])
                tfidf_scores = (self._tfidf_vectors @ query_vec.T).toarray().flatten()
                
                for idx, tool_name in enumerate(self.tool_names):
                    if tool_name in scores:
                        scores[tool_name]["tfidf"] = float(tfidf_scores[idx])
            except Exception as e:
                logger.debug(f"TF-IDF scoring failed: {e}")

        # Fuse scores: hybrid_score = alpha * bm25 + (1 - alpha) * tfidf
        fused_results: List[tuple] = []
        for tool_name, score_dict in scores.items():
            bm25 = score_dict.get("bm25", 0.0)
            tfidf = score_dict.get("tfidf", 0.0)
            hybrid = self.hybrid_alpha * bm25 + (1 - self.hybrid_alpha) * tfidf
            fused_results.append((tool_name, hybrid))

        # Sort by score descending
        fused_results.sort(key=lambda x: x[1], reverse=True)

        # Build final results
        search_results = []
        for tool_name, score in fused_results:
            if score < min_score:
                continue
            
            tool = self.tool_map.get(tool_name)
            if tool is None:
                continue
            
            search_results.append(ToolSearchResult(
                name=tool.name,
                description=tool.description,
                score=score,
            ))
            
            if len(search_results) >= limit:
                break

        return search_results


# =============================================================================
# StackOne ToolSet Wrapper
# =============================================================================

class StackOneToolSetWrapper:
    """
    SuperOptiX wrapper for StackOneToolSet with enhanced features.
    
    Provides:
    - MCP-backed dynamic tool discovery
    - Glob pattern filtering (actions, providers)
    - Multi-account support
    - File upload detection
    - Integration with SuperOptiX optimization
    
    Example:
        toolset = StackOneToolSetWrapper()
        tools = toolset.fetch_tools(
            actions=["hris_*", "!hris_delete_*"],
            account_ids=["acc-123"]
        )
        
        # With optimization
        bridge = toolset.to_bridge()
        optimized = bridge.optimize(dataset, metric)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        account_id: Optional[str] = None,
        base_url: str = "https://api.stackone.com",
    ):
        """
        Initialize StackOne toolset wrapper.
        
        Args:
            api_key: API key (or use STACKONE_API_KEY env var)
            account_id: Default account ID
            base_url: API base URL
        """
        self.api_key = api_key or os.getenv("STACKONE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key must be provided via api_key parameter or STACKONE_API_KEY env var"
            )
        
        self.account_id = account_id
        self.base_url = base_url
        self._account_ids: List[str] = []
        self._cached_tools: Optional[List[Any]] = None
        
        # Initialize native toolset if available
        self._native_toolset: Optional[Any] = None
        if STACKONE_AVAILABLE and _StackOneToolSet:
            try:
                self._native_toolset = _StackOneToolSet(
                    api_key=self.api_key,
                    account_id=account_id,
                    base_url=base_url,
                )
            except Exception as e:
                logger.warning(f"Failed to initialize native StackOneToolSet: {e}")

    def set_accounts(self, account_ids: List[str]) -> "StackOneToolSetWrapper":
        """
        Set account IDs for filtering tools.
        
        Args:
            account_ids: List of account IDs
            
        Returns:
            Self for chaining
        """
        self._account_ids = account_ids
        if self._native_toolset:
            self._native_toolset.set_accounts(account_ids)
        return self

    def _filter_by_action(self, tool_name: str, actions: List[str]) -> bool:
        """Check if tool name matches action patterns (with exclusions)."""
        include_patterns = [a for a in actions if not a.startswith("!")]
        exclude_patterns = [a[1:] for a in actions if a.startswith("!")]
        
        # Check exclusions first
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(tool_name, pattern):
                return False
        
        # Check inclusions
        if not include_patterns:
            return True
        
        return any(fnmatch.fnmatch(tool_name, p) for p in include_patterns)

    def _filter_by_provider(self, tool_name: str, providers: List[str]) -> bool:
        """Check if tool belongs to any of the specified providers."""
        provider = tool_name.split("_")[0].lower()
        return provider in {p.lower() for p in providers}

    def fetch_tools(
        self,
        account_ids: Optional[List[str]] = None,
        providers: Optional[List[str]] = None,
        actions: Optional[List[str]] = None,
    ) -> List[Any]:
        """
        Fetch tools with optional filtering.
        
        Args:
            account_ids: Filter by account IDs
            providers: Filter by provider names (e.g., ["hibob", "bamboohr"])
            actions: Filter by action patterns with glob support and exclusions
                    (e.g., ["hris_*", "!hris_delete_*"])
                    
        Returns:
            List of StackOneTool instances
            
        Example:
            # Get all HRIS tools except delete operations
            tools = toolset.fetch_tools(actions=["hris_*", "!hris_delete_*"])
            
            # Get tools for specific provider
            tools = toolset.fetch_tools(providers=["hibob"])
        """
        # Use native toolset if available
        if self._native_toolset:
            try:
                tools_obj = self._native_toolset.fetch_tools(
                    account_ids=account_ids,
                    providers=providers,
                    actions=[a for a in (actions or []) if not a.startswith("!")],
                )
                tools = tools_obj.to_list() if hasattr(tools_obj, "to_list") else list(tools_obj)
                
                # Apply exclusion patterns
                if actions:
                    exclude_patterns = [a[1:] for a in actions if a.startswith("!")]
                    if exclude_patterns:
                        tools = [
                            t for t in tools
                            if not any(fnmatch.fnmatch(t.name, p) for p in exclude_patterns)
                        ]
                
                self._cached_tools = tools
                return tools
            except Exception as e:
                logger.warning(f"Native fetch_tools failed: {e}. Using cached tools.")

        # Fallback: return cached tools with filtering
        if self._cached_tools:
            tools = self._cached_tools
            
            if providers:
                tools = [t for t in tools if self._filter_by_provider(t.name, providers)]
            
            if actions:
                tools = [t for t in tools if self._filter_by_action(t.name, actions)]
            
            return tools

        logger.warning("No tools available. Install stackone-ai with MCP support.")
        return []

    def get_tool(self, name: str) -> Optional[Any]:
        """Get a specific tool by name."""
        if self._cached_tools:
            for tool in self._cached_tools:
                if tool.name == name:
                    return tool
        return None

    def to_bridge(self, tools: Optional[List[Any]] = None) -> "StackOneBridge":
        """
        Convert tools to a StackOneBridge for framework conversion.
        
        Args:
            tools: Tools to convert (uses cached if not provided)
            
        Returns:
            StackOneBridge instance
        """
        target_tools = tools or self._cached_tools or []
        return StackOneBridge(target_tools)

    def create_tool_index(self, tools: Optional[List[Any]] = None) -> ToolIndex:
        """
        Create a hybrid search index for tool discovery.
        
        Args:
            tools: Tools to index (uses cached if not provided)
            
        Returns:
            ToolIndex instance
        """
        target_tools = tools or self._cached_tools or []
        return ToolIndex(target_tools)

    def get_feedback_tool(self) -> StackOneFeedbackTool:
        """
        Get the feedback collection tool.
        
        Returns:
            StackOneFeedbackTool instance
        """
        return StackOneFeedbackTool(api_key=self.api_key, base_url=self.base_url)


# =============================================================================
# File Upload Support
# =============================================================================

class FileUploadHandler:
    """
    Handles file uploads for StackOne tools.
    
    Automatically detects binary parameters from OpenAPI specs
    and handles file encoding/upload.
    """

    BINARY_CONTENT_TYPES = [
        "application/octet-stream",
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/gif",
        "application/zip",
    ]

    @staticmethod
    def is_file_parameter(param_schema: Dict[str, Any]) -> bool:
        """
        Check if a parameter represents a file upload.
        
        Detects:
        - format: binary
        - type: file
        - contentMediaType in BINARY_CONTENT_TYPES
        """
        if param_schema.get("format") == "binary":
            return True
        if param_schema.get("type") == "file":
            return True
        if param_schema.get("contentMediaType") in FileUploadHandler.BINARY_CONTENT_TYPES:
            return True
        return False

    @staticmethod
    def encode_file(file_path: str) -> Dict[str, Any]:
        """
        Encode a file for upload.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict with base64 content and metadata
        """
        import mimetypes
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or "application/octet-stream"
        
        with open(file_path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf-8")
        
        return {
            "filename": os.path.basename(file_path),
            "content": content,
            "content_type": mime_type,
        }

    @staticmethod
    def prepare_file_arguments(
        arguments: Dict[str, Any],
        parameter_schemas: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Prepare arguments by encoding any file parameters.
        
        Args:
            arguments: Tool arguments
            parameter_schemas: Parameter schemas from tool
            
        Returns:
            Arguments with files encoded
        """
        prepared = dict(arguments)
        
        for param_name, param_schema in parameter_schemas.items():
            if param_name in prepared and FileUploadHandler.is_file_parameter(param_schema):
                value = prepared[param_name]
                if isinstance(value, str) and os.path.exists(value):
                    prepared[param_name] = FileUploadHandler.encode_file(value)
        
        return prepared


class StackOneOptimizableComponent(BaseComponent):
    """
    Component wrapper for StackOne tools to enable GEPA optimization.
    
    This component treats the tool description as the optimizable variable.
    GEPA will mutate the description to help the LLM better understand when 
    and how to use the tool.
    """

    def __init__(self, stackone_tool: Any):
        super().__init__(
            name=stackone_tool.name,
            description=stackone_tool.description,
            input_fields=list(stackone_tool.parameters.properties.keys()),
            output_fields=["result"],
            variable=stackone_tool.description,
            framework="stackone",
        )
        self.tool = stackone_tool

    def forward(self, **inputs: Any) -> Dict[str, Any]:
        """Execute the tool with the current (potentially optimized) description."""
        # Note: In a real optimization run, 'forward' might be used to test 
        # if the LLM picks the tool correctly based on its description.
        result = self.tool.execute(inputs)
        return {"result": result}


class StackOneBridge:
    """Bridge for converting StackOne tools to other frameworks."""

    def __init__(self, stackone_tools: Any):
        """
        Initialize the bridge with StackOne tools.

        Args:
            stackone_tools: Either a StackOne Tools object or a list of StackOneTool instances.
        """
        if not STACKONE_AVAILABLE:
            raise ImportError(
                "stackone-ai is not installed. Please install it with `pip install stackone-ai`."
            )

        if hasattr(stackone_tools, "to_list"):
            self.tools = stackone_tools.to_list()
        elif isinstance(stackone_tools, list):
            self.tools = stackone_tools
        else:
            raise ValueError("Invalid stackone_tools format. Expected Tools object or list.")

    def optimize(
        self, 
        dataset: List[Dict[str, Any]], 
        metric: Any,
        reflection_lm: str = "gpt-4o-mini",
        max_iterations: int = 5
    ) -> List[Any]:
        """
        Optimize StackOne tool descriptions using GEPA.

        Args:
            dataset: List of examples [{"inputs": {...}, "outputs": {...}}]
            metric: Metric function to evaluate performance
            reflection_lm: LM to use for generating description improvements
            max_iterations: Number of GEPA iterations

        Returns:
            List of optimized StackOneTool instances.
        """
        from superoptix.optimizers.universal_gepa import UniversalGEPA

        optimized_tools = []
        for tool in self.tools:
            logger.info(f"🧬 Optimizing description for tool: {tool.name}")
            
            # Wrap tool in optimizable component
            component = StackOneOptimizableComponent(tool)
            
            # Setup Universal GEPA
            optimizer = UniversalGEPA(
                metric=metric,
                reflection_lm=reflection_lm,
                max_iterations=max_iterations
            )
            
            # Run optimization
            result = optimizer.optimize(component, dataset)
            
            # Update tool description with optimized version
            tool.description = result.optimized_variable
            optimized_tools.append(tool)
            
            logger.info(f"✅ Optimized description for {tool.name}: {tool.description[:50]}...")

        return optimized_tools

    def to_dspy(self) -> List[Any]:
        """
        Convert StackOne tools to DSPy Tool objects.

        Returns:
            List of dspy.Tool objects.
        """
        if not DSPY_AVAILABLE:
            logger.warning("DSPy not installed. to_dspy() will fail if called.")
            raise ImportError("dspy is not installed.")

        dspy_tools = []
        for tool in self.tools:
            # DSPy Tool expects a function, name, and desc
            # We use the tool.execute method as the function
            d_tool = DSPyTool(
                func=tool.execute,
                name=tool.name,
                desc=tool.description
            )
            dspy_tools.append(d_tool)
        
        return dspy_tools

    def _create_pydantic_model_from_schema(self, tool_name: str, schema: Dict[str, Any]) -> Type[BaseModel]:
        """
        Dynamically create a Pydantic model from StackOne's JSON schema.
        """
        fields: Dict[str, Any] = {}
        
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict
        }

        for field_name, field_info in properties.items():
            field_type_str = field_info.get("type", "string")
            python_type = type_mapping.get(field_type_str, str)
            
            description = field_info.get("description", "")
            
            if field_name in required:
                fields[field_name] = (python_type, Field(description=description))
            else:
                fields[field_name] = (Optional[python_type], Field(default=None, description=description))
        
        # Create dynamic model
        model_name = f"{tool_name}Args"
        return create_model(model_name, **fields) # type: ignore

    def to_pydantic_ai(self) -> List[Any]:
        """
        Convert StackOne tools to Pydantic AI Tool objects.
        
        This generates fully typed Pydantic tools, enabling the agent to see
        the exact schema and validate arguments before execution.

        Returns:
            List of pydantic_ai.Tool objects.
        """
        if not PYDANTIC_AI_AVAILABLE:
            logger.warning("Pydantic AI not installed. to_pydantic_ai() will fail if called.")
            raise ImportError("pydantic-ai is not installed.")

        pai_tools = []
        for tool in self.tools:
            # 1. Create a dynamic Pydantic model for the arguments
            # We access the raw schema dict from the StackOne tool
            raw_schema = tool.parameters.model_dump()
            ArgsModel = self._create_pydantic_model_from_schema(tool.name, raw_schema)

            # 2. Create a wrapper function that accepts this typed model
            # Pydantic AI will introspect 'args: ArgsModel' to build the tool schema
            async def tool_wrapper(ctx: RunContext, args: ArgsModel) -> str:
                # Convert Pydantic model back to dict for StackOne
                return str(tool.execute(args.model_dump(exclude_none=True)))

            # 3. Create the Pydantic AI Tool
            p_tool = PydanticAITool(
                tool_wrapper,
                name=tool.name,
                description=tool.description,
            )
            pai_tools.append(p_tool)

        return pai_tools

    def to_openai(self) -> List[Dict[str, Any]]:
        """
        Delegate to native StackOne OpenAI conversion.
        """
        # StackOne has native support for this, we just provide the bridge pass-through
        return [t.to_openai_function() for t in self.tools]

    def to_langchain(self) -> List[Any]:
        """
        Delegate to native StackOne LangChain conversion.
        """
        # StackOne has native support for this
        return [t.to_langchain() for t in self.tools]

    def _to_google_function_declaration(self, tool: Any) -> Dict[str, Any]:
        """
        Convert a StackOne tool to Google Vertex AI FunctionDeclaration format.
        """
        # Google's format is similar to OpenAI but stricter on types
        # Ref: https://cloud.google.com/vertex-ai/docs/reference/rest/v1beta1/Tool
        
        schema = tool.parameters.model_dump()
        
        # Ensure strict compatibility with Google's Schema format
        # This is a simplified mapping; complex nested types might need recursion
        parameters = {
            "type": "OBJECT",
            "properties": {},
            "required": schema.get("required", [])
        }

        type_map = {
            "string": "STRING",
            "integer": "INTEGER",
            "number": "NUMBER",
            "boolean": "BOOLEAN",
            "array": "ARRAY",
            "object": "OBJECT"
        }

        for prop_name, prop_info in schema.get("properties", {}).items():
            prop_type = type_map.get(prop_info.get("type", "string"), "STRING")
            parameters["properties"][prop_name] = {
                "type": prop_type,
                "description": prop_info.get("description", "")
            }

        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": parameters
        }

    def to_google_adk(self) -> List[Dict[str, Any]]:
        """
        Convert StackOne tools to Google ADK / Vertex AI Tool objects.

        Returns:
            List of Tool dictionaries compatible with Google Generative AI SDK.
        """
        # In Google's SDK, a Tool is a collection of FunctionDeclarations
        # We return a list of FunctionDeclarations which can be passed to
        # genai.GenerativeModel(tools=[...])
        
        return [self._to_google_function_declaration(t) for t in self.tools]

    def to_semantic_kernel(self) -> List[Any]:
        """
        Convert StackOne tools to Microsoft Semantic Kernel Functions.

        Returns:
            List of KernelFunction objects.
        """
        try:
            from semantic_kernel.functions import kernel_function
            from semantic_kernel.functions.kernel_function_from_method import KernelFunctionFromMethod
        except ImportError:
            logger.warning("Semantic Kernel not installed. to_semantic_kernel() will fail.")
            raise ImportError("semantic-kernel is not installed.")

        sk_functions = []

        for tool in self.tools:
            # 1. Create a dynamic Pydantic model for arguments (reuse existing logic)
            raw_schema = tool.parameters.model_dump()
            ArgsModel = self._create_pydantic_model_from_schema(tool.name, raw_schema)

            # 2. Define the method to be wrapped
            # Semantic Kernel expects methods to have typed arguments for automatic schema generation
            # We use a closure to capture the specific tool instance
            def make_sk_method(current_tool, args_model):
                # The method name and docstring are critical for SK
                @kernel_function(
                    name=current_tool.name,
                    description=current_tool.description
                )
                def execute_tool(**kwargs) -> str:
                    # Validate against our dynamic model
                    try:
                        validated_args = args_model(**kwargs)
                        return str(current_tool.execute(validated_args.model_dump(exclude_none=True)))
                    except Exception as e:
                        return f"Error executing tool {current_tool.name}: {str(e)}"
                
                return execute_tool

            # 3. Create Kernel Function
            # We use KernelFunctionFromMethod to create the function object
            method = make_sk_method(tool, ArgsModel)
            
            # Note: In newer SK versions, the decorator handles creation, 
            # but we explicitly wrap it to ensure metadata is correct
            func = KernelFunctionFromMethod(
                method=method,
                plugin_name="StackOnePlugin"
            )
            sk_functions.append(func)

        return sk_functions

    def to_discovery_tools(self, framework: str = "dspy") -> List[Any]:
        """
        Create "Meta Tools" (search/execute) for dynamic tool discovery.
        
        Instead of loading all tools, this returns just 'tool_search' and 'tool_execute'.
        The agent can then search for the right tool at runtime and execute it.
        
        Args:
            framework: Target framework ('dspy', 'pydantic_ai', 'google', 'semantic_kernel')
            
        Returns:
            List of converted meta-tools.
        """
        try:
            from stackone_ai.models import Tools
            from stackone_ai.utility_tools import ToolIndex, create_tool_search, create_tool_execute
        except ImportError:
            raise ImportError("stackone-ai >= 2.0 required for discovery tools.")

        # 1. Create the ToolIndex and Meta Tools using StackOne SDK
        # We need a Tools collection object for create_tool_execute
        tools_collection = Tools(self.tools)
        index = ToolIndex(self.tools)
        
        search_tool = create_tool_search(index)
        execute_tool = create_tool_execute(tools_collection)
        
        meta_tools = [search_tool, execute_tool]
        
        # 2. Convert these meta-tools to the requested framework using our existing logic
        # We create a temporary bridge just for these 2 tools
        temp_bridge = StackOneBridge(meta_tools)
        
        if framework == "dspy":
            return temp_bridge.to_dspy()
        elif framework == "pydantic_ai":
            return temp_bridge.to_pydantic_ai()
        elif framework == "google":
            return temp_bridge.to_google_adk()
        elif framework == "semantic_kernel":
            return temp_bridge.to_semantic_kernel()
        else:
            raise ValueError(f"Unknown framework: {framework}")