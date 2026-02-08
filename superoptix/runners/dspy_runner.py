"""DSPy Runner for executing agent pipelines."""

import importlib.util
import inspect
import os
import re
import sys
import threading
import time
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import dspy
import yaml
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from superoptix.runners.dspy_runtime_helpers import set_tool_trace_emitter

try:
    from superoptix.core.rag_mixin import RAGMixin

    RAG_MIXIN_AVAILABLE = True
except Exception:
    RAGMixin = None
    RAG_MIXIN_AVAILABLE = False

try:
    from superoptix.memory import AgentMemory, FileBackend, RedisBackend, SQLiteBackend

    MEMORY_AVAILABLE = True
except Exception:
    AgentMemory = None
    FileBackend = None
    RedisBackend = None
    SQLiteBackend = None
    MEMORY_AVAILABLE = False

console = Console()


def to_pascal_case(text: str) -> str:
    """
    Converts snake_case or kebab-case to PascalCase, preserving compound words.

    Examples:
        research_agent_deepagents -> ResearchAgentDeepAgents
        sentiment_analyzer -> SentimentAnalyzer
        pydantic-mcp -> PydanticMcp
    """
    # Replace hyphens with underscores, then split on underscores
    text = text.replace("-", "_")
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", str(text or ""))
    words = [w for w in normalized.split("_") if w]
    pascal_words = []

    for word in words:
        # Skip empty words
        if not word:
            continue
        # Preserve known compound words/frameworks
        if word.lower() in ["deepagents", "crewai", "openai", "pydantic"]:
            # Keep compound words capitalized properly
            if word.lower() == "deepagents":
                pascal_words.append("DeepAgents")
            elif word.lower() == "crewai":
                pascal_words.append("CrewAI")
            elif word.lower() == "openai":
                pascal_words.append("OpenAI")
            elif word.lower() == "pydantic":
                pascal_words.append("Pydantic")
            else:
                pascal_words.append(word.capitalize())
        else:
            pascal_words.append(word.capitalize())

    return "".join(pascal_words)


def to_snake_case(text: str) -> str:
    """Convert field names to snake_case to match generated DSPy signatures."""
    return str(text).strip().replace("-", "_").replace(" ", "_").lower()


def resolve_pipeline_class(module: Any, agent_name: str) -> Any:
    """
    Resolve generated pipeline class robustly across naming variants.

    Handles differences like:
    - CrewAIStackonePipeline vs CrewaiStackonePipeline
    - kebab/snake agent IDs
    """
    candidates = []
    candidates.append(f"{to_pascal_case(agent_name)}Pipeline")
    snake = to_snake_case(agent_name)
    candidates.append("".join(part.capitalize() for part in snake.split("_")) + "Pipeline")
    candidates.append(f"{agent_name.title().replace('_', '').replace('-', '')}Pipeline")

    seen = set()
    for name in candidates:
        if name in seen:
            continue
        seen.add(name)
        cls = getattr(module, name, None)
        if cls is not None:
            return cls

    # Fallback: find the most likely *Pipeline class by normalized class name.
    target_norm = re.sub(r"[^a-z0-9]", "", snake.lower()) + "pipeline"
    for name, obj in module.__dict__.items():
        if isinstance(obj, type) and name.endswith("Pipeline"):
            name_norm = re.sub(r"[^a-z0-9]", "", name.lower())
            if target_norm == name_norm or target_norm in name_norm:
                return obj

    # Final fallback: first pipeline-like class.
    for _, obj in module.__dict__.items():
        if isinstance(obj, type) and _.endswith("Pipeline"):
            return obj
    return None


