from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BaseInput(BaseModel):
    """Base input model with arbitrary types allowed."""

    model_config = ConfigDict(arbitrary_types_allowed=True)


class BaseOutput(BaseModel):
    """Base output model with arbitrary types allowed."""

    model_config = ConfigDict(arbitrary_types_allowed=True)


class SentimentInput(BaseInput):
    """Input model for sentiment analysis."""

    text: str = Field(..., description="Text to analyze")


class SentimentOutput(BaseOutput):
    """Output model for sentiment analysis."""

    sentiment: str = Field(..., description="Analyzed sentiment")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    key_phrases: List[str] = Field(
        default_factory=list, description="Key phrases identified"
    )
    reasoning: List[str] = Field(
        default_factory=list, description="Reasoning for sentiment"
    )


# --- Agent Tier System ---


class AgentTier(str, Enum):
    """Agent capability tiers that determine available features."""

    ORACLES = "oracles"
    GENIES = "genies"


class OrchestrationType(str, Enum):
    """Types of orchestration available - only basic sequential for current version."""

    BASIC = "basic"  # Sequential orchestration only


# --- Orchestra Orchestration Models ---


class Workspace(BaseModel):
    """Defines the shared workspace for an orchestra."""

    type: str = Field(
        "local_fs", description="The type of workspace, e.g., 'local_fs'."
    )
    path: str = Field(..., description="The path to the shared workspace directory.")


class ExecutionStrategy(str, Enum):
    """Execution strategy for orchestra tasks - simplified for current version."""

    SEQUENTIAL = "sequential"


class TaskPriority(str, Enum):
    """Priority levels for tasks."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DependencyType(str, Enum):
    """Types of task dependencies."""

    REQUIRES_OUTPUT = "requires_output"  # Task needs output from another task
    REQUIRES_COMPLETION = "requires_completion"  # Task needs another task to complete


class TaskDependency(BaseModel):
    """Defines a dependency between tasks."""

    task_name: str = Field(..., description="Name of the dependent task.")
    dependency_type: DependencyType = Field(
        default=DependencyType.REQUIRES_OUTPUT, description="Type of dependency."
    )
    timeout_seconds: Optional[int] = Field(
        default=None, description="Timeout for waiting on dependency."
    )


class Task(BaseModel):
    """Defines a single task to be executed by an agent in an orchestra."""

    name: str = Field(..., description="Unique name for the task.")
    agent: str = Field(..., description="The name of the agent assigned to this task.")
    description: str = Field(
        ..., description="Detailed description of the task, can include placeholders."
    )
    context: List[str] = Field(
        default_factory=list,
        description="List of names of other tasks whose output is required as input.",
    )

    # Basic execution configuration
    dependencies: List[TaskDependency] = Field(
        default_factory=list, description="Task dependencies."
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM, description="Task priority level."
    )
    timeout_seconds: Optional[int] = Field(
        default=None, description="Task execution timeout."
    )
    retry_count: int = Field(default=0, description="Number of retries on failure.")


# --- Tier-Based Feature Configuration ---


class TierFeatures(BaseModel):
    """Defines available features for each agent tier."""

    @staticmethod
    def get_available_features(tier: AgentTier) -> Dict[str, Any]:
        """Get available features for a specific tier."""
        base_features = {
            "orchestration_types": [OrchestrationType.BASIC],
            "max_parallel_tasks": 1,  # Sequential only
            "execution_strategies": ["sequential"],
            "basic_optimization": True,
            "basic_evaluation": True,
        }

        if tier == AgentTier.GENIES:
            base_features.update(
                {
                    "rag_retrieval": True,
                    "react_tools": True,
                    "agent_memory": True,
                }
            )

        return base_features


class TierValidator:
    """Validates orchestration configuration against agent tier restrictions."""

    @staticmethod
    def validate_orchestration_access(
        agent_tier: AgentTier, orchestra_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate if the given agent tier can access the requested orchestration features.

        Returns:
            Dict with 'valid' (bool) and 'errors' (List[str]) keys
        """
        errors = []
        features = TierFeatures.get_available_features(agent_tier)

        # Check orchestration type - only basic allowed
        orchestra_type = orchestra_config.get("type", "basic")
        if orchestra_type != "basic":
            errors.append(
                f"Only basic sequential orchestration is supported. "
                f"Current tier: {agent_tier.value}"
            )

        # Check execution strategy - only sequential allowed
        execution_strategy = orchestra_config.get("execution", {}).get(
            "strategy", "sequential"
        )
        if execution_strategy != "sequential":
            errors.append(
                f"Only sequential execution strategy is supported. "
                f"Current tier: {agent_tier.value}"
            )

        # Check parallel tasks - should be 1 for sequential
        max_parallel = orchestra_config.get("execution", {}).get(
            "max_parallel_tasks", 1
        )
        if max_parallel > 1:
            errors.append(
                f"Only sequential execution supported (max_parallel_tasks=1). "
                f"Current tier: {agent_tier.value}"
            )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "available_features": features,
        }


