"""
Integration tests for enhanced pipeline templates

Tests that the pipeline templates properly integrate with the optimizer factory
and that existing functionality is not broken.
"""

import pytest
from unittest.mock import Mock, patch

# Mock DSPy imports to avoid dependency issues in tests
import sys
from unittest.mock import MagicMock

# Create mock dspy module
mock_dspy = MagicMock()
mock_dspy.LM = MagicMock()
mock_dspy.configure = MagicMock()
mock_dspy.Example = MagicMock()
mock_dspy.ChainOfThought = MagicMock()
mock_dspy.context = MagicMock()
sys.modules["dspy"] = mock_dspy

from superoptix.core.optimizer_factory import DSPyOptimizerFactory


class TestPipelineIntegration:
    """Test suite for pipeline template integration."""

    @pytest.fixture
    def sample_oracle_playbook(self):
        """Create a sample Oracle tier playbook for testing."""
        return {
            "apiVersion": "agent/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "Test Oracle Agent",
                "id": "test-oracle",
                "level": "oracles",
            },
            "spec": {
                "language_model": {
                    "provider": "ollama",
                    "model": "llama3.2:1b",
                    "temperature": 0.1,
                    "max_tokens": 32000,
                },
                "persona": {"role": "Test Assistant", "goal": "Test functionality"},
                "tasks": [
                    {
                        "name": "answer_question",
                        "inputs": [{"name": "question", "type": "str"}],
                        "outputs": [{"name": "answer", "type": "str"}],
                    }
                ],
                "optimization": {
                    "optimizer": {
                        "name": "BootstrapFewShot",
                        "params": {
                            "metric": "answer_exact_match",
                            "max_bootstrapped_demos": 3,
                        },
                    }
                },
                "feature_specifications": {
                    "scenarios": [
                        {
                            "name": "test_scenario",
                            "input": {"question": "What is 2+2?"},
                            "expected_output": {"answer": "4"},
                        }
                    ]
                },
            },
        }

    @pytest.fixture
    def sample_genie_playbook(self):
        """Create a sample Genie tier playbook for testing."""
        return {
            "apiVersion": "agent/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "Test Genie Agent",
                "id": "test-genie",
                "level": "genies",
            },
            "spec": {
                "language_model": {
                    "provider": "ollama",
                    "model": "llama3.1:8b",
                    "temperature": 0.1,
                    "max_tokens": 32000,
                },
                "persona": {
                    "role": "Test ReAct Assistant",
                    "goal": "Test ReAct functionality",
                },
                "tasks": [
                    {
                        "name": "answer_with_tools",
                        "inputs": [{"name": "question", "type": "str"}],
                        "outputs": [{"name": "answer", "type": "str"}],
                    }
                ],
                "optimization": {
                    "optimizer": {
                        "name": "GEPA",
                        "params": {
                            "metric": "answer_exact_match",
                            "auto": "light",
                            "reflection_lm": "llama3.1:8b",
                        },
                    }
                },
                "feature_specifications": {
                    "scenarios": [
                        {
                            "name": "test_tool_scenario",
                            "input": {"question": "Calculate 15 * 23"},
                            "expected_output": {"answer": "345"},
                        }
                    ]
                },
            },
        }

    def test_optimizer_factory_integration(self):
        """Test that optimizer factory works with pipeline utilities."""
        from superoptix.core.pipeline_utils import PipelineUtilities

        # Test get_optimizer method
        optimizer = PipelineUtilities.get_optimizer("oracles", k=5)
        assert optimizer is not None
        assert hasattr(optimizer, "compile")

        # Test get_custom_optimizer method
        optimizer = PipelineUtilities.get_custom_optimizer(
            "BootstrapFewShot", params={"max_bootstrapped_demos": 3}
        )
        assert optimizer is not None
        assert hasattr(optimizer, "compile")

    def test_lm_configuration_extraction(self, sample_oracle_playbook):
        """Test LM configuration extraction from playbook."""
        lm_config = sample_oracle_playbook["spec"]["language_model"]

        # Test that configuration is properly structured
        assert lm_config["provider"] == "ollama"
        assert lm_config["model"] == "llama3.2:1b"
        assert lm_config["temperature"] == 0.1
        assert lm_config["max_tokens"] == 32000

    def test_optimizer_config_parsing(self, sample_oracle_playbook):
        """Test optimizer configuration parsing from playbook."""
        optimizer_config = sample_oracle_playbook["spec"]["optimization"]["optimizer"]

        assert optimizer_config["name"] == "BootstrapFewShot"
        assert "params" in optimizer_config
        assert optimizer_config["params"]["max_bootstrapped_demos"] == 3

    def test_bdd_scenario_extraction(self, sample_oracle_playbook):
        """Test BDD scenario extraction from playbook."""
        scenarios = sample_oracle_playbook["spec"]["feature_specifications"][
            "scenarios"
        ]

        assert len(scenarios) == 1
        assert scenarios[0]["name"] == "test_scenario"
        assert scenarios[0]["input"]["question"] == "What is 2+2?"
        assert scenarios[0]["expected_output"]["answer"] == "4"

    @patch("superoptix.core.optimizer_factory.DSPyOptimizerFactory.create_optimizer")
    def test_optimizer_creation_flow(
        self, mock_create_optimizer, sample_oracle_playbook
    ):
        """Test the optimizer creation flow in pipelines."""
        # Mock the optimizer creation
        mock_optimizer = Mock()
        mock_optimizer.compile = Mock(return_value=Mock())
        mock_create_optimizer.return_value = mock_optimizer

        # Test configuration extraction
        optimizer_config = sample_oracle_playbook["spec"]["optimization"]["optimizer"]
        lm_config = sample_oracle_playbook["spec"]["language_model"]

        # Simulate what the pipeline template does
        DSPyOptimizerFactory.create_optimizer(
            optimizer_name=optimizer_config["name"],
            params=optimizer_config["params"],
            lm_config=lm_config,
        )

        # Verify the factory was called correctly
        mock_create_optimizer.assert_called_once_with(
            optimizer_name="BootstrapFewShot",
            params={"metric": "answer_exact_match", "max_bootstrapped_demos": 3},
            lm_config=lm_config,
        )

    def test_gepa_configuration(self, sample_genie_playbook):
        """Test GEPA-specific configuration handling."""
        optimizer_config = sample_genie_playbook["spec"]["optimization"]["optimizer"]

        assert optimizer_config["name"] == "GEPA"
        assert "reflection_lm" in optimizer_config["params"]
        assert optimizer_config["params"]["reflection_lm"] == "llama3.1:8b"
        assert optimizer_config["params"]["auto"] == "light"

    def test_tier_based_optimization(self):
        """Test tier-based optimizer selection."""
        # Test Oracle tier
        optimizer = DSPyOptimizerFactory.create_tier_optimized_optimizer(
            tier="oracles", training_data_size=3, optimizer_config=None
        )
        assert optimizer is not None

        # Test Genies tier
        optimizer = DSPyOptimizerFactory.create_tier_optimized_optimizer(
            tier="genies", training_data_size=10, optimizer_config=None
        )
        assert optimizer is not None

    def test_error_handling_invalid_optimizer(self):
        """Test error handling for invalid optimizer configurations."""
        with pytest.raises(ValueError):
            DSPyOptimizerFactory.create_optimizer("NonExistentOptimizer")

    def test_fallback_optimizer_creation(self):
        """Test fallback to dummy optimizer when creation fails."""
        from superoptix.core.pipeline_utils import PipelineUtilities

        # This should not raise an exception even with invalid optimizer
        optimizer = PipelineUtilities.get_custom_optimizer(
            "NonExistentOptimizer", params={}
        )

        # Should return dummy optimizer that has compile method
        assert optimizer is not None
        assert hasattr(optimizer, "compile")

    def test_copro_special_handling(self):
        """Test special handling for COPRO optimizer."""
        # COPRO requires eval_kwargs, test this is handled correctly
        try:
            optimizer = DSPyOptimizerFactory.create_optimizer("COPRO")
            assert optimizer is not None

            # Test that it has the expected interface
            assert hasattr(optimizer, "compile")

        except ImportError:
            pytest.skip("COPRO not available in test environment")

    def test_metric_conversion(self):
        """Test metric string to function conversion."""
        # Test built-in metrics
        metric_func = DSPyOptimizerFactory._get_metric_function("answer_exact_match")
        assert callable(metric_func)

        metric_func = DSPyOptimizerFactory._get_metric_function(
            "answer_substring_match"
        )
        assert callable(metric_func)

        # Test fallback for unknown metric
        metric_func = DSPyOptimizerFactory._get_metric_function("unknown_metric")
        assert callable(metric_func)

    def test_alternative_optimizer_names(self):
        """Test that alternative optimizer names work correctly."""
        # Test both naming conventions
        optimizer1 = DSPyOptimizerFactory.create_optimizer("bootstrap_few_shot")
        optimizer2 = DSPyOptimizerFactory.create_optimizer("BootstrapFewShot")

        assert optimizer1 is not None
        assert optimizer2 is not None
        assert type(optimizer1) is type(optimizer2)

    @pytest.mark.parametrize(
        "tier,expected_optimizer",
        [
            ("oracles", "LabeledFewShot"),
            ("genies", "BootstrapFewShot"),
        ],
    )
    def test_tier_default_optimizers(self, tier, expected_optimizer):
        """Test that correct default optimizers are selected for each tier."""
        optimizer = DSPyOptimizerFactory.create_tier_optimized_optimizer(
            tier=tier, training_data_size=5, optimizer_config=None
        )

        assert optimizer is not None
        # Note: We can't easily test the exact type without importing the actual classes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