class DSPyRunner:
    """Runner for DSPy-based agents."""

    def __init__(
        self, agent_name: str, project_name: str = None, project_root: Path = None
    ):
        self.agent_name = agent_name.lower()

        # Use provided project root or find it
        if project_root:
            self.project_root = project_root
        else:
            self.project_root = self._find_project_root()

        if project_name:
            self.system_name = project_name
        else:
            with open(self.project_root / ".super") as f:
                self.system_name = yaml.safe_load(f).get("project")

        # Calculate paths
        self.agent_path = (
            self.project_root / self.system_name / "agents" / self.agent_name
        )

        # Detect pipeline file (framework-specific or default)
        pipelines_dir = self.agent_path / "pipelines"
        self.pipeline_path = self._find_pipeline_file(pipelines_dir)

        self.optimized_path = (
            self.agent_path / "pipelines" / f"{self.agent_name}_optimized.json"
        )
        self.playbook_path = self._find_playbook_file(self.agent_path / "playbook")
        self._rag_helper = None
        self._rag_initialized = False
        self._rag_enabled = False
        self._memory = None
        self._memory_initialized = False
        self._memory_enabled = False

    def _find_project_root(self) -> Path:
        """Find project root by looking for .super file."""
        current_dir = Path.cwd()
        while current_dir != current_dir.parent:
            if (current_dir / ".super").exists():
                return current_dir
            current_dir = current_dir.parent
        raise FileNotFoundError("Could not find .super file")

    def _find_pipeline_file(self, pipelines_dir: Path) -> Path:
        """
        Find the pipeline file, checking for framework-specific versions.

        Checks in order:
        1. {agent_name}_pipeline.py (default DSPy)
        2. {agent_name}_deepagents_pipeline.py (DeepAgents framework)
        3. {agent_name}_crewai_pipeline.py (CrewAI framework)
        4. {agent_name}_microsoft_pipeline.py (Microsoft framework)
        5. {agent_name}_openai_pipeline.py (OpenAI framework)
        6. {agent_name}_claude_sdk_pipeline.py (Claude Agent SDK framework)

        Args:
            pipelines_dir: Directory containing pipeline files

        Returns:
            Path to the pipeline file

        Raises:
            FileNotFoundError: If no pipeline file is found
        """
        if not pipelines_dir.exists():
            raise FileNotFoundError(f"Pipelines directory not found: {pipelines_dir}")

        # Prefer default DSPy pipeline first.
        default_pipeline = pipelines_dir / f"{self.agent_name}_pipeline.py"
        if default_pipeline.exists():
            return default_pipeline

        # Fall back to framework-specific pipelines.
        framework_variants = [
            "deepagents",
            "crewai",
            "microsoft",
            "openai",
            "google_adk",
            "pydantic_ai",  # Pydantic AI framework
            "claude_sdk",  # Claude Agent SDK framework
        ]

        for framework in framework_variants:
            framework_pipeline = (
                pipelines_dir / f"{self.agent_name}_{framework}_pipeline.py"
            )
            if framework_pipeline.exists():
                return framework_pipeline

        # No pipeline found
        raise FileNotFoundError(
            f"No pipeline file found for agent '{self.agent_name}' in {pipelines_dir}"
        )

    def _find_playbook_file(self, playbook_dir: Path) -> Path:
        """Find playbook file with underscore/hyphen compatibility."""
        if not playbook_dir.exists():
            raise FileNotFoundError(f"Playbook directory not found: {playbook_dir}")

        candidates = [
            playbook_dir / f"{self.agent_name}_playbook.yaml",
            playbook_dir / f"{self.agent_name.replace('_', '-')}_playbook.yaml",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate

        discovered = sorted(playbook_dir.glob("*_playbook.yaml"))
        if discovered:
            return discovered[0]

        raise FileNotFoundError(
            f"No playbook file found for agent '{self.agent_name}' in {playbook_dir}"
        )

    def _load_playbook_data(self) -> Dict[str, Any]:
        """Load playbook and return full dict (or empty dict on failure)."""
        if not self.playbook_path.exists():
            return {}
        with open(self.playbook_path, "r") as f:
            return yaml.safe_load(f) or {}

    def _get_input_output_field_names(self, spec_data: Dict[str, Any]) -> tuple[str, list[str]]:
        """Resolve primary input and output field names from playbook spec."""
        input_field = "query"
        output_fields = ["response"]

        tasks = spec_data.get("tasks", [])
        if tasks and isinstance(tasks, list):
            first_task = tasks[0] or {}
            task_inputs = first_task.get("inputs", [])
            task_outputs = first_task.get("outputs", [])
            if task_inputs and isinstance(task_inputs, list):
                input_field = to_snake_case((task_inputs[0] or {}).get("name", input_field))
            if task_outputs and isinstance(task_outputs, list):
                names = [f.get("name") for f in task_outputs if isinstance(f, dict)]
                output_fields = [to_snake_case(name) for name in names if name] or output_fields
                return input_field, output_fields

        # Fallback to spec-level input_fields/output_fields
        spec_inputs = spec_data.get("input_fields", [])
        if spec_inputs and isinstance(spec_inputs, list):
            first_input = spec_inputs[0] if isinstance(spec_inputs[0], dict) else {}
            input_field = to_snake_case(first_input.get("name", input_field))

        # Fallback to spec-level output_fields if task outputs missing
        spec_outputs = spec_data.get("output_fields", [])
        if spec_outputs and isinstance(spec_outputs, list):
            names = [f.get("name") for f in spec_outputs if isinstance(f, dict)]
            output_fields = [to_snake_case(name) for name in names if name] or output_fields

        return input_field, output_fields

    def _is_rag_enabled_in_spec(self, spec_data: Dict[str, Any]) -> bool:
        """Check whether RAG/retrieval is enabled in playbook spec."""
        rag_cfg = spec_data.get("rag", {}) if isinstance(spec_data, dict) else {}
        retrieval_cfg = (
            spec_data.get("retrieval", {}) if isinstance(spec_data, dict) else {}
        )

        rag_on = isinstance(rag_cfg, dict) and bool(rag_cfg.get("enabled", False))
        retrieval_on = isinstance(retrieval_cfg, dict) and bool(
            retrieval_cfg.get("enabled", False)
        )
        return rag_on or retrieval_on

    def _ensure_rag_initialized(self, spec_data: Dict[str, Any]) -> bool:
        """
        Initialize shared RAG helper once per runner instance.
        Reuses existing SuperOptiX RAG mixin + vector DB integrations.
        """
        if self._rag_initialized:
            return self._rag_enabled

        self._rag_initialized = True
        self._rag_enabled = False

        if not self._is_rag_enabled_in_spec(spec_data):
            return False
        if not RAG_MIXIN_AVAILABLE or RAGMixin is None:
            console.print(
                "[yellow]⚠️ RAG configured but RAG mixin is unavailable. Continuing without retrieval.[/]"
            )
            return False

        class _RunnerRAGHelper(RAGMixin):
            pass

        try:
            helper = _RunnerRAGHelper()
            enabled = bool(helper.setup_rag(spec_data))
            self._rag_helper = helper if enabled else None
            self._rag_enabled = enabled
            if enabled:
                console.print("[cyan]🔍 RAG retrieval enabled (runner-managed).[/]")
            else:
                console.print(
                    "[yellow]⚠️ RAG configured but initialization failed. Continuing without retrieval.[/]"
                )
            return enabled
        except Exception as e:
            console.print(
                f"[yellow]⚠️ RAG setup error ({e}). Continuing without retrieval.[/]"
            )
            self._rag_helper = None
            self._rag_enabled = False
            return False

    async def _retrieve_context_text(self, spec_data: Dict[str, Any], query: str) -> str:
        """Retrieve context using existing RAG mixin path and return merged text."""
        if not query or not query.strip():
            return ""
        if not self._ensure_rag_initialized(spec_data):
            return ""
        if not self._rag_helper:
            return ""

        try:
            rag_cfg = spec_data.get("rag", {}) if isinstance(spec_data, dict) else {}
            retrieval_cfg = (
                spec_data.get("retrieval", {}) if isinstance(spec_data, dict) else {}
            )
            cfg = rag_cfg if isinstance(rag_cfg, dict) and rag_cfg else retrieval_cfg
            top_k = cfg.get("top_k") if isinstance(cfg, dict) else None
            retrieved_docs = await self._rag_helper.retrieve_context(query, top_k=top_k)
            if not retrieved_docs:
                return ""
            return "\n\n".join(str(doc) for doc in retrieved_docs if doc)
        except Exception as e:
            console.print(
                f"[yellow]⚠️ RAG retrieval failed ({e}). Continuing without retrieval.[/]"
            )
            return ""

    def _augment_query_with_context(self, query: str, context_text: str) -> str:
        """Compose query with retrieved context for DSPy input."""
        if not context_text:
            return query
        return f"{query}\n\nRelevant Context:\n{context_text}"

    def _is_memory_enabled_in_spec(self, spec_data: Dict[str, Any]) -> bool:
        """Check whether memory is enabled in playbook spec."""
        memory_cfg = spec_data.get("memory", {}) if isinstance(spec_data, dict) else {}
        return isinstance(memory_cfg, dict) and bool(memory_cfg.get("enabled", False))

    def _build_memory_backend(self, memory_cfg: Dict[str, Any]):
        """Build memory backend from config, with safe fallbacks."""
        backend_cfg = memory_cfg.get("backend", {})
        backend_type = "sqlite"
        backend_config = {}

        if isinstance(backend_cfg, str):
            backend_type = backend_cfg.strip().lower()
        elif isinstance(backend_cfg, dict):
            backend_type = str(backend_cfg.get("type", "sqlite")).strip().lower()
            if isinstance(backend_cfg.get("config"), dict):
                backend_config = backend_cfg.get("config", {})
            else:
                backend_config = {
                    key: value
                    for key, value in backend_cfg.items()
                    if key not in {"type", "config"}
                }

        if backend_type == "file" and FileBackend is not None:
            storage_path = backend_config.get("storage_path") or backend_config.get(
                "path"
            )
            return FileBackend(storage_path=storage_path) if storage_path else FileBackend()

        if backend_type == "redis" and RedisBackend is not None:
            return RedisBackend(
                host=backend_config.get("host", "localhost"),
                port=int(backend_config.get("port", 6379)),
                db=int(backend_config.get("db", 0)),
                password=backend_config.get("password"),
                prefix=backend_config.get("prefix", "superoptix:"),
            )

        if SQLiteBackend is not None:
            db_path = backend_config.get("db_path") or backend_config.get("path")
            return SQLiteBackend(db_path=db_path) if db_path else SQLiteBackend()
        return None

    def _ensure_memory_initialized(self, spec_data: Dict[str, Any]) -> bool:
        """Initialize shared memory helper once per runner instance."""
        if self._memory_initialized:
            return self._memory_enabled

        self._memory_initialized = True
        self._memory_enabled = False

        if not self._is_memory_enabled_in_spec(spec_data):
            return False

        if not MEMORY_AVAILABLE or AgentMemory is None:
            console.print(
                "[yellow]⚠️ Memory configured but memory modules are unavailable. Continuing without memory.[/]"
            )
            return False

        memory_cfg = spec_data.get("memory", {})
        if not isinstance(memory_cfg, dict):
            return False

        try:
            backend = self._build_memory_backend(memory_cfg)
            short_cfg = (
                memory_cfg.get("short_term", {})
                if isinstance(memory_cfg.get("short_term", {}), dict)
                else {}
            )
            long_cfg = (
                memory_cfg.get("long_term", {})
                if isinstance(memory_cfg.get("long_term", {}), dict)
                else {}
            )
            context_cfg = (
                memory_cfg.get("context_manager", {})
                if isinstance(memory_cfg.get("context_manager", {}), dict)
                else {}
            )

            agent_id = str(
                memory_cfg.get("agent_id")
                or f"{self.system_name}:{self.agent_name}"
            ).strip()
            short_term_capacity = int(short_cfg.get("capacity", 100))
            enable_embeddings = bool(long_cfg.get("enable_embeddings", False))
            max_context_tokens = int(
                context_cfg.get("max_context_length", memory_cfg.get("max_context_tokens", 4096))
            )

            self._memory = AgentMemory(
                agent_id=agent_id,
                backend=backend,
                short_term_capacity=short_term_capacity,
                enable_embeddings=enable_embeddings,
                enable_context_optimization=False,
                max_context_tokens=max_context_tokens,
            )
            self._memory_enabled = True
            console.print("[cyan]🧠 Memory enabled (runner-managed).[/]")
            return True
        except Exception as e:
            console.print(
                f"[yellow]⚠️ Memory setup error ({e}). Continuing without memory.[/]"
            )
            self._memory = None
            self._memory_enabled = False
            return False

    def _start_memory_interaction(self, query: str) -> str | None:
        """Start a memory episode and log incoming user query."""
        if not self._memory_enabled or self._memory is None:
            return None
        try:
            episode_id = self._memory.start_interaction(
                {"query": query, "agent_name": self.agent_name}
            )
            if episode_id:
                self._memory.add_interaction_event(
                    event_type="user_query",
                    description="User submitted query",
                    data={"query": query},
                )
            return episode_id
        except Exception:
            return None

    def _retrieve_memory_context_text(self, spec_data: Dict[str, Any], query: str) -> str:
        """Recall relevant memory snippets and format as context text."""
        if not query or not query.strip():
            return ""
        if not self._ensure_memory_initialized(spec_data):
            return ""
        if self._memory is None:
            return ""

        try:
            memory_cfg = spec_data.get("memory", {})
            short_cfg = (
                memory_cfg.get("short_term", {})
                if isinstance(memory_cfg.get("short_term", {}), dict)
                else {}
            )
            long_cfg = (
                memory_cfg.get("long_term", {})
                if isinstance(memory_cfg.get("long_term", {}), dict)
                else {}
            )
            search_cfg = (
                long_cfg.get("search", {})
                if isinstance(long_cfg.get("search", {}), dict)
                else {}
            )
            recall_limit = int(
                search_cfg.get("default_limit", memory_cfg.get("recall_limit", 3))
            )
            recall_limit = min(10, max(1, recall_limit))
            min_similarity = float(search_cfg.get("min_similarity_threshold", 0.3))

            recalled = self._memory.recall(
                query=query,
                memory_type="all",
                limit=recall_limit,
                min_similarity=min_similarity,
            )
            conversation_window = int(short_cfg.get("window_size", 3))
            conversation_window = min(10, max(1, conversation_window))
            conversation = self._memory.get_conversation_context(
                last_n=conversation_window
            )
            recent_messages = conversation.get("recent_conversation", [])

            lines = []
            if recent_messages:
                lines.append("Recent Conversation:")
                for message in recent_messages:
                    role = str(message.get("role", "unknown")).strip()
                    content = str(message.get("content", "")).strip()
                    if content:
                        lines.append(f"- [{role}] {content[:240]}")

            if recalled:
                lines.append("Recalled Memory:")
                for item in recalled:
                    memory_type = str(item.get("type", "memory")).strip()
                    content = str(item.get("content", "")).strip()
                    if content:
                        lines.append(f"- [{memory_type}] {content[:320]}")

            return "\n".join(lines).strip()
        except Exception as e:
            console.print(
                f"[yellow]⚠️ Memory recall failed ({e}). Continuing without memory context.[/]"
            )
            return ""

    def _persist_memory_interaction(
        self, spec_data: Dict[str, Any], query: str, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Persist query/response to memory and return a small stats payload."""
        if not self._memory_enabled or self._memory is None:
            return {}

        try:
            memory_cfg = spec_data.get("memory", {})
            short_cfg = (
                memory_cfg.get("short_term", {})
                if isinstance(memory_cfg.get("short_term", {}), dict)
                else {}
            )
            long_cfg = (
                memory_cfg.get("long_term", {})
                if isinstance(memory_cfg.get("long_term", {}), dict)
                else {}
            )

            user_fields = [
                key
                for key in result.keys()
                if not key.startswith("_") and key not in {"is_valid"}
            ]
            response_text = "\n".join(
                f"{field}: {result.get(field)}" for field in user_fields
            ).strip()
            if not response_text:
                response_text = str(result)

            self._memory.short_term.add_to_conversation("user", query)
            self._memory.short_term.add_to_conversation("assistant", response_text)

            ttl_value = short_cfg.get("default_ttl")
            ttl = int(ttl_value) if isinstance(ttl_value, int) and ttl_value > 0 else None
            interaction_text = f"Q: {query}\nA: {response_text}"
            self._memory.remember(
                content=interaction_text,
                memory_type="short",
                importance=0.7,
                ttl=ttl,
            )

            if bool(long_cfg.get("enabled", True)):
                self._memory.remember(
                    content=interaction_text,
                    memory_type="long",
                    category="interactions",
                    importance=0.6,
                    tags=["dspy", self.agent_name],
                )

            summary = self._memory.get_memory_summary()
            short_stats = summary.get("short_term_memory", {})
            long_stats = summary.get("long_term_memory", {})
            episodic_stats = summary.get("episodic_memory", {})
            return {
                "interactions": summary.get("interaction_count", 0),
                "short_term_items": short_stats.get("size", 0),
                "long_term_items": long_stats.get("total_items", 0),
                "active_episodes": episodic_stats.get("active_episodes", 0),
            }
        except Exception as e:
            console.print(
                f"[yellow]⚠️ Memory persistence failed ({e}). Continuing.[/]"
            )
            return {}

    def _end_memory_interaction(self, success: bool, error: str | None = None) -> None:
        """End the active memory episode if one exists."""
        if not self._memory_enabled or self._memory is None:
            return
        try:
            outcome = {"success": bool(success)}
            if error:
                outcome["error"] = str(error)
            self._memory.end_interaction(outcome)
        except Exception:
            return

    def _resolve_dspy_lm_params(
        self,
        spec_data: Dict[str, Any],
        allow_local_ollama: bool = False,
        purpose: str = "task",
        model_override: str | None = None,
        provider_override: str | None = None,
        runtime_mode: str = "auto",
    ) -> Dict[str, Any]:
        """Resolve playbook/provider/env into simple DSPy LM constructor params."""
        lm_config = (
            spec_data.get("model")
            or spec_data.get("language_model")
            or spec_data.get("llm")
            or {}
        )

        model = str(lm_config.get("model", "")).strip()
        has_provider_in_playbook = "provider" in lm_config
        provider = str(lm_config.get("provider", "ollama")).strip().lower()
        temperature = lm_config.get("temperature", 0.7)
        max_tokens = lm_config.get("max_tokens", 2048)
        reasoning_cfg = (
            spec_data.get("reasoning", {})
            if isinstance(spec_data.get("reasoning", {}), dict)
            else {}
        )
        # module_params from spec.dspy are mapped into spec.reasoning at compile time.
        # Honor them here so these controls are not no-ops.
        if "temperature" in reasoning_cfg and reasoning_cfg.get("temperature") is not None:
            temperature = reasoning_cfg.get("temperature")
        if "max_tokens" in reasoning_cfg and reasoning_cfg.get("max_tokens") is not None:
            max_tokens = reasoning_cfg.get("max_tokens")

        local_task_default = os.getenv("SUPEROPTIX_DSPY_TASK_MODEL", "llama3.1:8b")
        local_teacher_default = os.getenv(
            "SUPEROPTIX_DSPY_TEACHER_MODEL", "llama3.1:8b"
        )
        cloud_task_default = os.getenv(
            "SUPEROPTIX_DSPY_CLOUD_TASK_MODEL", "gemini-2.5-flash-lite"
        )
        cloud_teacher_default = os.getenv(
            "SUPEROPTIX_DSPY_CLOUD_TEACHER_MODEL", "gemini-2.5-flash"
        )

        if provider_override:
            provider = str(provider_override).strip().lower()

        if model_override:
            model = str(model_override).strip()
            if model.startswith("ollama_chat/") or model.startswith("ollama/"):
                provider = "ollama"
            elif model.startswith("gemini/") or model.startswith("models/"):
                provider = "google-genai"

        runtime_mode = (runtime_mode or "auto").lower()

        if runtime_mode == "local" and not provider:
            provider = "ollama"

        # If user explicitly requests cloud but playbook had no provider, switch to cloud default provider/model.
        if (
            runtime_mode == "cloud"
            and not provider_override
            and not has_provider_in_playbook
            and provider in {"", "ollama", "local"}
        ):
            provider = "google-genai"
            if not model:
                model = (
                    cloud_teacher_default
                    if purpose == "teacher"
                    else cloud_task_default
                )

        # Ollama-first default for auto/local when model is missing.
        if not model:
            if provider in {"ollama", "local", ""}:
                provider = "ollama"
                model = (
                    local_teacher_default
                    if purpose == "teacher"
                    else local_task_default
                )
            else:
                model = (
                    cloud_teacher_default
                    if purpose == "teacher"
                    else cloud_task_default
                )

        if runtime_mode == "cloud" and provider in {"ollama", "local"}:
            raise ValueError(
                "Cloud mode cannot use local provider 'ollama'. Use --local or choose a cloud provider."
            )

        if provider in {"google", "google-genai"}:
            provider = "google-genai"

        if provider == "ollama" and not allow_local_ollama:
            raise ValueError(
                "Local Ollama provider requires local mode compilation. Recompile with --local (or --local-ollama)."
            )

        if provider == "ollama":
            model_name = model if model.startswith("ollama_chat/") else f"ollama_chat/{model}"
            return {
                "model_name": model_name,
                "api_key": "",
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

        if provider == "google-genai":
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError(
                    "Missing GEMINI_API_KEY/GOOGLE_API_KEY. Set one before running this cloud pipeline."
                )
            model_str = str(model).strip()
            if model_str.startswith("gemini/"):
                model_name = model_str
            elif model_str.startswith("models/"):
                model_name = f"gemini/{model_str.split('/', 1)[1]}"
            elif "/" in model_str:
                model_name = f"gemini/{model_str.split('/')[-1]}"
            else:
                model_name = f"gemini/{model_str}"
            return {
                "model_name": model_name,
                "api_key": api_key,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

        api_key_env_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "azure": "AZURE_OPENAI_API_KEY",
            "mistral": "MISTRAL_API_KEY",
            "cohere": "COHERE_API_KEY",
            "groq": "GROQ_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
        }
        api_key_env = api_key_env_map.get(provider)
        api_key = os.getenv(api_key_env) if api_key_env else os.getenv("OPENAI_API_KEY", "")
        if api_key_env and not api_key:
            raise ValueError(f"Missing {api_key_env}. Set it before running this cloud pipeline.")

        model_name = model if "/" in model else f"{provider}/{model}"
        return {
            "model_name": model_name,
            "api_key": api_key,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

    def _configure_dspy_lm_from_playbook(
        self,
        spec_data: Dict[str, Any],
        allow_local_ollama: bool = False,
        model_override: str | None = None,
        provider_override: str | None = None,
        runtime_mode: str = "auto",
    ) -> dspy.LM:
        """Configure and return a DSPy LM using playbook model settings."""
        lm_params = self._resolve_dspy_lm_params(
            spec_data,
            allow_local_ollama=allow_local_ollama,
            model_override=model_override,
            provider_override=provider_override,
            runtime_mode=runtime_mode,
        )
        lm = dspy.LM(
            model=lm_params["model_name"],
            api_key=lm_params["api_key"],
            temperature=lm_params["temperature"],
            max_tokens=lm_params["max_tokens"],
        )
        dspy.configure(lm=lm)
        return lm

    def _prediction_to_result(
        self, prediction: Any, output_fields: list[str]
    ) -> Dict[str, Any]:
        """Convert a DSPy prediction object into a stable dict."""
        result: Dict[str, Any] = {}

        for field in output_fields:
            value = None
            if hasattr(prediction, field):
                value = getattr(prediction, field)
            elif isinstance(prediction, dict):
                value = prediction.get(field)
            if value is not None:
                result[field] = value

        if not result:
            # Fallback for unknown output schema.
            result["response"] = str(prediction)

        return result

    def _resolve_dspy_adapter_config(
        self, spec_data: Dict[str, Any], module: Any | None = None
    ) -> Dict[str, Any]:
        """Resolve adapter config from global + per-module + runtime overrides."""
        runtime_cfg: Dict[str, Any] = {}
        runtime_adapter_cfg: Dict[str, Any] = {}
        active_module_name: str = ""

        if module is not None and hasattr(module, "get_dspy_runtime_config") and callable(
            module.get_dspy_runtime_config
        ):
            try:
                runtime_cfg = module.get_dspy_runtime_config() or {}
                if isinstance(runtime_cfg, dict):
                    runtime_adapter_cfg = runtime_cfg.get("adapter", {}) or {}
                    active_module_name = str(runtime_cfg.get("module", "")).strip().lower()
            except Exception:
                runtime_cfg = {}
                runtime_adapter_cfg = {}

        dspy_cfg = spec_data.get("dspy", {}) if isinstance(spec_data, dict) else {}
        base_adapter_cfg: Dict[str, Any] = {}
        module_adapter_cfg: Dict[str, Any] = {}
        default_module_name: str = ""
        if isinstance(dspy_cfg, dict):
            base_adapter_cfg = dspy_cfg.get("adapter", {}) or {}
            default_module_name = str(dspy_cfg.get("module", "")).strip().lower()

            modules_cfg = dspy_cfg.get("modules", [])
            if isinstance(modules_cfg, list):
                target_module = active_module_name or default_module_name
                for item in modules_cfg:
                    if not isinstance(item, dict):
                        continue
                    name = str(item.get("name", "")).strip().lower()
                    if name == target_module and isinstance(item.get("adapter"), dict):
                        module_adapter_cfg = item.get("adapter", {}) or {}
                        break

        adapter_cfg: Dict[str, Any] = {}
        if isinstance(base_adapter_cfg, dict):
            adapter_cfg.update(base_adapter_cfg)
        if isinstance(module_adapter_cfg, dict):
            adapter_cfg.update(module_adapter_cfg)
        if isinstance(runtime_adapter_cfg, dict):
            adapter_cfg.update(runtime_adapter_cfg)

        # Keep active module hint for auto-selection heuristics/diagnostics.
        if active_module_name:
            adapter_cfg["_active_module"] = active_module_name
        elif default_module_name:
            adapter_cfg["_active_module"] = default_module_name

        if not isinstance(adapter_cfg, dict):
            return {}
        return adapter_cfg

    def _should_prefer_structured_adapter(self, spec_data: Dict[str, Any]) -> bool:
        """Heuristic: prefer structured adapters when multiple/typed outputs are expected."""
        output_fields = spec_data.get("output_fields")
        if isinstance(output_fields, list) and len(output_fields) > 1:
            return True

        tasks = spec_data.get("tasks")
        if isinstance(tasks, list) and tasks:
            first_task = tasks[0] if isinstance(tasks[0], dict) else {}
            task_outputs = first_task.get("outputs")
            if isinstance(task_outputs, list) and len(task_outputs) > 1:
                return True

        return False

    def _choose_adapter_type(
        self, adapter_cfg: Dict[str, Any], spec_data: Dict[str, Any]
    ) -> str:
        """Choose adapter type based on explicit type or auto mode heuristics."""
        mode = str(adapter_cfg.get("mode", "auto")).strip().lower()
        manual_type = str(adapter_cfg.get("type", "chat")).strip().lower()

        if mode != "auto":
            return manual_type

        dspy_cfg = spec_data.get("dspy", {}) if isinstance(spec_data, dict) else {}
        module_name = str(adapter_cfg.get("_active_module", "")).strip().lower()
        if not module_name and isinstance(dspy_cfg, dict):
            module_name = str(dspy_cfg.get("module", "")).strip().lower()

        tools_cfg = dspy_cfg.get("tools", {}) if isinstance(dspy_cfg, dict) else {}
        tools_mode = str(
            tools_cfg.get("mode", "none") if isinstance(tools_cfg, dict) else "none"
        ).strip().lower()

        # ReAct and tool-heavy flows are usually chat-centric.
        if module_name == "react" or tools_mode in {
            "builtin",
            "mcp",
            "stackone",
            "stackone_discovery",
        }:
            return "chat"

        if self._should_prefer_structured_adapter(spec_data):
            return "json"

        return "chat"

    def _build_dspy_adapter(
        self,
        adapter_type: str,
        native_fc: bool,
        strict: bool,
        retry_on_parse_error: int,
    ) -> Any | None:
        """Construct a DSPy adapter instance with best-effort optional args."""
        adapter_map = {
            "chat": dspy.ChatAdapter,
            "json": dspy.JSONAdapter,
            "xml": dspy.XMLAdapter,
            "twostep": dspy.TwoStepAdapter,
        }
        adapter_cls = adapter_map.get(adapter_type)
        if adapter_cls is None:
            return None

        kwargs = {}
        init_params = inspect.signature(adapter_cls.__init__).parameters
        if "use_native_function_calling" in init_params:
            kwargs["use_native_function_calling"] = native_fc
        if "strict" in init_params:
            kwargs["strict"] = strict
        if "retry_on_parse_error" in init_params:
            kwargs["retry_on_parse_error"] = retry_on_parse_error
        elif "max_retries" in init_params:
            kwargs["max_retries"] = retry_on_parse_error

        try:
            return adapter_cls(**kwargs)
        except Exception:
            return None

    def _configure_dspy_adapter(
        self, spec_data: Dict[str, Any], module: Any | None = None
    ) -> None:
        """Configure DSPy adapter centrally so generated pipeline stays minimal."""
        adapter_cfg = self._resolve_dspy_adapter_config(spec_data, module)
        if not adapter_cfg:
            return

        adapter_type = self._choose_adapter_type(adapter_cfg, spec_data)
        fallback_type = str(adapter_cfg.get("fallback_adapter", "chat")).strip().lower()
        native_fc = bool(adapter_cfg.get("native_function_calling", False))
        strict = bool(adapter_cfg.get("strict", False))
        try:
            retry_on_parse_error = int(adapter_cfg.get("retry_on_parse_error", 1) or 0)
        except (TypeError, ValueError):
            retry_on_parse_error = 1
        retry_on_parse_error = max(0, retry_on_parse_error)

        adapter = self._build_dspy_adapter(
            adapter_type=adapter_type,
            native_fc=native_fc,
            strict=strict,
            retry_on_parse_error=retry_on_parse_error,
        )
        chosen_type = adapter_type

        if adapter is None and fallback_type != adapter_type:
            adapter = self._build_dspy_adapter(
                adapter_type=fallback_type,
                native_fc=native_fc,
                strict=strict,
                retry_on_parse_error=retry_on_parse_error,
            )
            chosen_type = fallback_type

        if adapter is None:
            return

        try:
            dspy.configure(lm=dspy.settings.lm, adapter=adapter)
            mode = str(adapter_cfg.get("mode", "auto")).strip().lower()
            console.print(
                f"[dim]DSPy adapter: {chosen_type} (mode={mode}, strict={strict}, retries={retry_on_parse_error})[/]"
            )
        except Exception:
            # Non-fatal; keep default adapter path.
            return

    def _tool_trace_enabled(self, spec_data: Dict[str, Any]) -> bool:
        """Whether transient live tool traces are enabled for this run."""
        env = str(os.getenv("SUPEROPTIX_DSPY_THINKING_LOGS", "")).strip().lower()
        if env in {"1", "true", "yes", "on"}:
            return True

        dspy_cfg = spec_data.get("dspy", {}) if isinstance(spec_data, dict) else {}
        tools_cfg = dspy_cfg.get("tools", {}) if isinstance(dspy_cfg, dict) else {}
        trace_cfg = tools_cfg.get("trace", {}) if isinstance(tools_cfg, dict) else {}
        if isinstance(trace_cfg, dict):
            return bool(trace_cfg.get("enabled", False))
        return False

    def _render_tool_trace_panel(self, events: list[Dict[str, Any]]) -> Panel:
        """Render transient live tool trace panel."""
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Time", style="dim", width=8)
        table.add_column("Stage", style="magenta", width=14)
        table.add_column("Detail", style="white")

        for event in events[-10:]:
            detail = str(event.get("detail", ""))
            if len(detail) > 120:
                detail = detail[:117] + "..."
            table.add_row(
                str(event.get("time", "")),
                str(event.get("stage", "")),
                detail,
            )

        if not events:
            table.add_row(
                datetime.now().strftime("%H:%M:%S"),
                "trace",
                "Waiting for tool activity...",
            )

        return Panel(
            table,
            title="DSPy Thinking Logs",
            subtitle="Transient tool trace (auto-clears)",
            border_style="cyan",
        )

    def _run_program_with_timeout(self, program, kwargs: Dict[str, Any]):
        """Run DSPy program with optional hard timeout to avoid long hangs."""
        try:
            timeout_sec = float(os.getenv("SUPEROPTIX_DSPY_PROGRAM_TIMEOUT_SEC", "120"))
        except (TypeError, ValueError):
            timeout_sec = 120.0

        if timeout_sec <= 0:
            return program(**kwargs)

        state: dict[str, Any] = {"done": False, "result": None, "error": None}

        def _target():
            try:
                state["result"] = program(**kwargs)
            except Exception as exc:
                state["error"] = exc
            finally:
                state["done"] = True

        thread = threading.Thread(target=_target, daemon=True)
        thread.start()
        thread.join(timeout=timeout_sec)
        if not state["done"]:
            raise TimeoutError(
                f"DSPy program timed out after {int(timeout_sec)}s. "
                "Tune model/tools or increase SUPEROPTIX_DSPY_PROGRAM_TIMEOUT_SEC."
            )
        if state["error"] is not None:
            raise state["error"]
        return state["result"]

    async def optimize(
        self,
        strategy: str = "bootstrap",
        force: bool = False,
        runtime_mode: str = "auto",
        provider_override: str | None = None,
        model_override: str | None = None,
    ) -> Dict[str, Any]:
        """Optimize the agent pipeline using DSPy optimization techniques."""
        optimization_result = {
            "started_at": str(time.time()),
            "success": False,
            "training_examples": 0,
            "score": None,
            "usage_stats": {},
            "error": None,
        }

        try:
            console.print("\n[yellow]🔍 Checking for existing optimized pipeline...[/]")

            # Check if optimized version already exists
            if self.optimized_path.exists() and not force:
                console.print(
                    f"\n[yellow]⚠️ Optimized pipeline already exists at {self.optimized_path}[/]"
                )
                console.print(
                    "[yellow]Use --force to re-optimize or run with existing optimization[/]"
                )
                optimization_result["success"] = True
                optimization_result["note"] = "Already optimized"
                return optimization_result

            console.print(
                Panel(
                    "🔧 DSPy Optimization in progress\n\n• This step fine-tunes prompts and may take several minutes.\n• API calls can incur compute cost – monitor your provider dashboard.\n• You can abort anytime with CTRL+C; your base pipeline remains intact.",
                    title="🚀 Optimization Notice",
                    border_style="bright_magenta",
                )
            )
            console.print(
                f"\n[yellow]🚀 Starting optimization using '[bold]{strategy}[/]' strategy...[/]"
            )

            # Import and execute the pipeline module
            import importlib.util
            import sys

            spec = importlib.util.spec_from_file_location(
                f"{self.agent_name}_pipeline", self.pipeline_path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            # Native minimal DSPy optimization path (build_program + GEPA in runner)
            if hasattr(module, "build_program") and callable(module.build_program):
                playbook = self._load_playbook_data()
                spec_data = playbook.get("spec", playbook)
                input_field, output_fields = self._get_input_output_field_names(spec_data)
                optimization_cfg = {}
                gepa_cfg = {}
                playbook_gepa_cfg = (
                    spec_data.get("optimization", {})
                    .get("optimizer", {})
                    .get("params", {})
                    if isinstance(spec_data.get("optimization", {}), dict)
                    else {}
                )
                if isinstance(playbook_gepa_cfg, dict):
                    gepa_cfg.update(playbook_gepa_cfg)
                if hasattr(module, "get_optimization_config") and callable(
                    module.get_optimization_config
                ):
                    optimization_cfg = module.get_optimization_config() or {}
                    module_gepa_cfg = optimization_cfg.get("gepa", {}) or {}
                    if isinstance(module_gepa_cfg, dict):
                        # Module snapshot takes precedence for visible pipeline-config overrides.
                        gepa_cfg.update(module_gepa_cfg)

                scenarios = []
                if "feature_specifications" in spec_data and spec_data[
                    "feature_specifications"
                ].get("scenarios"):
                    scenarios = spec_data["feature_specifications"]["scenarios"]
                elif "scenarios" in spec_data:
                    scenarios = spec_data["scenarios"]

                if not scenarios:
                    optimization_result["error"] = (
                        "No scenarios found in playbook for optimization"
                    )
                    optimization_result["completed_at"] = str(time.time())
                    return optimization_result

                allow_local_ollama = bool(
                    getattr(module, "ALLOW_LOCAL_OLLAMA", False)
                )
                compiled_runtime_mode = str(
                    getattr(module, "RUNTIME_MODE", "auto") or "auto"
                ).lower()
                effective_runtime_mode = (runtime_mode or "auto").lower()
                if effective_runtime_mode == "auto":
                    effective_runtime_mode = compiled_runtime_mode
                effective_provider_override = provider_override or getattr(
                    module, "PROVIDER_OVERRIDE", None
                )
                effective_model_override = model_override or getattr(
                    module, "MODEL_OVERRIDE", None
                )
                task_params = self._resolve_dspy_lm_params(
                    spec_data,
                    allow_local_ollama=allow_local_ollama,
                    purpose="task",
                    model_override=effective_model_override
                    or gepa_cfg.get("task_model"),
                    provider_override=effective_provider_override,
                    runtime_mode=effective_runtime_mode,
                )

                # Configure task LM (student)
                if hasattr(module, "setup_lm") and callable(module.setup_lm):
                    module.setup_lm(**task_params)
                    self._configure_dspy_adapter(spec_data, module)
                else:
                    self._configure_dspy_lm_from_playbook(
                        spec_data,
                        allow_local_ollama=allow_local_ollama,
                        model_override=effective_model_override
                        or gepa_cfg.get("task_model"),
                        provider_override=effective_provider_override,
                        runtime_mode=effective_runtime_mode,
                    )
                    self._configure_dspy_adapter(spec_data, module)

                program = module.build_program()

                # Build DSPy examples from scenarios.
                examples = []
                for sc in scenarios:
                    if not isinstance(sc, dict):
                        continue
                    inp = sc.get("input", {}) or {}
                    if self._is_rag_enabled_in_spec(spec_data):
                        seed_query = str(inp.get(input_field, "")).strip()
                        if seed_query:
                            context_text = await self._retrieve_context_text(
                                spec_data, seed_query
                            )
                            if context_text:
                                inp = dict(inp)
                                inp[input_field] = self._augment_query_with_context(
                                    seed_query, context_text
                                )
                    expected = sc.get("expected_output", {}) or {}
                    merged = {**inp, **expected}
                    ex = dspy.Example(**merged).with_inputs(input_field)
                    examples.append(ex)

                if not examples:
                    optimization_result["error"] = (
                        "No valid training examples from scenarios"
                    )
                    optimization_result["completed_at"] = str(time.time())
                    return optimization_result

                # GEPA teacher/reflection LM defaults:
                # - Cloud: gemini-2.5-flash
                # - Local ollama: same task model unless user overrides via env
                if task_params["model_name"].startswith("ollama_chat/"):
                    teacher_params = dict(task_params)
                    teacher_model_override = (
                        os.getenv("SUPEROPTIX_DSPY_TEACHER_MODEL")
                        or gepa_cfg.get("reflection_lm")
                        or gepa_cfg.get("teacher_model")
                    )
                    if teacher_model_override:
                        teacher_params["model_name"] = (
                            teacher_model_override
                            if teacher_model_override.startswith("ollama_chat/")
                            else f"ollama_chat/{teacher_model_override}"
                        )
                else:
                    teacher_params = self._resolve_dspy_lm_params(
                        spec_data,
                        allow_local_ollama=allow_local_ollama,
                        purpose="teacher",
                        model_override=(
                            gepa_cfg.get("reflection_lm")
                            or gepa_cfg.get("teacher_model")
                        ),
                        provider_override=effective_provider_override,
                        runtime_mode=effective_runtime_mode,
                    )

                reflection_lm = dspy.LM(
                    model=teacher_params["model_name"],
                    api_key=teacher_params["api_key"],
                    temperature=1.0,
                    max_tokens=32000,
                )

                assertion_metric_weight = 0.3
                try:
                    if hasattr(module, "DSPY_ASSERTIONS_CONFIG"):
                        cfg = getattr(module, "DSPY_ASSERTIONS_CONFIG", {}) or {}
                        assertion_metric_weight = float(
                            cfg.get("metric_weight", assertion_metric_weight)
                        )
                except Exception:
                    assertion_metric_weight = 0.3
                assertion_metric_weight = min(1.0, max(0.0, assertion_metric_weight))
                metric_stats = {
                    "count": 0,
                    "quality_sum": 0.0,
                    "assertion_sum": 0.0,
                    "blended_sum": 0.0,
                }

                # Generic float metric for GEPA.
                def gepa_metric(gold, pred, trace=None, pred_name=None, pred_trace=None):
                    try:
                        scores = []
                        for field in output_fields:
                            g = str(getattr(gold, field, "")).strip().lower()
                            p = str(getattr(pred, field, "")).strip().lower()
                            if not g:
                                continue
                            if g in p or p in g:
                                scores.append(1.0)
                            else:
                                g_tokens = set(g.split())
                                p_tokens = set(p.split())
                                overlap = (
                                    len(g_tokens & p_tokens) / len(g_tokens)
                                    if g_tokens
                                    else 0.0
                                )
                                scores.append(float(overlap))
                        quality_score = float(sum(scores) / len(scores)) if scores else 0.5

                        assertion_score = 1.0
                        if hasattr(module, "validate_prediction_result") and callable(
                            module.validate_prediction_result
                        ):
                            pred_result = self._prediction_to_result(pred, output_fields)
                            if hasattr(module, "postprocess_prediction") and callable(
                                module.postprocess_prediction
                            ):
                                pred_result = module.postprocess_prediction(
                                    pred, pred_result, output_fields
                                )
                            payload = module.validate_prediction_result(pred_result) or {}
                            if isinstance(payload, dict):
                                assertion_score = float(
                                    payload.get(
                                        "assertion_score",
                                        1.0
                                        if payload.get("assertions_passed", True)
                                        else 0.0,
                                    )
                                )
                        assertion_score = min(1.0, max(0.0, assertion_score))

                        # Blend quality and validity so GEPA optimizes for both.
                        blended = (
                            (1.0 - assertion_metric_weight) * quality_score
                            + assertion_metric_weight * assertion_score
                        )
                        metric_stats["count"] += 1
                        metric_stats["quality_sum"] += quality_score
                        metric_stats["assertion_sum"] += assertion_score
                        metric_stats["blended_sum"] += blended
                        return float(blended)
                    except Exception:
                        return 0.0

                try:
                    from dspy.teleprompt import GEPA
                except ImportError as e:
                    optimization_result["error"] = (
                        f"GEPA is required for DSPy optimization but is unavailable: {e}"
                    )
                    optimization_result["completed_at"] = str(time.time())
                    return optimization_result
                import inspect

                auto = "light"
                auto = gepa_cfg.get("auto", auto)

                # Build GEPA kwargs dynamically to stay compatible across DSPy versions.
                init_sig = inspect.signature(GEPA.__init__)
                init_params = init_sig.parameters

                init_kwargs: Dict[str, Any] = {"metric": gepa_metric}
                optional_init_cfg = {
                    "auto": auto,
                    "reflection_lm": reflection_lm,
                    "candidate_selection_strategy": gepa_cfg.get(
                        "candidate_selection_strategy"
                    ),
                    "skip_perfect_score": gepa_cfg.get("skip_perfect_score", True),
                    "reflection_minibatch_size": gepa_cfg.get(
                        "reflection_minibatch_size"
                    ),
                    "perfect_score": gepa_cfg.get("perfect_score", 1.0),
                    "use_merge": gepa_cfg.get("use_merge", True),
                    "max_merge_invocations": gepa_cfg.get(
                        "max_merge_invocations", 5
                    ),
                    "failure_score": gepa_cfg.get("failure_score", 0.0),
                    "seed": gepa_cfg.get("seed", 0),
                }
                for key, value in optional_init_cfg.items():
                    if key in init_params and value is not None:
                        init_kwargs[key] = value

                gepa = GEPA(**init_kwargs)

                compile_sig = inspect.signature(gepa.compile)
                compile_params = compile_sig.parameters
                compile_kwargs: Dict[str, Any] = {
                    "student": program,
                    "trainset": examples,
                }
                if "valset" in compile_params:
                    compile_kwargs["valset"] = examples
                if (
                    "max_full_evals" in compile_params
                    and gepa_cfg.get("max_full_evals") is not None
                ):
                    compile_kwargs["max_full_evals"] = gepa_cfg.get(
                        "max_full_evals"
                    )
                if (
                    "max_metric_calls" in compile_params
                    and gepa_cfg.get("max_metric_calls") is not None
                ):
                    compile_kwargs["max_metric_calls"] = gepa_cfg.get(
                        "max_metric_calls"
                    )
                if "track_stats" in compile_params and gepa_cfg.get("track_stats") is not None:
                    compile_kwargs["track_stats"] = gepa_cfg.get("track_stats")

                optimized_program = gepa.compile(**compile_kwargs)
                optimizer_used = "GEPA"

                # Persist optimized weights for run-time loading.
                if hasattr(optimized_program, "save"):
                    optimized_program.save(str(self.optimized_path))

                optimization_result["success"] = True
                optimization_result["training_examples"] = len(examples)
                optimization_result["optimizer"] = optimizer_used
                optimization_result["assertion_metric_weight"] = assertion_metric_weight
                optimization_result["score"] = "optimized"
                if metric_stats["count"] > 0:
                    avg_quality = metric_stats["quality_sum"] / metric_stats["count"]
                    avg_assertion = metric_stats["assertion_sum"] / metric_stats["count"]
                    avg_blended = metric_stats["blended_sum"] / metric_stats["count"]
                    optimization_result["avg_quality_score"] = round(avg_quality, 4)
                    optimization_result["avg_assertion_score"] = round(avg_assertion, 4)
                    optimization_result["avg_blended_score"] = round(avg_blended, 4)
                    console.print(
                        "[cyan]📈 GEPA Metric Summary:[/] "
                        f"quality={avg_quality:.3f}, assertions={avg_assertion:.3f}, blended={avg_blended:.3f} "
                        f"(assertion_weight={assertion_metric_weight:.2f})"
                    )
                optimization_result["completed_at"] = str(time.time())
                return optimization_result

            # Get pipeline class
            pipeline_class = resolve_pipeline_class(module, self.agent_name)
            if not pipeline_class:
                raise AttributeError(
                    f"Could not find pipeline class for agent '{self.agent_name}' in module '{module.__name__}'"
                )
            pipeline = pipeline_class()

            # Load playbook to get functional tests
            if self.playbook_path.exists():
                with open(self.playbook_path, "r") as f:
                    playbook = yaml.safe_load(f) or {}

                spec_data = playbook.get("spec", playbook)
                scenarios = None

                if "feature_specifications" in spec_data and spec_data[
                    "feature_specifications"
                ].get("scenarios"):
                    scenarios = spec_data["feature_specifications"]["scenarios"]
                elif "scenarios" in spec_data:
                    scenarios = spec_data["scenarios"]

                if scenarios:
                    console.print(
                        f"[green]✅ Found {len(scenarios)} scenarios for optimization[/]"
                    )

                    # --------------------------------------------------
                    # 🔄  Transform scenarios -> training examples
                    # --------------------------------------------------
                    training_examples = []
                    for sc in scenarios:
                        if isinstance(sc, dict):
                            inputs = sc.get("input", {})
                            expected = sc.get("expected_output", {})
                            if inputs or expected:
                                # Merge in the same way BDDTestMixin does
                                training_examples.append({**inputs, **expected})
                            else:
                                # Fallback: if already flattened assume valid
                                training_examples.append(sc)
                        else:
                            # Unexpected format – skip gracefully
                            continue

                    # The pipeline's train method now handles saving and returns stats.
                    train_stats = pipeline.train(
                        training_data=training_examples,
                        save_optimized=True,
                        optimized_path=str(self.optimized_path),
                    )

                    # Update the main optimization result with the stats from the train method
                    optimization_result.update(train_stats)

                else:
                    optimization_result["error"] = (
                        "No scenarios found in playbook for optimization"
                    )
            else:
                optimization_result["error"] = (
                    f"Playbook not found at {self.playbook_path}"
                )

        except Exception as e:
            optimization_result["error"] = str(e)
            console.print(f"[red]❌ Optimization failed: {e}[/]")

        optimization_result["completed_at"] = str(time.time())
        return optimization_result

    async def run(
        self,
        query: str,
        use_optimization: bool = True,
        runtime_optimize: bool = False,
        force_runtime: bool = False,
        runtime_mode: str = "auto",
        provider_override: str | None = None,
        model_override: str | None = None,
    ) -> Any:
        """Run DSPy agent with given query."""
        # Suppress the specific Pydantic UserWarning that can be noisy.
        warnings.filterwarnings(
            "ignore", category=UserWarning, message="Pydantic serializer warnings.*"
        )

        # Track optimization status for better user feedback
        optimization_status = {
            "used_pre_optimized": False,
            "runtime_optimization": runtime_optimize,
            "optimization_available": False,
            "optimization_used": False,
        }

        try:
            # Check for optimized pipeline first
            optimization_status["optimization_available"] = self.optimized_path.exists()

            # Smart handling when both --optimize flag and pre-optimized file exist
            if runtime_optimize and self.optimized_path.exists() and not force_runtime:
                console.print(
                    f"\n[yellow]⚠️ Pre-optimized pipeline already exists at {self.optimized_path.name}[/]"
                )
                console.print(
                    "[yellow]You used --optimize flag, but optimization is already available.[/]"
                )
                console.print("\n[cyan]Options:[/]")
                console.print(
                    "[green]1. Use existing pre-optimized pipeline (FAST, recommended)[/]"
                )
                console.print(
                    "[yellow]2. Perform fresh runtime optimization (SLOW, may overwrite existing)[/]"
                )

                # For now, default to pre-optimized (safer and faster)
                console.print(
                    "\n[green]💡 Using existing pre-optimized pipeline for better performance.[/]"
                )
                console.print(
                    f'[dim]To force fresh optimization, use: super agent run {self.agent_name} --force-optimize --goal "goal"[/]'
                )
                console.print(
                    f"[dim]Or use: super agent optimize {self.agent_name} --force[/]"
                )

                # Override runtime_optimize to use pre-optimized
                runtime_optimize = False
                use_optimized = True
                optimization_status["used_pre_optimized"] = True
                optimization_status["optimization_used"] = True
                optimization_status["runtime_optimization"] = False
            elif force_runtime and self.optimized_path.exists():
                console.print(
                    "\n[yellow]🔄 Force runtime optimization requested - ignoring existing pre-optimized pipeline[/]"
                )
                use_optimized = False
            else:
                use_optimized = (
                    use_optimization
                    and self.optimized_path.exists()
                    and not runtime_optimize
                )

            if use_optimized:
                if not optimization_status.get(
                    "used_pre_optimized"
                ):  # Only print if not already printed above
                    optimization_status["used_pre_optimized"] = True
                    optimization_status["optimization_used"] = True
                console.print(
                    f"\n[green]🚀 Using pre-optimized pipeline from {self.optimized_path.name}[/]"
                )
            elif runtime_optimize:
                console.print(
                    "\n[yellow]⚡ Runtime optimization will be performed (slower execution)[/]"
                )
            elif self.optimized_path.exists():
                console.print(
                    "\n[yellow]📝 Pre-optimized pipeline available but runtime optimization requested[/]"
                )
            else:
                console.print(
                    "\n[yellow]📝 Using base pipeline (no optimization available)[/]"
                )

            console.print(f"\n[yellow]Looking for pipeline at:[/] {self.pipeline_path}")

            if not self.pipeline_path.exists():
                raise FileNotFoundError(f"Pipeline not found at {self.pipeline_path}")
            playbook = {}
            if self.playbook_path.exists():
                with open(self.playbook_path, "r") as f:
                    playbook = yaml.safe_load(f) or {}

            spec_data = playbook.get("spec", playbook)
            memory_enabled = self._ensure_memory_initialized(spec_data)
            if memory_enabled:
                self._start_memory_interaction(query)

            # Load pipeline module
            spec = importlib.util.spec_from_file_location(
                f"{self.agent_name}_pipeline", self.pipeline_path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module

            spec.loader.exec_module(module)

            # New minimal native DSPy path:
            # generated module exposes build_program() and runner handles runtime wiring.
            if hasattr(module, "build_program") and callable(module.build_program):
                console.print(
                    "[cyan]🧠 Running native DSPy module (runner-managed LM/playbook)[/]"
                )

                # Runtime optimization/loading are legacy Pipeline features.
                if use_optimized and self.optimized_path.exists():
                    console.print(
                        f"[cyan]📦 Found optimized DSPy weights: {self.optimized_path.name}[/]"
                    )
                if runtime_optimize:
                    console.print(
                        "[yellow]⚠️ Runtime optimization is not supported in native DSPy mode yet; running base program.[/]"
                    )

                # Configure LM from playbook (provider/model/auth stays in SuperOptiX).
                if hasattr(module, "setup_lm") and callable(module.setup_lm):
                    allow_local_ollama = bool(
                        getattr(module, "ALLOW_LOCAL_OLLAMA", False)
                    )
                    compiled_runtime_mode = str(
                        getattr(module, "RUNTIME_MODE", "auto") or "auto"
                    ).lower()
                    effective_runtime_mode = (runtime_mode or "auto").lower()
                    if effective_runtime_mode == "auto":
                        effective_runtime_mode = compiled_runtime_mode
                    effective_provider_override = provider_override or getattr(
                        module, "PROVIDER_OVERRIDE", None
                    )
                    effective_model_override = model_override or getattr(
                        module, "MODEL_OVERRIDE", None
                    )
                    lm_params = self._resolve_dspy_lm_params(
                        spec_data,
                        allow_local_ollama=allow_local_ollama,
                        purpose="task",
                        model_override=effective_model_override,
                        provider_override=effective_provider_override,
                        runtime_mode=effective_runtime_mode,
                    )
                    module.setup_lm(**lm_params)
                    self._configure_dspy_adapter(spec_data, module)
                else:
                    allow_local_ollama = bool(
                        getattr(module, "ALLOW_LOCAL_OLLAMA", False)
                    )
                    compiled_runtime_mode = str(
                        getattr(module, "RUNTIME_MODE", "auto") or "auto"
                    ).lower()
                    effective_runtime_mode = (runtime_mode or "auto").lower()
                    if effective_runtime_mode == "auto":
                        effective_runtime_mode = compiled_runtime_mode
                    effective_provider_override = provider_override or getattr(
                        module, "PROVIDER_OVERRIDE", None
                    )
                    effective_model_override = model_override or getattr(
                        module, "MODEL_OVERRIDE", None
                    )
                    self._configure_dspy_lm_from_playbook(
                        spec_data,
                        allow_local_ollama=allow_local_ollama,
                        model_override=effective_model_override,
                        provider_override=effective_provider_override,
                        runtime_mode=effective_runtime_mode,
                    )
                    self._configure_dspy_adapter(spec_data, module)

                input_field, output_fields = self._get_input_output_field_names(spec_data)
                program = module.build_program()

                if use_optimized and hasattr(program, "load"):
                    try:
                        program.load(str(self.optimized_path))
                        optimization_status["used_pre_optimized"] = True
                        optimization_status["optimization_used"] = True
                        console.print(
                            f"[green]✅ Loaded optimized DSPy program from {self.optimized_path.name}[/]"
                        )
                    except Exception as e:
                        console.print(
                            f"[yellow]⚠️ Could not load optimized weights: {e}. Using base program.[/]"
                        )

                query_for_program = query
                if self._is_rag_enabled_in_spec(spec_data):
                    context_text = await self._retrieve_context_text(spec_data, query)
                    if context_text:
                        query_for_program = self._augment_query_with_context(
                            query_for_program, context_text
                        )
                if memory_enabled:
                    memory_text = self._retrieve_memory_context_text(spec_data, query)
                    if memory_text:
                        query_for_program = self._augment_query_with_context(
                            query_for_program, memory_text
                        )

                tool_trace_enabled = self._tool_trace_enabled(spec_data)
                trace_events: list[Dict[str, Any]] = []
                if tool_trace_enabled:
                    events = trace_events

                    def _emit_tool_event(payload: Dict[str, Any]):
                        stage = str(payload.get("stage", "tool"))
                        detail = str(payload.get("detail", ""))
                        if "latency_ms" in payload:
                            detail = f"{detail} ({payload.get('latency_ms')}ms)"
                        events.append(
                            {
                                "time": datetime.now().strftime("%H:%M:%S"),
                                "stage": stage,
                                "detail": detail,
                            }
                        )
                        # Keep only recent entries for fast live updates.
                        if len(events) > 20:
                            del events[:-20]
                        try:
                            live.update(self._render_tool_trace_panel(events))
                        except Exception:
                            return

                    with Live(
                        self._render_tool_trace_panel(events),
                        console=console,
                        transient=True,
                        refresh_per_second=8,
                    ) as live:
                        set_tool_trace_emitter(_emit_tool_event)
                        try:
                            prediction = self._run_program_with_timeout(
                                program, {input_field: query_for_program}
                            )
                        finally:
                            set_tool_trace_emitter(None)
                else:
                    prediction = self._run_program_with_timeout(
                        program, {input_field: query_for_program}
                    )

                if tool_trace_enabled and trace_events:
                    console.print("[dim]Tool trace summary:[/]")
                    for event in trace_events[-20:]:
                        console.print(
                            f"{event.get('time','')} {event.get('stage','')}: {event.get('detail','')}",
                            style="dim",
                            markup=False,
                        )

                result = self._prediction_to_result(prediction, output_fields)
                if hasattr(module, "postprocess_prediction") and callable(
                    module.postprocess_prediction
                ):
                    try:
                        result = module.postprocess_prediction(
                            prediction, result, output_fields
                        )
                    except Exception as e:
                        console.print(
                            f"[yellow]⚠️ Structured postprocessing skipped: {e}[/]"
                        )
                assertion_payload = None
                if hasattr(module, "validate_prediction_result") and callable(
                    module.validate_prediction_result
                ):
                    try:
                        assertion_payload = module.validate_prediction_result(result) or {}
                        if isinstance(assertion_payload, dict):
                            result = assertion_payload.get("result", result)
                    except Exception as e:
                        console.print(
                            f"[yellow]⚠️ Assertion validation skipped: {e}[/]"
                        )
                result["is_valid"] = any(
                    (isinstance(v, str) and bool(v.strip()))
                    or (not isinstance(v, str) and v is not None)
                    for v in result.values()
                )
                if isinstance(assertion_payload, dict):
                    assertion_errors = assertion_payload.get("assertion_errors", []) or []
                    assertion_mode = str(
                        assertion_payload.get("assertion_mode", "fail_fast")
                    ).strip().lower()
                    assertions_passed = bool(
                        assertion_payload.get("assertions_passed", not assertion_errors)
                    )
                    assertion_score = assertion_payload.get("assertion_score")
                    checks_total = assertion_payload.get("checks_total")
                    checks_failed = assertion_payload.get("checks_failed")
                    result["_assertion_errors"] = assertion_errors
                    result["_assertion_mode"] = assertion_mode
                    result["_assertions_passed"] = assertions_passed
                    if assertion_score is not None:
                        result["_assertion_score"] = assertion_score
                    if checks_total is not None:
                        result["_assertion_checks_total"] = checks_total
                    if checks_failed is not None:
                        result["_assertion_checks_failed"] = checks_failed

                    if assertion_errors:
                        console.print(
                            f"[yellow]⚠️ Assertions reported {len(assertion_errors)} issue(s).[/]"
                        )
                        for issue in assertion_errors[:5]:
                            console.print(f"[yellow]   • {issue}[/]")
                        if len(assertion_errors) > 5:
                            console.print(
                                f"[yellow]   • ... {len(assertion_errors) - 5} more[/]"
                            )

                    if assertion_mode == "fail_fast" and not assertions_passed:
                        result["is_valid"] = False
                if memory_enabled:
                    result["_memory_stats"] = self._persist_memory_interaction(
                        spec_data, query, result
                    )
                result["_memory_enabled"] = bool(memory_enabled)
                result["_optimization_status"] = optimization_status
                self._end_memory_interaction(success=result.get("is_valid", False))

                # Results table
                results_table = Table(title="Analysis Results")
                results_table.add_column("Aspect", style="cyan")
                results_table.add_column("Value", style="green")
                for key, value in result.items():
                    if key not in [
                        "is_valid",
                        "_optimization_status",
                        "_assertion_errors",
                        "_assertion_mode",
                        "_assertions_passed",
                        "_assertion_score",
                        "_assertion_checks_total",
                        "_assertion_checks_failed",
                        "_memory_stats",
                        "_memory_enabled",
                    ]:
                        results_table.add_row(key.title(), str(value))
                console.print(results_table)

                color = "green" if result.get("is_valid", False) else "red"
                status = "✅ PASSED" if result.get("is_valid", False) else "❌ FAILED"
                console.print(f"\n[{color}]Validation Status: {status}[/]")
                return result

            # Initialize pipeline
            pipeline_class = resolve_pipeline_class(module, self.agent_name)
            if not pipeline_class:
                raise AttributeError(
                    f"Could not find pipeline class for agent '{self.agent_name}' in module '{module.__name__}'"
                )

            pipeline = pipeline_class()

            # Load optimized model if available and requested
            if use_optimized:
                try:
                    console.print(
                        f"[cyan]📦 Loading pre-optimized model from {self.optimized_path.name}[/]"
                    )
                    if hasattr(pipeline.module, "load"):
                        pipeline.module.load(str(self.optimized_path))
                        pipeline.is_trained = True
                        console.print(
                            "[green]✅ Pre-optimized model loaded successfully[/]"
                        )
                    else:
                        console.print(
                            "[yellow]⚠️ Pipeline doesn't support loading, falling back to base model[/]"
                        )
                        use_optimized = False
                        optimization_status["used_pre_optimized"] = False
                        optimization_status["optimization_used"] = False
                except Exception as e:
                    console.print(
                        f"[yellow]⚠️ Failed to load pre-optimized model: {e}. Using base model.[/]"
                    )
                    use_optimized = False
                    optimization_status["used_pre_optimized"] = False
                    optimization_status["optimization_used"] = False

            # Handle runtime optimization
            if runtime_optimize and not use_optimized:
                console.print("[yellow]🔄 Performing runtime optimization...[/]")
                # Train pipeline if functional tests exist to be used as golden examples
                training_examples = []
                if "feature_specifications" in spec_data and spec_data[
                    "feature_specifications"
                ].get("scenarios"):
                    scenarios = spec_data["feature_specifications"]["scenarios"]
                    # Adapt to the format expected by the pipeline's train method
                    training_examples = [
                        {"input": test["input"], "output": test["expected_output"]}
                        for test in scenarios
                    ]

                if training_examples:
                    console.print(
                        f"[green]📚 Found {len(training_examples)} scenarios for optimization[/]"
                    )
                    training_stats = pipeline.train(training_examples)
                    if training_stats.get("success", False):
                        optimization_status["optimization_used"] = True
                        console.print(
                            "[green]✅ Runtime optimization completed successfully[/]"
                        )
                    else:
                        console.print(
                            "[yellow]⚠️ Runtime optimization failed, using base model[/]"
                        )
                else:
                    console.print(
                        "[yellow]⚠️ No scenarios available for optimization, using base model[/]"
                    )

            # Basic setup if no optimization is used
            elif not use_optimized:
                # Note: Only train if this is an explicit optimization run
                # This prevents automatic training on every run
                # Only call setup() if it exists (DSPy-specific, not needed for other frameworks)
                if hasattr(pipeline, "setup") and callable(getattr(pipeline, "setup")):
                    pipeline.setup()  # Basic setup without training

            # Show execution start
            console.print(
                Panel(
                    f"[bold blue]🤖 Running {self.agent_name.title()} Pipeline[/]\n\n"
                    f"[cyan]Executing Task:[/] {query}\n",
                    title="Agent Execution",
                    border_style="blue",
                )
            )

            # Run pipeline with error handling
            try:
                # Different frameworks use different execution methods
                if hasattr(pipeline, "run") and callable(getattr(pipeline, "run")):
                    # Non-DSPy frameworks (DeepAgents, CrewAI, OpenAI, etc.) use .run()
                    # Check if run() is async
                    import inspect

                    if inspect.iscoroutinefunction(pipeline.run):
                        result = await pipeline.run(query=query)
                    else:
                        result = pipeline.run(query=query)
                elif callable(pipeline):
                    # DSPy pipelines are callable
                    result = await pipeline(query)
                else:
                    raise AttributeError(
                        f"Pipeline has no callable method (run or __call__)"
                    )

                # ------------------------------------------------------------------
                # 🎯 Basic validation if pipeline didn't provide one
                # ------------------------------------------------------------------
                if isinstance(result, dict) and "is_valid" not in result:
                    # Heuristic: check that at least one non-meta field is non-empty
                    user_fields = [
                        k
                        for k in result.keys()
                        if not k.startswith("_")
                        and k not in ("agent_id", "usage", "trained")
                    ]
                    non_empty = any(
                        bool(str(result.get(f, "")).strip()) for f in user_fields
                    )
                    result["is_valid"] = non_empty
                    if not non_empty:
                        result["validation_warnings"] = (
                            "All primary output fields are empty"
                        )
                    else:
                        result["validation_warnings"] = []

                if memory_enabled and isinstance(result, dict):
                    result["_memory_stats"] = self._persist_memory_interaction(
                        spec_data, query, result
                    )
                    result["_memory_enabled"] = True
                self._end_memory_interaction(
                    success=bool(result.get("is_valid", False))
                    if isinstance(result, dict)
                    else True
                )

            except Exception as e:
                error_str = str(e)
                if memory_enabled:
                    self._end_memory_interaction(success=False, error=error_str)

                # Check for the specific Ollama KeyError: 'name' error
                if (
                    "KeyError: 'name'" in error_str
                    or "litellm.APIConnectionError: 'name'" in error_str
                ):
                    console.print("\n[red]❌ Model Compatibility Error[/]")
                    console.print(
                        "\n[yellow]The current model does not support structured output format required by DSPy.[/]"
                    )
                    console.print(
                        "\n[cyan]Please try one of the following solutions:[/]"
                    )
                    console.print(
                        "1. [bold]Use a different model[/] in your playbook configuration:"
                    )
                    console.print(
                        "   - OpenAI models (gpt-3.5-turbo, gpt-4) support structured output"
                    )
                    console.print(
                        "   - For Ollama, try models like llama3:70b or mixtral:8x7b"
                    )
                    console.print(
                        "2. [bold]Update your playbook[/] to use a compatible model:"
                    )
                    console.print(
                        "   - Edit the model field in your agent's playbook.yaml file"
                    )
                    console.print("   - Example: model: gpt-3.5-turbo")
                    console.print("\n[yellow]To edit your playbook:[/]")
                    console.print(
                        f"  nano {self.project_root}/{self.system_name}/agents/{self.agent_name}/playbook/{self.agent_name}_playbook.yaml"
                    )
                    return None

                # Generic error handling for other errors
                console.print(
                    f"\n[red]❌ Error during pipeline execution:[/] {error_str}"
                )
                console.print(
                    "\n[yellow]This might be due to a JSON parsing error or model compatibility issue.[/]"
                )
                console.print("\n[cyan]Suggestions:[/]")
                console.print(
                    "1. Try using a different model in your playbook configuration"
                )
                console.print("2. Check if Ollama is running with the correct model")
                console.print("3. Try a simpler query")
                console.print("\n[yellow]Technical details:[/]")
                console.print(f"{error_str}")
                return None

            # Add optimization status to result
            if result and isinstance(result, dict):
                result["_optimization_status"] = optimization_status
                if memory_enabled:
                    result.setdefault("_memory_enabled", True)

            # Display results
            if result:
                # Results table
                results_table = Table(title="Analysis Results")
                results_table.add_column("Aspect", style="cyan")
                results_table.add_column("Value", style="green")

                for key, value in result.items():
                    if key not in [
                        "evaluation",
                        "is_valid",
                        "is_optimized",
                        "validation_warnings",
                        "_optimization_status",  # Hide internal optimization status
                        "_memory_stats",
                        "_memory_enabled",
                    ]:
                        results_table.add_row(key.title(), str(value))

                console.print(results_table)

                # Evaluation table
                if "evaluation" in result:
                    eval_table = Table(title="Evaluation Metrics")
                    eval_table.add_column("Metric", style="cyan")
                    eval_table.add_column("Score", style="green")

                    for metric, score in result["evaluation"].items():
                        if isinstance(score, float):
                            eval_table.add_row(metric.title(), f"{score:.2f}")
                        else:
                            eval_table.add_row(metric.title(), str(score))

                    console.print(eval_table)

                # Enhanced optimization status display
                opt_status = result.get("_optimization_status", optimization_status)

                if opt_status["used_pre_optimized"]:
                    console.print("\n[green]Pre-Optimized Pipeline: ✅ YES[/]")
                    console.print("[green]Runtime Optimization: ⚪ NO[/]")
                elif (
                    opt_status["runtime_optimization"]
                    and opt_status["optimization_used"]
                ):
                    console.print("\n[yellow]Pre-Optimized Pipeline: ⚪ NO[/]")
                    console.print("[green]Runtime Optimization: ✅ YES[/]")
                elif opt_status["optimization_available"]:
                    console.print(
                        "\n[yellow]Pre-Optimized Pipeline: ⚠️ Available but not used[/]"
                    )
                    console.print("[yellow]Runtime Optimization: ⚪ NO[/]")
                    console.print(
                        f"[dim]💡 Use 'super agent run {self.agent_name} --goal \"goal\"' to use pre-optimization[/]"
                    )
                else:
                    console.print("\n[yellow]Pre-Optimized Pipeline: ⚪ NO[/]")
                    console.print("[yellow]Runtime Optimization: ⚪ NO[/]")
                    console.print(
                        f"[dim]💡 Run 'super agent optimize {self.agent_name}' to create optimized version[/]"
                    )

                # Validation status
                color = "green" if result.get("is_valid", False) else "red"
                status = "✅ PASSED" if result.get("is_valid", False) else "❌ FAILED"
                console.print(f"\n[{color}]Validation Status: {status}[/]")

                if "validation_warnings" in result:
                    console.print(
                        f"[yellow]Validation Warnings: {result['validation_warnings']}[/]"
                    )

                # Return the full result object for orchestration purposes
                return result

            return None

        except FileNotFoundError as e:
            if "memory_enabled" in locals() and memory_enabled:
                self._end_memory_interaction(success=False, error=str(e))
            console.print(f"\n[red]❌ Error:[/] {e}")
            return None
        except Exception as e:
            if "memory_enabled" in locals() and memory_enabled:
                self._end_memory_interaction(success=False, error=str(e))
            console.print(f"\n[red]❌ An unexpected error occurred:[/] {e}")
            import traceback

            traceback.print_exc()
            return None
        finally:
            # Restore warnings
            warnings.resetwarnings()

    @staticmethod
    def format_result(result: Dict[str, Any]) -> str:
        """Format result for display."""
        if isinstance(result, dict):
            return "\n".join(f"{k}: {v}" for k, v in result.items())
        return str(result)
