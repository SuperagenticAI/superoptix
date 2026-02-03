"""Oracles tier playbook validator"""

from typing import Dict, List, Any


class OraclesPlaybookValidator:
    """Validator for Oracles and Genies tier playbooks."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate(self, playbook_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate a playbook for Oracles/Genies tier compatibility."""
        self.errors = []
        self.warnings = []

        # Validate metadata
        self._validate_metadata(playbook_data.get("metadata", {}))

        # Validate spec
        self._validate_spec(playbook_data.get("spec", {}))

        return {"errors": self.errors, "warnings": self.warnings}

    def _validate_metadata(self, metadata: Dict[str, Any]):
        """Validate metadata section."""
        if not metadata.get("name"):
            self.errors.append("Metadata must include 'name' field")

        if not metadata.get("id"):
            self.errors.append("Metadata must include 'id' field")

        if not metadata.get("version"):
            self.errors.append("Metadata must include 'version' field")

        # Validate tier
        tier = metadata.get("level", "oracles")
        valid_tiers = ["oracles", "genies"]
        if tier not in valid_tiers:
            self.errors.append(
                f"Invalid tier '{tier}'. Must be one of: {', '.join(valid_tiers)}"
            )

    def _validate_spec(self, spec: Dict[str, Any]):
        """Validate spec section."""
        if not spec.get("language_model"):
            self.errors.append("Spec must include 'language_model' configuration")

        if not spec.get("tasks"):
            self.errors.append("Spec must include 'tasks' array")
        elif not isinstance(spec["tasks"], list) or len(spec["tasks"]) == 0:
            self.errors.append("Spec must include at least one task")

        # Validate tier-specific features
        tier = spec.get("metadata", {}).get("level", "oracles")

        if tier == "oracles":
            # Oracles tier shouldn't have ReAct, tools, or memory
            if spec.get("react_config"):
                self.errors.append("ReAct configuration requires Genies tier")

            if spec.get("tools"):
                self.errors.append("Tool configuration requires Genies tier")

            if spec.get("memory"):
                self.errors.append("Memory configuration requires Genies tier")

            if spec.get("rag_config"):
                self.errors.append("RAG configuration requires Genies tier")

        elif tier == "genies":
            # Genies tier can have these features, but validate their structure
            if spec.get("react_config"):
                self._validate_react_config(spec["react_config"])

            if spec.get("tools"):
                self._validate_tools_config(spec["tools"])

            if spec.get("memory"):
                self._validate_memory_config(spec["memory"])

    def _validate_react_config(self, react_config: Dict[str, Any]):
        """Validate ReAct configuration."""
        if not isinstance(react_config, dict):
            self.errors.append("ReAct configuration must be a dictionary")
            return

        if "enabled" not in react_config:
            self.errors.append("ReAct configuration must include 'enabled' field")

    def _validate_tools_config(self, tools_config: Dict[str, Any]):
        """Validate tools configuration."""
        if not isinstance(tools_config, dict):
            self.errors.append("Tools configuration must be a dictionary")
            return

        if "enabled" not in tools_config:
            self.errors.append("Tools configuration must include 'enabled' field")

    def _validate_memory_config(self, memory_config: Dict[str, Any]):
        """Validate memory configuration."""
        if not isinstance(memory_config, dict):
            self.errors.append("Memory configuration must be a dictionary")
            return

        if "enabled" not in memory_config:
            self.errors.append("Memory configuration must include 'enabled' field")
