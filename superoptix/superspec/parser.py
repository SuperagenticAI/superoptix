"""
SuperSpec Parser

Parses agent playbook files according to the SuperSpec DSL specification.
Provides structured access to playbook configuration.
"""

import yaml
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass


@dataclass
class AgentMetadata:
    """Agent metadata structure."""

    name: str
    id: str
    version: str
    namespace: Optional[str] = None
    level: str = "oracles"
    stage: str = "alpha"
    agent_type: str = "Autonomous"
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class TaskDefinition:
    """Task definition structure."""

    name: str
    instruction: str
    description: Optional[str] = None
    inputs: Optional[List[Dict[str, Any]]] = None
    outputs: Optional[List[Dict[str, Any]]] = None
    schema: Optional[Dict[str, Any]] = None
    reasoning_steps: Optional[List[str]] = None
    training_examples: Optional[List[Dict[str, Any]]] = None
    assertions: Optional[List[Dict[str, Any]]] = None


@dataclass
class AgentFlowStep:
    """Agent flow step structure."""

    name: str
    type: str
    task: str
    depends_on: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None
    retry_policy: Optional[Dict[str, Any]] = None


@dataclass
class AgentSpec:
    """Complete agent specification."""

    api_version: str
    kind: str
    metadata: AgentMetadata
    language_model: Dict[str, Any]
    tasks: List[TaskDefinition]
    dspy: Optional[Dict[str, Any]] = None
    pydantic_ai: Optional[Dict[str, Any]] = None
    openai_agent: Optional[Dict[str, Any]] = None
    google_adk: Optional[Dict[str, Any]] = None
    deepagents: Optional[Dict[str, Any]] = None
    crewai: Optional[Dict[str, Any]] = None
    rlm: Optional[Dict[str, Any]] = None
    persona: Optional[Dict[str, Any]] = None
    agentflow: Optional[List[AgentFlowStep]] = None
    retrieval: Optional[Dict[str, Any]] = None
    memory: Optional[Dict[str, Any]] = None
    tool_calling: Optional[Dict[str, Any]] = None
    evaluation: Optional[Dict[str, Any]] = None
    optimization: Optional[Dict[str, Any]] = None
    training: Optional[Dict[str, Any]] = None
    runtime: Optional[Dict[str, Any]] = None
    observability: Optional[Dict[str, Any]] = None
    security: Optional[Dict[str, Any]] = None
    feature_specifications: Optional[Dict[str, Any]] = None