class ExecutionConfig(BaseModel):
    """Configuration for orchestra execution - simplified for current version."""

    strategy: ExecutionStrategy = Field(
        default=ExecutionStrategy.SEQUENTIAL,
        description="Execution strategy - sequential only.",
    )
    max_parallel_tasks: int = Field(
        default=1,
        description="Maximum number of tasks to run in parallel - always 1 for sequential.",
    )
    task_timeout_seconds: int = Field(
        default=300, description="Default timeout for tasks."
    )
    retry_strategy: str = Field(
        default="simple", description="Retry strategy for failed tasks."
    )

    # Performance monitoring
    enable_metrics: bool = Field(
        default=True, description="Enable execution metrics collection."
    )
    enable_trace: bool = Field(default=True, description="Enable execution tracing.")


class OrchestraDefinition(BaseModel):
    """The root model for an orchestra definition YAML file."""

    id: str = Field(
        ..., description="The unique identifier for the orchestra, used in the CLI."
    )
    name: str = Field(..., description="The display name of the orchestra.")
    description: str = Field(
        ..., description="A brief description of what the orchestra does."
    )
    workspace: Workspace = Field(..., description="The shared workspace configuration.")

    # Basic execution configuration
    execution: ExecutionConfig = Field(
        default_factory=ExecutionConfig, description="Execution configuration."
    )

    # Tier-based configuration
    orchestration_type: OrchestrationType = Field(
        default=OrchestrationType.BASIC, description="Type of orchestration to use."
    )
    required_tier: Optional[AgentTier] = Field(
        default=None, description="Minimum tier required to run this orchestra."
    )


class OrchestraFile(BaseModel):
    """Represents the entire structure of a _orchestra.yaml file."""

    orchestra: OrchestraDefinition
    agents: List[str] = Field(
        ..., description="A list of agent names that are part of this orchestra."
    )
    tasks: List[Task] = Field(
        ..., description="A list of tasks that define the orchestration workflow."
    )

    @field_validator("orchestra")
    @classmethod
    def validate_tier_compatibility(cls, v):
        """Validate that the orchestra configuration is compatible with the required tier."""
        if v.required_tier and v.required_tier not in [
            AgentTier.ORACLES,
            AgentTier.GENIES,
        ]:
            raise ValueError(
                f"Unsupported tier: {v.required_tier}. Only Oracles and Genies tiers are supported."
            )
        return v


# --- Exception Classes ---


class TierPermissionError(Exception):
    """Raised when an agent tier doesn't have permission for a feature."""

    def __init__(
        self,
        message: str,
        current_tier: str,
        required_tier: str = None,
        available_features: Dict[str, Any] = None,
    ):
        self.current_tier = current_tier
        self.required_tier = required_tier
        self.available_features = available_features
        super().__init__(message)
