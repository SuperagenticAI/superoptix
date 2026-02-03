"""
Framework-agnostic base component for SuperOptiX.

Inspired by Optimas BaseComponent pattern, adapted for SuperOptiX multi-framework support.
"""

import threading
from abc import abstractmethod
from contextlib import contextmanager
from types import SimpleNamespace
from typing import Any, Dict, List, Optional


class BaseComponent:
    """
    Universal component interface for all agent frameworks.

    This class provides a framework-agnostic interface for wrapping agents from
    different frameworks (DSPy, CrewAI, OpenAI, Microsoft, DeepAgent, Google ADK).

    Key Concepts:
    - input_fields: What data the component needs
    - output_fields: What data the component produces
    - variable: The optimizable part (prompt, instructions, etc.) - GEPA optimizes this!
    - config: Framework-specific configuration (model, temperature, etc.)
    - framework: Which framework this component uses

    Thread-safe for parallel optimization.
    """

    def __init__(
        self,
        name: str,
        description: str,
        input_fields: List[str],
        output_fields: List[str],
        variable: Optional[Any] = None,
        variable_type: str = "prompt",
        variable_search_space: Optional[Dict[str, List[Any]]] = None,
        config: Optional[Dict[str, Any]] = None,
        framework: str = "dspy",
    ):
        """
        Initialize a framework-agnostic component.

        Args:
            name: Component name (e.g., "research_agent")
            description: Human-readable description
            input_fields: List of input field names (e.g., ["query", "context"])
            output_fields: List of output field names (e.g., ["response", "confidence"])
            variable: The optimizable variable (prompt/instructions/etc.)
            variable_type: Type of variable ("prompt", "hyperparameter", "local_lm")
            variable_search_space: Search space for optimization (optional)
            config: Configuration dict (model, temperature, etc.)
            framework: Target framework ("dspy", "crewai", "openai", "microsoft", "deepagents", "google-adk")
        """
        self.name = name
        self.description = description
        self.input_fields = input_fields
        self.output_fields = output_fields
        self.variable_type = variable_type
        self.variable_search_space = variable_search_space
        self.framework = framework

        # Thread-safe variable and config management
        self._default_variable = variable
        self._default_config = SimpleNamespace(**(config or {}))
        self._thread_local = threading.local()
        self._lock = threading.Lock()

        # Execution trajectory (for debugging/tracing)
        self.traj = {}

    @property
    def optimizable(self) -> bool:
        """Returns True if this component has an optimizable variable."""
        return self._default_variable is not None

    @property
    def variable(self):
        """
        Thread-safe access to the optimizable variable.

        This is what GEPA will optimize (prompt, instructions, etc.)
        """
        if not hasattr(self._thread_local, "variable"):
            with self._lock:
                self._thread_local.variable = self._default_variable
        return self._thread_local.variable

    @property
    def config(self) -> SimpleNamespace:
        """Thread-safe access to configuration."""
        if not hasattr(self._thread_local, "config"):
            with self._lock:
                self._thread_local.config = SimpleNamespace(
                    **vars(self._default_config)
                )
        return self._thread_local.config

    def update(self, new_variable: Any) -> None:
        """
        Update the optimizable variable (used by GEPA optimizer).

        Args:
            new_variable: New optimized variable value
        """
        with self._lock:
            self._default_variable = new_variable
            if hasattr(self._thread_local, "variable"):
                self._thread_local.variable = new_variable

    def update_config(self, **kwargs) -> None:
        """
        Update configuration values.

        Args:
            **kwargs: Config key-value pairs to update
        """
        with self._lock:
            config_dict = vars(self.config).copy()
            config_dict.update(kwargs)
            self._thread_local.config = SimpleNamespace(**config_dict)

    @contextmanager
    def context(self, variable=None, **config_overrides):
        """
        Temporarily override variable/config within a context.

        Useful for testing different prompts without permanently changing them.

        Args:
            variable: Optional variable override
            **config_overrides: Config overrides (e.g., temperature=0.8)

        Example:
            with component.context(variable="New prompt", temperature=0.9):
                result = component(query="test")
        """
        original_variable = self.variable
        original_config = vars(self.config).copy()

        try:
            if variable is not None:
                with self._lock:
                    self._thread_local.variable = variable

            if config_overrides:
                self.update_config(**config_overrides)

            yield self

        finally:
            with self._lock:
                self._thread_local.variable = original_variable
                self._thread_local.config = SimpleNamespace(**original_config)

    @abstractmethod
    def forward(self, **inputs: Any) -> Dict[str, Any]:
        """
        Execute the component (framework-specific implementation).

        Args:
            **inputs: Input values matching input_fields

        Returns:
            Dict mapping output_fields to their values

        Example:
            outputs = component.forward(query="What is AI?")
            # Returns: {"response": "AI is...", "confidence": 0.95}
        """
        raise NotImplementedError("Subclasses must implement forward()")

    def __call__(self, **inputs: Any) -> Dict[str, Any]:
        """
        Execute component and track trajectory.

        Args:
            **inputs: Input values

        Returns:
            Output dict
        """
        # Validate inputs
        missing_inputs = set(self.input_fields) - set(inputs.keys())
        if missing_inputs:
            raise ValueError(
                f"Component '{self.name}' missing required inputs: {missing_inputs}"
            )

        # Execute
        outputs = self.forward(**inputs)

        # Track trajectory
        self.traj = {
            "input": inputs,
            "output": outputs,
            "variable": self.variable,
            "framework": self.framework,
        }

        return outputs

    def get_component_info(self) -> Dict[str, Any]:
        """
        Get component metadata.

        Returns:
            Dict with component info
        """
        return {
            "name": self.name,
            "description": self.description,
            "framework": self.framework,
            "input_fields": self.input_fields,
            "output_fields": self.output_fields,
            "optimizable": self.optimizable,
            "variable_type": self.variable_type,
        }

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(name='{self.name}', "
            f"framework='{self.framework}', "
            f"optimizable={self.optimizable})"
        )
