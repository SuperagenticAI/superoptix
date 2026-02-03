"""Tier-based feature gating system for SuperOptiX DSPy capabilities."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class TierLevel(Enum):
    """Available tier levels in SuperOptiX - simplified for current version."""

    ORACLES = "oracles"
    GENIES = "genies"


@dataclass
class FeatureConfig:
    """Configuration for a specific feature."""

    name: str
    description: str
    min_tier: TierLevel
    beta: bool = False


class TierSystem:
    """Manages tier-based feature access and validation."""

    def __init__(self):
        self.features = self._initialize_features()
        self.tier_hierarchy = self._get_tier_hierarchy()

    def _initialize_features(self) -> Dict[str, FeatureConfig]:
        """Initialize all available features with their tier requirements."""
        return {
            # Oracles Tier - Basic DSPy Features
            "basic_predict": FeatureConfig(
                name="Basic Predict Module",
                description="Simple prediction with input/output",
                min_tier=TierLevel.ORACLES,
            ),
            "chain_of_thought": FeatureConfig(
                name="Chain of Thought",
                description="Reasoning with intermediate steps",
                min_tier=TierLevel.ORACLES,
            ),
            "bootstrap_fewshot": FeatureConfig(
                name="Bootstrap Few-Shot",
                description="Basic prompt optimization",
                min_tier=TierLevel.ORACLES,
            ),
            "basic_evaluation": FeatureConfig(
                name="Basic Evaluation",
                description="Exact match and F1 score metrics",
                min_tier=TierLevel.ORACLES,
            ),
            "sequential_orchestra": FeatureConfig(
                name="Sequential Orchestra",
                description="Basic sequential task orchestration",
                min_tier=TierLevel.ORACLES,
            ),
            # Genies Tier - Enhanced Features
            "react_agents": FeatureConfig(
                name="ReAct Agents",
                description="Reasoning and Acting with tools",
                min_tier=TierLevel.GENIES,
            ),
            "tool_integration": FeatureConfig(
                name="Tool Integration",
                description="Basic tool integration framework",
                min_tier=TierLevel.GENIES,
            ),
            "rag_retrieval": FeatureConfig(
                name="RAG Retrieval",
                description="Retrieval-Augmented Generation",
                min_tier=TierLevel.GENIES,
            ),
            "agent_memory": FeatureConfig(
                name="Agent Memory",
                description="Short-term and episodic memory",
                min_tier=TierLevel.GENIES,
            ),
            "basic_streaming": FeatureConfig(
                name="Basic Streaming",
                description="Real-time response streaming",
                min_tier=TierLevel.GENIES,
            ),
            "json_xml_adapters": FeatureConfig(
                name="JSON/XML Adapters",
                description="Structured input/output formats",
                min_tier=TierLevel.GENIES,
            ),
        }

    def _get_tier_hierarchy(self) -> Dict[TierLevel, int]:
        """Get tier hierarchy for access level checking."""
        return {
            TierLevel.ORACLES: 1,
            TierLevel.GENIES: 2,
        }

    def check_feature_access(self, feature_name: str, user_tier: TierLevel) -> bool:
        """Check if user tier has access to a specific feature."""
        if feature_name not in self.features:
            return False

        feature = self.features[feature_name]
        user_level = self.tier_hierarchy[user_tier]
        required_level = self.tier_hierarchy[feature.min_tier]

        return user_level >= required_level

    def get_accessible_features(self, user_tier: TierLevel) -> List[FeatureConfig]:
        """Get all features accessible to a user tier."""
        accessible = []
        for feature in self.features.values():
            if self.check_feature_access(
                feature.name.lower().replace(" ", "_"), user_tier
            ):
                accessible.append(feature)
        return accessible

    def get_upgrade_message(self, feature_name: str, user_tier: TierLevel) -> str:
        """Get upgrade message for a feature."""
        if feature_name not in self.features:
            return f"Feature '{feature_name}' not found."

        feature = self.features[feature_name]
        if self.check_feature_access(feature_name, user_tier):
            return f"You already have access to {feature.name}."

        return f"Upgrade to {feature.min_tier.value.title()} tier to access {feature.name}."

    def get_tier_features_summary(self, tier: TierLevel) -> Dict[str, List[str]]:
        """Get a summary of features available in a tier."""
        accessible = self.get_accessible_features(tier)

        categories = {
            "Basic Features": [],
            "Advanced Features": [],
        }

        for feature in accessible:
            if feature.min_tier == TierLevel.ORACLES:
                categories["Basic Features"].append(feature.name)
            else:
                categories["Advanced Features"].append(feature.name)

        return categories

    def validate_playbook_features(
        self, playbook_config: Dict, user_tier: TierLevel
    ) -> Dict[str, List[str]]:
        """Validate that all features in a playbook are accessible to the user tier."""
        errors = []
        warnings = []

        # Check for advanced features that require Genies tier
        if user_tier == TierLevel.ORACLES:
            # Check if playbook uses ReAct or tools
            if playbook_config.get("spec", {}).get("react_config"):
                errors.append("ReAct agents require Genies tier")

            if playbook_config.get("spec", {}).get("tools"):
                errors.append("Tool integration requires Genies tier")

            if playbook_config.get("spec", {}).get("rag_config"):
                errors.append("RAG retrieval requires Genies tier")

            if playbook_config.get("spec", {}).get("memory"):
                errors.append("Agent memory requires Genies tier")

        return {
            "errors": errors,
            "warnings": warnings,
        }


# Global tier system instance
tier_system = TierSystem()
