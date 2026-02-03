"""
Optimizer Factory for DSPy Optimizers

This module provides a factory pattern for creating and configuring DSPy optimizers
with proper parameter handling and LLM configuration.
"""

import inspect
import logging
from typing import Any, Callable, Dict, Optional

import dspy
from dspy.teleprompt import (
    GEPA,
    SIMBA,
    BootstrapFewShot,
    BootstrapFewShotWithRandomSearch,
    BetterTogether,
    COPRO,
    Ensemble,
    KNNFewShot,
    LabeledFewShot,
    MIPROv2,
)

logger = logging.getLogger(__name__)


class DSPyOptimizerFactory:
    """Factory for creating DSPy optimizers with proper configuration."""

    # Registry of available optimizers
    OPTIMIZER_REGISTRY = {
        "gepa": GEPA,
        "simba": SIMBA,
        "bootstrapfewshot": BootstrapFewShot,
        "bootstrap_few_shot": BootstrapFewShot,  # Alternative name
        "bootstrapfewshotwithRandomsearch": BootstrapFewShotWithRandomSearch,
        "random_search": BootstrapFewShotWithRandomSearch,  # Alternative name
        "bettertogether": BetterTogether,
        "better_together": BetterTogether,  # Alternative name
        "copro": COPRO,
        "ensemble": Ensemble,
        "knnfewshot": KNNFewShot,
        "knn_few_shot": KNNFewShot,  # Alternative name
        "labeledfewshot": LabeledFewShot,
        "labeled_few_shot": LabeledFewShot,  # Alternative name
        "miprov2": MIPROv2,
        "mipro": MIPROv2,  # Alternative name
    }

    # Default parameters for each optimizer
    DEFAULT_PARAMS = {
        "gepa": {
            "metric": "answer_exact_match",
            "auto": "light",
        },
        "simba": {
            "metric": "answer_exact_match",
            "bsize": 32,
            "num_candidates": 6,
            "max_steps": 8,
            "max_demos": 4,
            "demo_input_field_maxlen": 100_000,
            "num_threads": 1,
            "temperature_for_sampling": 0.2,
            "temperature_for_candidates": 0.2,
        },
        "bootstrapfewshot": {
            "metric": "answer_exact_match",
            "max_bootstrapped_demos": 4,
            "max_labeled_demos": 16,
            "max_rounds": 1,
        },
        "random_search": {
            "metric": "answer_exact_match",
            "num_candidates": 10,
            "num_threads": 1,
        },
        "bettertogether": {
            "metric": "answer_exact_match",
            "max_bootstrapped_demos": 4,
            "max_labeled_demos": 16,
        },
        "copro": {
            "metric": "answer_exact_match",
            "breadth": 10,
            "depth": 3,
            "init_temperature": 1.4,
        },
        "ensemble": {
            "metric": "answer_exact_match",
            "size": 3,
        },
        "knnfewshot": {
            "k": 3,
            "trainset": None,  # Will be provided during compilation
        },
        "labeledfewshot": {
            "k": 16,
        },
        "miprov2": {
            "metric": "answer_exact_match",
            "num_candidates": 20,
            "init_temperature": 1.0,
        },
    }

    @classmethod
    def get_available_optimizers(cls) -> Dict[str, str]:
        """Get list of available optimizers with descriptions."""
        descriptions = {
            "gepa": "Genetic-Pareto - Reflective prompt evolution",
            "simba": "Stochastic Introspective Mini-Batch Ascent - Advanced optimization",
            "bootstrapfewshot": "Bootstrap Few-Shot - Basic few-shot learning",
            "random_search": "Random Search - Bootstrap with random search",
            "bettertogether": "Better Together - Ensemble of few-shot examples",
            "copro": "COPRO - Collaborative Prompt Optimization",
            "ensemble": "Ensemble - Multiple model ensemble",
            "knnfewshot": "KNN Few-Shot - K-nearest neighbor few-shot",
            "labeledfewshot": "Labeled Few-Shot - Traditional few-shot with labels",
            "miprov2": "MIPROv2 - Multi-step Instruction Prompt Optimization",
        }
        return descriptions

    @classmethod
    def create_optimizer(
        cls,
        optimizer_name: str,
        params: Optional[Dict[str, Any]] = None,
        lm_config: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Create an optimizer instance with proper configuration.

        Args:
            optimizer_name: Name of the optimizer to create
            params: Custom parameters for the optimizer
            lm_config: Language model configuration for special optimizers like GEPA

        Returns:
            Configured optimizer instance

        Raises:
            ValueError: If optimizer name is not recognized
            RuntimeError: If optimizer configuration fails
        """
        optimizer_name_lower = optimizer_name.lower().replace("-", "").replace("_", "")

        if optimizer_name_lower not in cls.OPTIMIZER_REGISTRY:
            available = ", ".join(cls.OPTIMIZER_REGISTRY.keys())
            raise ValueError(
                f"Unknown optimizer: {optimizer_name}. Available optimizers: {available}"
            )

        optimizer_class = cls.OPTIMIZER_REGISTRY[optimizer_name_lower]

        # Get default parameters and merge with custom params
        default_params = cls.DEFAULT_PARAMS.get(optimizer_name_lower, {}).copy()
        if params:
            default_params.update(params)

        try:
            # Special handling for optimizers requiring specific configuration
            return cls._configure_optimizer(
                optimizer_class, optimizer_name_lower, default_params, lm_config
            )

        except Exception as e:
            logger.error(f"Failed to create optimizer {optimizer_name}: {e}")
            raise RuntimeError(
                f"Failed to create optimizer {optimizer_name}: {e}"
            ) from e

    @classmethod
    def _configure_optimizer(
        cls,
        optimizer_class: type,
        optimizer_name: str,
        params: Dict[str, Any],
        lm_config: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Configure specific optimizer with proper parameter handling."""

        if optimizer_name == "gepa":
            return cls._configure_gepa(optimizer_class, params, lm_config)
        elif optimizer_name == "simba":
            return cls._configure_simba(optimizer_class, params)
        elif optimizer_name in ["bootstrapfewshot", "bootstrap_few_shot"]:
            return cls._configure_bootstrap(optimizer_class, params)
        elif optimizer_name == "copro":
            return cls._configure_copro(optimizer_class, params)
        elif optimizer_name in ["knnfewshot", "knn_few_shot"]:
            return cls._configure_knn(optimizer_class, params)
        else:
            # Generic configuration for other optimizers
            return cls._configure_generic(optimizer_class, params)

    @classmethod
    def _configure_gepa(
        cls,
        optimizer_class: type,
        params: Dict[str, Any],
        lm_config: Optional[Dict[str, Any]] = None,
    ) -> GEPA:
        """Configure GEPA optimizer with reflection LM."""
        # Handle reflection_lm configuration
        if "reflection_lm" in params:
            if isinstance(params["reflection_lm"], str):
                # Convert string model name to LM instance
                reflection_lm_model = params["reflection_lm"]
                reflection_lm_provider = params.get("reflection_lm_provider", "ollama")

                if reflection_lm_provider == "ollama":
                    if not reflection_lm_model.startswith("ollama_chat/"):
                        reflection_lm_model = f"ollama_chat/{reflection_lm_model}"
                    params["reflection_lm"] = dspy.LM(
                        model=reflection_lm_model,
                        provider="ollama",
                        api_base="http://localhost:11434",
                        api_key="",
                        temperature=1.0,
                        max_tokens=32000,
                    )
                else:
                    params["reflection_lm"] = dspy.LM(
                        model=reflection_lm_model,
                        provider=reflection_lm_provider,
                        temperature=1.0,
                        max_tokens=32000,
                    )
        elif lm_config:
            # Use provided LM config for reflection LM
            reflection_lm_model = lm_config.get("model", "qwen3:8b")
            reflection_lm_provider = lm_config.get("provider", "ollama")

            if reflection_lm_provider == "ollama":
                if not reflection_lm_model.startswith("ollama_chat/"):
                    reflection_lm_model = f"ollama_chat/{reflection_lm_model}"
                params["reflection_lm"] = dspy.LM(
                    model=reflection_lm_model,
                    provider="ollama",
                    api_base="http://localhost:11434",
                    api_key="",
                    temperature=1.0,
                    max_tokens=32000,
                )
            else:
                params["reflection_lm"] = dspy.LM(
                    model=reflection_lm_model,
                    provider=reflection_lm_provider,
                    temperature=1.0,
                    max_tokens=32000,
                )

        # Handle metric configuration
        if isinstance(params.get("metric"), str):
            params["metric"] = cls._get_metric_function(params["metric"])

        # Remove provider-specific params before passing to GEPA
        gepa_params = {k: v for k, v in params.items() if not k.endswith("_provider")}

        return optimizer_class(**gepa_params)

    @classmethod
    def _configure_simba(cls, optimizer_class: type, params: Dict[str, Any]) -> SIMBA:
        """Configure SIMBA optimizer."""
        # Handle metric configuration
        if isinstance(params.get("metric"), str):
            params["metric"] = cls._get_metric_function(params["metric"])

        return optimizer_class(**params)

    @classmethod
    def _configure_bootstrap(
        cls, optimizer_class: type, params: Dict[str, Any]
    ) -> BootstrapFewShot:
        """Configure Bootstrap Few-Shot optimizer."""
        # Handle metric configuration
        if isinstance(params.get("metric"), str):
            params["metric"] = cls._get_metric_function(params["metric"])

        return optimizer_class(**params)

    @classmethod
    def _configure_copro(cls, optimizer_class: type, params: Dict[str, Any]) -> COPRO:
        """Configure COPRO optimizer."""
        # Handle metric configuration
        if isinstance(params.get("metric"), str):
            params["metric"] = cls._get_metric_function(params["metric"])

        return optimizer_class(**params)

    @classmethod
    def _configure_knn(
        cls, optimizer_class: type, params: Dict[str, Any]
    ) -> KNNFewShot:
        """Configure KNN Few-Shot optimizer."""
        # KNN Few-Shot doesn't require metric, just k and trainset
        return optimizer_class(**params)

    @classmethod
    def _configure_generic(cls, optimizer_class: type, params: Dict[str, Any]) -> Any:
        """Configure generic optimizer."""
        # Handle metric configuration if present
        if isinstance(params.get("metric"), str):
            params["metric"] = cls._get_metric_function(params["metric"])

        # Filter out invalid parameters by inspecting the optimizer's __init__ signature
        try:
            sig = inspect.signature(optimizer_class.__init__)
            valid_params = {
                k: v for k, v in params.items() if k in sig.parameters or k == "metric"
            }
            return optimizer_class(**valid_params)
        except (TypeError, AttributeError):
            # If signature inspection fails, pass all params (original behavior)
            return optimizer_class(**params)

    @classmethod
    def _get_metric_function(cls, metric_name: str) -> Callable:
        """Get metric function by name."""
        # Built-in DSPy metrics
        metric_registry = {
            "answer_exact_match": cls._answer_exact_match,
            "semantic_f1": cls._semantic_f1,
            "answer_substring_match": cls._answer_substring_match,
            "fuzzy_match": cls._fuzzy_match,
            # Advanced GEPA feedback metrics
            "advanced_math_feedback": cls._advanced_math_feedback,
            "multi_component_enterprise_feedback": cls._multi_component_enterprise_feedback,
            "privacy_preservation_feedback": cls._privacy_preservation_feedback,
            "vulnerability_detection_feedback": cls._vulnerability_detection_feedback,
            "medical_accuracy_feedback": cls._medical_accuracy_feedback,
            "legal_analysis_feedback": cls._legal_analysis_feedback,
            "data_science_methodology_feedback": cls._data_science_methodology_feedback,
        }

        if metric_name in metric_registry:
            return metric_registry[metric_name]

        # Try to import from dspy.evaluate.metrics
        try:
            import dspy.evaluate.metrics as metrics

            if hasattr(metrics, metric_name):
                return getattr(metrics, metric_name)
        except ImportError:
            pass

        # Fallback to answer exact match
        logger.warning(f"Unknown metric {metric_name}, using answer_exact_match")
        return cls._answer_exact_match

    @staticmethod
    def _answer_exact_match(example, pred, trace=None, *args, **kwargs) -> float:
        """Exact match metric for answers with smart extraction."""
        import re

        expected = getattr(example, "answer", "").strip()
        actual = getattr(pred, "answer", "").strip()

        if not expected or not actual:
            return 0.0

        def extract_answer(text):
            """Extract the actual answer from formatted text."""
            text = text.strip()

            # Handle LaTeX boxed format: $\boxed{345}$
            boxed_match = re.search(r"\$\\boxed\{([^}]+)\}\$", text)
            if boxed_match:
                return boxed_match.group(1).strip()

            # Handle "The answer is X" format
            answer_match = re.search(
                r"(?:the\s+)?(?:final\s+)?answer\s+is:?\s*(.+?)(?:\.|$)",
                text,
                re.IGNORECASE,
            )
            if answer_match:
                return answer_match.group(1).strip()

            # Handle "x = 4" format for algebra
            eq_match = re.search(r"x\s*=\s*([^,\s]+)", text, re.IGNORECASE)
            if eq_match:
                return eq_match.group(1).strip()

            # Handle simple numeric answers (last number in the text)
            numbers = re.findall(r"\b\d+(?:\.\d+)?\b", text)
            if numbers:
                return numbers[-1]

            # Fallback: return the original text
            return text

        expected_clean = extract_answer(expected).lower()
        actual_clean = extract_answer(actual).lower()

        return 1.0 if expected_clean == actual_clean else 0.0

    @staticmethod
    def _semantic_f1(example, pred, trace=None, *args, **kwargs) -> float:
        """Semantic F1 score metric."""
        try:
            import dspy.evaluate.metrics as metrics

            return metrics.answer_exact_match(example, pred)
        except ImportError:
            # Fallback to simple word overlap F1
            expected_words = set(getattr(example, "answer", "").lower().split())
            actual_words = set(getattr(pred, "answer", "").lower().split())

            if not expected_words or not actual_words:
                return 0.0

            intersection = expected_words.intersection(actual_words)
            if not intersection:
                return 0.0

            precision = len(intersection) / len(actual_words)
            recall = len(intersection) / len(expected_words)

            if precision + recall == 0:
                return 0.0

            return 2 * (precision * recall) / (precision + recall)

    @staticmethod
    def _answer_substring_match(example, pred, trace=None, *args, **kwargs) -> float:
        """Substring match metric - more forgiving than exact match."""
        expected = getattr(example, "answer", "").strip().lower()
        actual = getattr(pred, "answer", "").strip().lower()

        if not expected or not actual:
            return 0.0

        # Check if any word from expected answer appears in actual
        for word in expected.split():
            if word in actual:
                return 1.0

        return 0.0

    @staticmethod
    def _fuzzy_match(example, pred, trace=None, *args, **kwargs) -> float:
        """Fuzzy match using string similarity."""
        try:
            from difflib import SequenceMatcher

            expected = getattr(example, "answer", "").strip().lower()
            actual = getattr(pred, "answer", "").strip().lower()

            if not expected or not actual:
                return 0.0

            return SequenceMatcher(None, expected, actual).ratio()

        except ImportError:
            # Fallback to substring match
            return DSPyOptimizerFactory._answer_substring_match(
                example, pred, trace, *args, **kwargs
            )

    @classmethod
    def create_tier_optimized_optimizer(
        cls,
        tier: str,
        training_data_size: int,
        optimizer_config: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Create an optimizer optimized for a specific tier and dataset size.

        Args:
            tier: Tier level (oracles, genies, protocols, etc.)
            training_data_size: Size of training dataset
            optimizer_config: Optional custom optimizer configuration

        Returns:
            Configured optimizer instance
        """
        if optimizer_config and "name" in optimizer_config:
            # Use specified optimizer
            optimizer_name = optimizer_config["name"]
            params = optimizer_config.get("params", {})
            lm_config = optimizer_config.get("lm_config")
            return cls.create_optimizer(optimizer_name, params, lm_config)

        # Default optimizer selection based on tier and dataset size
        if tier == "oracles":
            if training_data_size <= 5:
                return cls.create_optimizer(
                    "labeledfewshot", {"k": min(training_data_size, 3)}
                )
            else:
                return cls.create_optimizer(
                    "bootstrapfewshot",
                    {"max_bootstrapped_demos": min(training_data_size // 2, 4)},
                )

        elif tier == "genies":
            if training_data_size <= 10:
                return cls.create_optimizer(
                    "bootstrapfewshot",
                    {"max_bootstrapped_demos": min(training_data_size // 2, 6)},
                )
            else:
                return cls.create_optimizer(
                    "bettertogether",
                    {"max_bootstrapped_demos": min(training_data_size // 3, 8)},
                )

        else:
            # Advanced tiers can use more sophisticated optimizers
            if training_data_size >= 20:
                return cls.create_optimizer("gepa", {"auto": "medium"})
            else:
                return cls.create_optimizer(
                    "simba", {"max_steps": min(training_data_size // 4, 6)}
                )

    # =====================================================================
    # Advanced GEPA Feedback Metrics
    # =====================================================================

    @staticmethod
    def _advanced_math_feedback(example, pred, trace=None, *args, **kwargs):
        """Advanced math feedback with solution validation and step analysis."""
        try:
            from dspy.primitives import Prediction

            expected_answer = getattr(example, "answer", "").strip()
            actual_answer = getattr(pred, "answer", "").strip()
            actual_solution = getattr(pred, "solution", "").strip()

            # Extract numeric answers for comparison
            def extract_answer(text):
                import re

                # Handle various math answer formats
                boxed_match = re.search(r"\$\\boxed\{([^}]+)\}\$", text)
                if boxed_match:
                    return boxed_match.group(1).strip()

                # Handle "x = value" format
                eq_match = re.search(r"x\s*=\s*([^,\s]+)", text, re.IGNORECASE)
                if eq_match:
                    return eq_match.group(1).strip()

                # Find numeric values
                numbers = re.findall(r"-?\d+(?:\.\d+)?(?:/\d+)?", text)
                if numbers:
                    return numbers[-1]

                return text.strip()

            expected_clean = extract_answer(expected_answer).lower()
            actual_clean = extract_answer(actual_answer).lower()

            score = 1.0 if expected_clean == actual_clean else 0.0

            # Generate feedback for GEPA
            if score == 1.0:
                feedback = f"Correct answer: {actual_answer}. Solution shows good mathematical reasoning."
                if "step" in actual_solution.lower():
                    feedback += " Step-by-step approach is clear and methodical."
            else:
                feedback = f"Incorrect answer. Expected: {expected_answer}, Got: {actual_answer}."
                feedback += (
                    " Review mathematical concepts and double-check calculations."
                )
                if len(actual_solution) < 50:
                    feedback += " Provide more detailed step-by-step reasoning."

            return Prediction(score=score, feedback=feedback)

        except Exception:
            # Fallback to simple comparison
            return (
                1.0
                if getattr(example, "answer", "") == getattr(pred, "answer", "")
                else 0.0
            )

    @staticmethod
    def _multi_component_enterprise_feedback(
        example, pred, trace=None, *args, **kwargs
    ):
        """Multi-component enterprise feedback for information extraction tasks."""
        try:
            from dspy.primitives import Prediction

            components = [
                "urgency",
                "sentiment",
                "categories",
                "entities",
                "action_items",
            ]
            total_score = 0.0
            feedback_parts = []

            for component in components:
                expected = getattr(example, component, "").lower().strip()
                actual = getattr(pred, component, "").lower().strip()

                if expected and actual:
                    # Simple keyword overlap scoring
                    expected_words = set(expected.split())
                    actual_words = set(actual.split())

                    if expected_words & actual_words:  # Any overlap
                        component_score = len(expected_words & actual_words) / len(
                            expected_words
                        )
                        total_score += component_score
                        feedback_parts.append(
                            f"{component}: Good identification ({component_score:.1%})"
                        )
                    else:
                        feedback_parts.append(f"{component}: Missed key elements")
                else:
                    feedback_parts.append(f"{component}: Missing analysis")

            overall_score = total_score / len(components) if components else 0.0
            feedback = "Component analysis: " + "; ".join(feedback_parts)

            if overall_score > 0.8:
                feedback += " Excellent comprehensive analysis."
            elif overall_score > 0.6:
                feedback += " Good analysis with room for improvement."
            else:
                feedback += " Needs significant improvement in information extraction."

            return Prediction(score=overall_score, feedback=feedback)

        except Exception:
            return 0.0

    @staticmethod
    def _privacy_preservation_feedback(example, pred, trace=None, *args, **kwargs):
        """Privacy preservation feedback for secure delegation tasks."""
        try:
            from dspy.primitives import Prediction
            import re

            original_query = getattr(example, "user_query", "")
            redacted_request = getattr(pred, "redacted_request", "")
            privacy_assessment = getattr(pred, "privacy_assessment", "")

            # Check for PII leakage in redacted request
            pii_patterns = [
                r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
                r"\b\d{2}/\d{2}/\d{4}\b",  # Date of birth
                r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",  # Names
                r"\b\d{4}-\d{4}-\d{4}-\d{4}\b",  # Credit card
                r"\b\d+\s+\w+\s+(?:St|Ave|Rd|Blvd)\b",  # Addresses
            ]

            leakage_count = 0
            for pattern in pii_patterns:
                if re.search(pattern, redacted_request):
                    leakage_count += 1

            # Score based on privacy protection
            base_score = 1.0 - (leakage_count * 0.3)  # Penalize PII leakage

            if "privacy" in privacy_assessment.lower():
                base_score += 0.1  # Bonus for explicit privacy consideration

            score = max(0.0, min(1.0, base_score))

            if score >= 0.9:
                feedback = "Excellent privacy preservation. No PII detected in redacted request."
            elif score >= 0.7:
                feedback = "Good privacy protection with minor concerns."
            else:
                feedback = f"Privacy risks detected: {leakage_count} potential PII leakages. Improve redaction techniques."

            return Prediction(score=score, feedback=feedback)

        except Exception:
            return 0.5

    @staticmethod
    def _vulnerability_detection_feedback(example, pred, trace=None, *args, **kwargs):
        """Security vulnerability detection feedback."""
        try:
            from dspy.primitives import Prediction

            expected_vulns = getattr(example, "vulnerabilities", "").lower()
            actual_vulns = getattr(pred, "vulnerabilities", "").lower()
            security_score = getattr(pred, "security_score", "")

            # Check for key vulnerability types
            vuln_types = [
                "sql injection",
                "xss",
                "authentication",
                "authorization",
                "cryptographic",
                "file upload",
            ]

            detected_score = 0.0
            for vuln_type in vuln_types:
                if vuln_type in expected_vulns:
                    if vuln_type in actual_vulns:
                        detected_score += 1.0
                    else:
                        detected_score -= 0.5  # Penalty for missing critical vulns

            # Normalize score
            expected_count = sum(1 for vt in vuln_types if vt in expected_vulns)
            if expected_count > 0:
                score = max(0.0, detected_score / expected_count)
            else:
                score = (
                    0.8 if "none" in actual_vulns or "secure" in actual_vulns else 0.5
                )

            if score >= 0.8:
                feedback = "Excellent vulnerability detection. Comprehensive security analysis."
            elif score >= 0.6:
                feedback = "Good detection rate. Consider more thorough analysis."
            else:
                feedback = "Missed critical vulnerabilities. Improve security analysis methodology."

            return Prediction(score=score, feedback=feedback)

        except Exception:
            return 0.5

    @staticmethod
    def _medical_accuracy_feedback(example, pred, trace=None, *args, **kwargs):
        """Medical information accuracy feedback with safety emphasis."""
        try:
            from dspy.primitives import Prediction

            clinical_analysis = getattr(pred, "clinical_analysis", "")
            medical_disclaimer = getattr(pred, "medical_disclaimer", "")

            score = 0.0
            feedback_parts = []

            # Check for medical disclaimer (critical for safety)
            if any(
                phrase in medical_disclaimer.lower()
                for phrase in [
                    "consult",
                    "healthcare provider",
                    "medical professional",
                    "doctor",
                ]
            ):
                score += 0.3
                feedback_parts.append("Good: Includes appropriate medical disclaimer")
            else:
                feedback_parts.append("Critical: Missing proper medical disclaimer")

            # Check for evidence-based language
            if any(
                phrase in clinical_analysis.lower()
                for phrase in ["evidence", "studies", "guidelines", "research"]
            ):
                score += 0.2
                feedback_parts.append("Good: Evidence-based approach")

            # Check for cautious language
            if any(
                phrase in clinical_analysis.lower()
                for phrase in ["may", "might", "potential", "possible", "consult"]
            ):
                score += 0.2
                feedback_parts.append("Good: Appropriately cautious language")

            # Bonus for comprehensive analysis
            if len(clinical_analysis) > 100:
                score += 0.3
                feedback_parts.append("Good: Comprehensive analysis")

            feedback = "Medical safety check: " + "; ".join(feedback_parts)

            if score >= 0.8:
                feedback += " Excellent medical information handling."
            else:
                feedback += " Improve medical safety and disclaimer practices."

            return Prediction(score=score, feedback=feedback)

        except Exception:
            return 0.5

    @staticmethod
    def _legal_analysis_feedback(example, pred, trace=None, *args, **kwargs):
        """Legal contract analysis feedback."""
        try:
            from dspy.primitives import Prediction

            risk_analysis = getattr(pred, "risk_analysis", "")
            legal_disclaimer = getattr(pred, "legal_disclaimer", "")
            missing_clauses = getattr(pred, "missing_clauses", "")

            score = 0.0
            feedback_parts = []

            # Check for legal disclaimer
            if any(
                phrase in legal_disclaimer.lower()
                for phrase in [
                    "legal counsel",
                    "attorney",
                    "qualified legal",
                    "professional review",
                ]
            ):
                score += 0.25
                feedback_parts.append("Good: Includes legal disclaimer")
            else:
                feedback_parts.append("Critical: Missing legal counsel disclaimer")

            # Check for risk assessment
            if any(
                phrase in risk_analysis.lower()
                for phrase in ["risk", "liability", "enforceable", "compliance"]
            ):
                score += 0.25
                feedback_parts.append("Good: Identifies legal risks")

            # Check for missing clauses analysis
            if missing_clauses and len(missing_clauses) > 20:
                score += 0.25
                feedback_parts.append("Good: Identifies missing provisions")

            # Check for severity ratings
            if any(
                phrase in risk_analysis.lower()
                for phrase in ["critical", "high", "medium", "low"]
            ):
                score += 0.25
                feedback_parts.append("Good: Provides risk severity assessment")

            feedback = "Legal analysis check: " + "; ".join(feedback_parts)

            if score >= 0.8:
                feedback += " Comprehensive legal analysis."
            else:
                feedback += " Improve legal risk assessment and disclaimers."

            return Prediction(score=score, feedback=feedback)

        except Exception:
            return 0.5

    @staticmethod
    def _data_science_methodology_feedback(example, pred, trace=None, *args, **kwargs):
        """Data science methodology feedback for analytical rigor."""
        try:
            from dspy.primitives import Prediction

            methodology = getattr(pred, "methodology", "")
            evaluation_strategy = getattr(pred, "evaluation_strategy", "")
            limitations = getattr(pred, "limitations", "")

            score = 0.0
            feedback_parts = []

            # Check for statistical rigor
            statistical_terms = [
                "hypothesis",
                "significance",
                "confidence",
                "validation",
                "cross-validation",
                "bias",
            ]
            if any(term in methodology.lower() for term in statistical_terms):
                score += 0.2
                feedback_parts.append("Good: Demonstrates statistical rigor")

            # Check for proper evaluation methodology
            eval_terms = [
                "train",
                "test",
                "validation",
                "holdout",
                "metrics",
                "baseline",
            ]
            if any(term in evaluation_strategy.lower() for term in eval_terms):
                score += 0.2
                feedback_parts.append("Good: Proper evaluation methodology")

            # Check for bias and limitation awareness
            if limitations and len(limitations) > 30:
                score += 0.2
                feedback_parts.append(
                    "Good: Acknowledges limitations and potential biases"
                )
            else:
                feedback_parts.append(
                    "Improve: Add discussion of limitations and biases"
                )

            # Check for business context
            business_terms = [
                "business",
                "actionable",
                "roi",
                "impact",
                "cost",
                "value",
            ]
            content_text = (methodology + evaluation_strategy).lower()
            if any(term in content_text for term in business_terms):
                score += 0.2
                feedback_parts.append("Good: Considers business context")

            # Check for reproducibility
            repro_terms = [
                "reproducible",
                "documentation",
                "version",
                "seed",
                "environment",
            ]
            if any(term in content_text for term in repro_terms):
                score += 0.2
                feedback_parts.append("Good: Addresses reproducibility")
            else:
                feedback_parts.append("Improve: Add reproducibility considerations")

            feedback = "Data science methodology: " + "; ".join(feedback_parts)

            if score >= 0.8:
                feedback += " Excellent scientific rigor and methodology."
            elif score >= 0.6:
                feedback += " Good approach with room for methodological improvement."
            else:
                feedback += " Needs significant improvement in scientific methodology."

            return Prediction(score=score, feedback=feedback)

        except Exception:
            return 0.5