class SuperSpecXParser:
    """Parser for SuperSpec DSL playbook files."""

    def __init__(self):
        """Initialize the parser."""
        self.parsed_specs = {}
        self.parsing_errors = []

    def parse_file(self, file_path: Union[str, Path]) -> Optional[AgentSpec]:
        """
        Parse a playbook file.

        Args:
            file_path: Path to the playbook YAML file

        Returns:
            Parsed AgentSpec or None if parsing failed
        """
        try:
            file_path = Path(file_path)

            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.suffix.lower() in [".yaml", ".yml"]:
                    data = yaml.safe_load(f)
                elif file_path.suffix.lower() == ".json":
                    data = json.load(f)
                else:
                    raise ValueError(f"Unsupported file format: {file_path.suffix}")

            return self.parse_dict(data, str(file_path))

        except Exception as e:
            self.parsing_errors.append(f"Failed to parse {file_path}: {str(e)}")
            return None

    def parse_dict(
        self, data: Dict[str, Any], source: str = "dict"
    ) -> Optional[AgentSpec]:
        """
        Parse a dictionary containing playbook data.

        Args:
            data: Dictionary with playbook configuration
            source: Source identifier for error reporting

        Returns:
            Parsed AgentSpec or None if parsing failed
        """
        try:
            # Parse metadata
            metadata_dict = data.get("metadata", {})
            metadata = AgentMetadata(
                name=metadata_dict.get("name", ""),
                id=metadata_dict.get("id", ""),
                version=metadata_dict.get("version", "1.0.0"),
                namespace=metadata_dict.get("namespace"),
                level=metadata_dict.get("level", "oracles"),
                stage=metadata_dict.get("stage", "alpha"),
                agent_type=metadata_dict.get("agent_type", "Autonomous"),
                description=metadata_dict.get("description"),
                tags=metadata_dict.get("tags"),
                created_at=metadata_dict.get("created_at"),
                updated_at=metadata_dict.get("updated_at"),
            )

            # Parse spec section
            spec_dict = data.get("spec", {})

            # Parse tasks
            tasks = []
            for task_dict in spec_dict.get("tasks", []):
                task = TaskDefinition(
                    name=task_dict.get("name", ""),
                    instruction=task_dict.get("instruction", ""),
                    description=task_dict.get("description"),
                    inputs=task_dict.get("inputs"),
                    outputs=task_dict.get("outputs"),
                    schema=task_dict.get("schema"),
                    reasoning_steps=task_dict.get("reasoning_steps"),
                    training_examples=task_dict.get("training_examples"),
                    assertions=task_dict.get("assertions"),
                )
                tasks.append(task)

            # Parse agentflow
            agentflow = []
            for step_dict in spec_dict.get("agentflow", []):
                step = AgentFlowStep(
                    name=step_dict.get("name", ""),
                    type=step_dict.get("type", ""),
                    task=step_dict.get("task", ""),
                    depends_on=step_dict.get("depends_on"),
                    config=step_dict.get("config"),
                    retry_policy=step_dict.get("retry_policy"),
                )
                agentflow.append(step)

            # Create AgentSpec
            agent_spec = AgentSpec(
                api_version=data.get("apiVersion", "agent/v1"),
                kind=data.get("kind", "AgentSpec"),
                metadata=metadata,
                language_model=spec_dict.get("language_model", {}),
                tasks=tasks,
                dspy=spec_dict.get("dspy"),
                pydantic_ai=spec_dict.get("pydantic_ai"),
                openai_agent=spec_dict.get("openai_agent"),
                google_adk=spec_dict.get("google_adk"),
                deepagents=spec_dict.get("deepagents"),
                crewai=spec_dict.get("crewai"),
                rlm=spec_dict.get("rlm"),
                persona=spec_dict.get("persona"),
                agentflow=agentflow if agentflow else None,
                retrieval=spec_dict.get("retrieval"),
                memory=spec_dict.get("memory"),
                tool_calling=spec_dict.get("tool_calling"),
                evaluation=spec_dict.get("evaluation"),
                optimization=spec_dict.get("optimization"),
                training=spec_dict.get("training"),
                runtime=spec_dict.get("runtime"),
                observability=spec_dict.get("observability"),
                security=spec_dict.get("security"),
                feature_specifications=spec_dict.get("feature_specifications"),
            )

            # Cache parsed spec
            self.parsed_specs[source] = agent_spec
            return agent_spec

        except Exception as e:
            self.parsing_errors.append(f"Failed to parse {source}: {str(e)}")
            return None

    def parse_directory(
        self, directory_path: Union[str, Path], pattern: str = "*.yaml"
    ) -> List[AgentSpec]:
        """
        Parse all playbook files in a directory.

        Args:
            directory_path: Path to directory containing playbook files
            pattern: File pattern to match (default: *.yaml)

        Returns:
            List of parsed AgentSpecs
        """
        directory_path = Path(directory_path)
        parsed_specs = []

        if not directory_path.exists():
            self.parsing_errors.append(f"Directory not found: {directory_path}")
            return parsed_specs

        # Find matching files
        if pattern.startswith("*"):
            files = directory_path.glob(pattern)
        else:
            files = directory_path.rglob(pattern)

        for file_path in files:
            if file_path.is_file():
                spec = self.parse_file(file_path)
                if spec:
                    parsed_specs.append(spec)

        return parsed_specs

    def get_tier_distribution(self) -> Dict[str, int]:
        """Get distribution of agent tiers from parsed specs."""
        tier_counts = {}
        for spec in self.parsed_specs.values():
            tier = spec.metadata.level
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        return tier_counts

    def get_namespace_distribution(self) -> Dict[str, int]:
        """Get distribution of agent namespaces from parsed specs."""
        namespace_counts = {}
        for spec in self.parsed_specs.values():
            namespace = spec.metadata.namespace or "unspecified"
            namespace_counts[namespace] = namespace_counts.get(namespace, 0) + 1
        return namespace_counts

    def find_specs_by_tier(self, tier: str) -> List[AgentSpec]:
        """Find all specs matching a specific tier."""
        return [
            spec for spec in self.parsed_specs.values() if spec.metadata.level == tier
        ]

    def find_specs_by_namespace(self, namespace: str) -> List[AgentSpec]:
        """Find all specs matching a specific namespace."""
        return [
            spec
            for spec in self.parsed_specs.values()
            if spec.metadata.namespace == namespace
        ]

    def find_specs_with_feature(self, feature: str) -> List[AgentSpec]:
        """Find all specs that use a specific feature."""
        specs_with_feature = []
        for spec in self.parsed_specs.values():
            if hasattr(spec, feature) and getattr(spec, feature) is not None:
                specs_with_feature.append(spec)
        return specs_with_feature

    def get_parsing_summary(self) -> Dict[str, Any]:
        """Get summary of parsing results."""
        total_parsed = len(self.parsed_specs)
        errors_count = len(self.parsing_errors)

        tier_dist = self.get_tier_distribution()
        namespace_dist = self.get_namespace_distribution()

        # Feature usage statistics
        feature_usage = {}
        features_to_check = [
            "dspy",
            "pydantic_ai",
            "openai_agent",
            "google_adk",
            "deepagents",
            "crewai",
            "memory",
            "tool_calling",
            "retrieval",
            "rlm",
            "agentflow",
            "optimization",
        ]

        for feature in features_to_check:
            count = len(self.find_specs_with_feature(feature))
            feature_usage[feature] = count

        return {
            "total_parsed": total_parsed,
            "parsing_errors": errors_count,
            "tier_distribution": tier_dist,
            "namespace_distribution": namespace_dist,
            "feature_usage": feature_usage,
            "errors": self.parsing_errors,
        }

    def export_to_json(self, spec: AgentSpec, file_path: Union[str, Path]) -> bool:
        """
        Export a parsed spec to JSON format.

        Args:
            spec: AgentSpec to export
            file_path: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert to dictionary
            spec_dict = {
                "apiVersion": spec.api_version,
                "kind": spec.kind,
                "metadata": {
                    "name": spec.metadata.name,
                    "id": spec.metadata.id,
                    "version": spec.metadata.version,
                    "namespace": spec.metadata.namespace,
                    "level": spec.metadata.level,
                    "stage": spec.metadata.stage,
                    "agent_type": spec.metadata.agent_type,
                    "description": spec.metadata.description,
                    "tags": spec.metadata.tags,
                    "created_at": spec.metadata.created_at,
                    "updated_at": spec.metadata.updated_at,
                },
                "spec": {
                    "language_model": spec.language_model,
                    "tasks": [
                        {
                            "name": task.name,
                            "instruction": task.instruction,
                            "description": task.description,
                            "inputs": task.inputs,
                            "outputs": task.outputs,
                            "schema": task.schema,
                            "reasoning_steps": task.reasoning_steps,
                            "training_examples": task.training_examples,
                            "assertions": task.assertions,
                        }
                        for task in spec.tasks
                    ],
                },
            }

            # Add optional fields
            if spec.persona:
                spec_dict["spec"]["persona"] = spec.persona
            if spec.agentflow:
                spec_dict["spec"]["agentflow"] = [
                    {
                        "name": step.name,
                        "type": step.type,
                        "task": step.task,
                        "depends_on": step.depends_on,
                        "config": step.config,
                        "retry_policy": step.retry_policy,
                    }
                    for step in spec.agentflow
                ]

            # Add other optional sections
            optional_fields = [
                "dspy",
                "pydantic_ai",
                "openai_agent",
                "google_adk",
                "deepagents",
                "crewai",
                "rlm",
                "retrieval",
                "memory",
                "tool_calling",
                "evaluation",
                "optimization",
                "training",
                "runtime",
                "observability",
                "security",
                "feature_specifications",
            ]

            for field in optional_fields:
                value = getattr(spec, field)
                if value is not None:
                    spec_dict["spec"][field] = value

            # Write to file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(spec_dict, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            self.parsing_errors.append(f"Failed to export to JSON: {str(e)}")
            return False

    def validate_tier_compatibility(self, spec: AgentSpec) -> List[str]:
        """
        Validate if spec features match the declared tier.

        Args:
            spec: AgentSpec to validate

        Returns:
            List of compatibility issues
        """
        issues = []
        tier = spec.metadata.level

        # Unified OSS flow supports memory/tool_calling/retrieval for DSPy across tiers.
        # Keep this method for legacy metadata checks only.

        # Check agentflow step types
        if spec.agentflow:
            oracles_types = ["Generate", "Think", "Compare", "Route"]
            genies_types = oracles_types + ["ActWithTools", "Search"]

            allowed_types = oracles_types if tier == "oracles" else genies_types

            for step in spec.agentflow:
                if step.type not in allowed_types:
                    issues.append(
                        f"Agentflow step type '{step.type}' not allowed for {tier} tier"
                    )

        return issues

    def validate_optimizer_compatibility(self, spec: AgentSpec) -> List[str]:
        """
        Validate if optimizer configuration is compatible with agent tier.

        Args:
            spec: AgentSpec to validate

        Returns:
            List of optimizer compatibility issues
        """
        issues = []

        if not spec.optimization or not spec.optimization.get("optimizer"):
            return issues

        tier = spec.metadata.level
        optimizer_config = spec.optimization.get("optimizer", {})
        optimizer_name = optimizer_config.get("name")

        if not optimizer_name:
            return issues

        # Import optimizer compatibility from schema
        from .schema import SuperSpecXSchema

        compatible_optimizers = SuperSpecXSchema.OPTIMIZER_TIER_COMPATIBILITY.get(
            tier, []
        )

        if optimizer_name not in compatible_optimizers:
            issues.append(
                f"Optimizer '{optimizer_name}' is not compatible with {tier} tier. "
                f"Compatible optimizers: {', '.join(compatible_optimizers)}"
            )

        # Note: Tier-specific validation can be enabled later if needed
        # For now, all optimizers are allowed for all tiers

        # Validate optimizer-specific parameters
        params = optimizer_config.get("params", {})

        if optimizer_name == "GEPA":
            # GEPA supports sensible defaults in runner/template.
            # Keep validation lightweight: only validate obviously conflicting budgets.
            if (
                params.get("auto") is not None
                and params.get("max_full_evals") is not None
            ):
                issues.append(
                    "GEPA params: use either 'auto' or 'max_full_evals', not both."
                )
            if (
                params.get("auto") is not None
                and params.get("max_metric_calls") is not None
            ):
                issues.append(
                    "GEPA params: use either 'auto' or 'max_metric_calls', not both."
                )

        elif optimizer_name == "SIMBA":
            # SIMBA parameter validation
            if params.get("bsize", 8) > 50:
                issues.append("SIMBA 'bsize' parameter should not exceed 50")

        elif optimizer_name == "BootstrapFewShot":
            # BootstrapFewShot parameter validation
            if params.get("max_bootstrapped_demos", 4) > 50:
                issues.append(
                    "BootstrapFewShot 'max_bootstrapped_demos' should not exceed 50"
                )

        return issues

    def get_optimization_summary(self, spec: AgentSpec) -> Dict[str, Any]:
        """
        Get optimization configuration summary for a spec.

        Args:
            spec: AgentSpec to analyze

        Returns:
            Dictionary with optimization summary
        """
        if not spec.optimization:
            return {"enabled": False}

        optimization = spec.optimization
        optimizer_config = optimization.get("optimizer", {})

        summary = {
            "enabled": optimization.get("enabled", False),
            "optimizer": {
                "name": optimizer_config.get("name", "Not specified"),
                "tier_compatible": True,
                "parameters": len(optimizer_config.get("params", {})),
                "has_metric": "metric" in optimizer_config.get("params", {}),
                "estimated_time": "Unknown",
            },
            "evaluation": {
                "enabled": optimization.get("evaluation", {}).get("enabled", True),
                "cross_validation": optimization.get("evaluation", {})
                .get("cross_validation", {})
                .get("enabled", False),
            },
            "hardware_optimization": {
                "target_tier": optimization.get("hardware_optimization", {}).get(
                    "target_tier", "standard"
                ),
                "parallel": optimization.get("hardware_optimization", {}).get(
                    "parallel_optimization", False
                ),
            },
        }

        # Check compatibility
        compatibility_issues = self.validate_optimizer_compatibility(spec)
        summary["optimizer"]["tier_compatible"] = len(compatibility_issues) == 0
        summary["compatibility_issues"] = compatibility_issues

        # Estimate time based on optimizer and budget
        optimizer_name = optimizer_config.get("name")
        if optimizer_name == "GEPA":
            budget = optimizer_config.get("params", {}).get("auto", "light")
            time_estimates = {
                "minimal": "1-2 minutes",
                "light": "3-5 minutes",
                "medium": "8-12 minutes",
                "heavy": "15-30 minutes",
            }
            summary["optimizer"]["estimated_time"] = time_estimates.get(
                budget, "3-5 minutes"
            )
        elif optimizer_name == "SIMBA":
            summary["optimizer"]["estimated_time"] = "1-3 minutes"
        elif optimizer_name == "BootstrapFewShot":
            summary["optimizer"]["estimated_time"] = "30-60 seconds"

        return summary

    def find_specs_with_optimizer(self, optimizer_name: str) -> List[AgentSpec]:
        """Find all specs that use a specific optimizer."""
        specs_with_optimizer = []
        for spec in self.parsed_specs.values():
            if (
                spec.optimization
                and spec.optimization.get("optimizer", {}).get("name") == optimizer_name
            ):
                specs_with_optimizer.append(spec)
        return specs_with_optimizer

    def get_optimizer_usage_stats(self) -> Dict[str, Any]:
        """Get statistics about optimizer usage across parsed specs."""
        total_specs = len(self.parsed_specs)
        optimized_specs = 0
        optimizer_counts = {}
        tier_optimizer_usage = {}

        for spec in self.parsed_specs.values():
            if spec.optimization and spec.optimization.get("enabled", False):
                optimized_specs += 1
                optimizer_name = spec.optimization.get("optimizer", {}).get(
                    "name", "Unknown"
                )
                optimizer_counts[optimizer_name] = (
                    optimizer_counts.get(optimizer_name, 0) + 1
                )

                # Track by tier
                tier = spec.metadata.level
                if tier not in tier_optimizer_usage:
                    tier_optimizer_usage[tier] = {}
                tier_optimizer_usage[tier][optimizer_name] = (
                    tier_optimizer_usage[tier].get(optimizer_name, 0) + 1
                )

        return {
            "total_specs": total_specs,
            "optimized_specs": optimized_specs,
            "optimization_rate": optimized_specs / total_specs
            if total_specs > 0
            else 0,
            "optimizer_distribution": optimizer_counts,
            "tier_optimizer_usage": tier_optimizer_usage,
            "most_popular_optimizer": max(optimizer_counts, key=optimizer_counts.get)
            if optimizer_counts
            else None,
        }

    def clear_cache(self):
        """Clear parsed specs cache and errors."""
        self.parsed_specs.clear()
        self.parsing_errors.clear()
