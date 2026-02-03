"""
Unit tests for DSPy Optimizer Factory

Tests the optimizer factory functionality including:
- Optimizer creation and configuration
- Parameter handling and validation
- LM configuration for special optimizers
- Error handling and fallbacks
"""

import pytest
from unittest.mock import Mock, patch

from superoptix.core.optimizer_factory import DSPyOptimizerFactory


class TestDSPyOptimizerFactory:
    """Test suite for DSPy Optimizer Factory."""

    def test_get_available_optimizers(self):
        """Test getting available optimizers list."""
        optimizers = DSPyOptimizerFactory.get_available_optimizers()

        assert isinstance(optimizers, dict)
        assert "gepa" in optimizers
        assert "simba" in optimizers
        assert "bootstrapfewshot" in optimizers
        assert "miprov2" in optimizers

        # Check descriptions are provided
        assert "Genetic-Pareto" in optimizers["gepa"]
        assert "Stochastic Introspective Mini-Batch Ascent" in optimizers["simba"]

    def test_create_basic_optimizer(self):
        """Test creating basic optimizers without special configuration."""
        # Test BootstrapFewShot
        optimizer = DSPyOptimizerFactory.create_optimizer("BootstrapFewShot")
        assert optimizer is not None
        assert hasattr(optimizer, "compile")

        # Test LabeledFewShot
        optimizer = DSPyOptimizerFactory.create_optimizer("LabeledFewShot")
        assert optimizer is not None
        assert hasattr(optimizer, "compile")

    def test_create_optimizer_with_params(self):
        """Test creating optimizers with custom parameters."""
        params = {"max_bootstrapped_demos": 5, "max_labeled_demos": 10, "max_rounds": 2}

        optimizer = DSPyOptimizerFactory.create_optimizer(
            "BootstrapFewShot", params=params
        )

        assert optimizer is not None
        assert hasattr(optimizer, "compile")

    @patch("superoptix.core.optimizer_factory.dspy.LM")
    def test_create_gepa_optimizer(self, mock_lm):
        """Test creating GEPA optimizer with reflection LM."""
        mock_lm_instance = Mock()
        mock_lm.return_value = mock_lm_instance

        params = {
            "metric": "answer_exact_match",
            "auto": "light",
            "reflection_lm": "llama3.1:8b",
        }

        lm_config = {"model": "llama3.2:1b", "provider": "ollama"}

        try:
            optimizer = DSPyOptimizerFactory.create_optimizer(
                "GEPA", params=params, lm_config=lm_config
            )

            # Verify LM was created for reflection
            mock_lm.assert_called()
            assert optimizer is not None

        except ImportError:
            # GEPA might not be available in test environment
            pytest.skip("GEPA not available in test environment")

    def test_create_simba_optimizer(self):
        """Test creating SIMBA optimizer."""
        params = {
            "metric": "answer_exact_match",
            "bsize": 16,
            "num_candidates": 4,
            "max_steps": 6,
        }

        try:
            optimizer = DSPyOptimizerFactory.create_optimizer("SIMBA", params=params)
            assert optimizer is not None
            assert hasattr(optimizer, "compile")

        except ImportError:
            pytest.skip("SIMBA not available in test environment")

    def test_create_tier_optimized_optimizer_oracles(self):
        """Test tier-optimized optimizer creation for oracles tier."""
        optimizer = DSPyOptimizerFactory.create_tier_optimized_optimizer(
            tier="oracles", training_data_size=3, optimizer_config=None
        )

        assert optimizer is not None
        assert hasattr(optimizer, "compile")

    def test_create_tier_optimized_optimizer_genies(self):
        """Test tier-optimized optimizer creation for genies tier."""
        optimizer = DSPyOptimizerFactory.create_tier_optimized_optimizer(
            tier="genies", training_data_size=10, optimizer_config=None
        )

        assert optimizer is not None
        assert hasattr(optimizer, "compile")

    def test_create_tier_optimized_with_config(self):
        """Test tier-optimized optimizer with custom config."""
        optimizer_config = {
            "name": "BootstrapFewShot",
            "params": {"max_bootstrapped_demos": 3},
        }

        optimizer = DSPyOptimizerFactory.create_tier_optimized_optimizer(
            tier="oracles", training_data_size=5, optimizer_config=optimizer_config
        )

        assert optimizer is not None
        assert hasattr(optimizer, "compile")

    def test_invalid_optimizer_name(self):
        """Test error handling for invalid optimizer names."""
        with pytest.raises(ValueError) as exc_info:
            DSPyOptimizerFactory.create_optimizer("InvalidOptimizer")

        assert "Unknown optimizer" in str(exc_info.value)
        assert "InvalidOptimizer" in str(exc_info.value)

    def test_metric_functions(self):
        """Test built-in metric functions."""
        # Create mock example and prediction
        example = Mock()
        example.answer = "Paris"

        pred = Mock()
        pred.answer = "Paris"

        # Test exact match
        score = DSPyOptimizerFactory._answer_exact_match(example, pred)
        assert score == 1.0

        # Test non-match
        pred.answer = "London"
        score = DSPyOptimizerFactory._answer_exact_match(example, pred)
        assert score == 0.0

    def test_substring_match_metric(self):
        """Test substring match metric."""
        example = Mock()
        example.answer = "The capital is Paris"

        pred = Mock()
        pred.answer = "Paris is the answer"

        score = DSPyOptimizerFactory._answer_substring_match(example, pred)
        assert score == 1.0  # "Paris" appears in both

    def test_fuzzy_match_metric(self):
        """Test fuzzy match metric."""
        example = Mock()
        example.answer = "Paris"

        pred = Mock()
        pred.answer = "Parris"  # Close but not exact

        score = DSPyOptimizerFactory._fuzzy_match(example, pred)
        assert score > 0.0  # Should be some similarity
        assert score < 1.0  # But not perfect match

    def test_alternative_optimizer_names(self):
        """Test alternative naming conventions for optimizers."""
        # Test underscore versions
        optimizer1 = DSPyOptimizerFactory.create_optimizer("bootstrap_few_shot")
        optimizer2 = DSPyOptimizerFactory.create_optimizer("bootstrapfewshot")

        assert optimizer1 is not None
        assert optimizer2 is not None
        assert type(optimizer1) is type(optimizer2)

    def test_parameter_validation(self):
        """Test parameter validation and filtering."""
        # Test that invalid parameters are filtered out and don't break creation
        # LabeledFewShot only accepts 'k' parameter
        params = {
            "k": 5,  # Valid parameter for LabeledFewShot
            "invalid_param": "should_be_ignored",  # Should be filtered out
        }

        # Should not raise error even with invalid params (they should be filtered)
        optimizer = DSPyOptimizerFactory.create_optimizer(
            "LabeledFewShot", params=params
        )
        assert optimizer is not None

    def test_empty_params(self):
        """Test handling of empty or None parameters."""
        optimizer = DSPyOptimizerFactory.create_optimizer("LabeledFewShot", params=None)
        assert optimizer is not None

        optimizer = DSPyOptimizerFactory.create_optimizer("LabeledFewShot", params={})
        assert optimizer is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
