"""
Universal GEPA Optimizer for SuperOptiX Multi-Framework Support.

This module implements a framework-agnostic GEPA optimizer that works with
BaseComponent instances from any framework (DSPy, Microsoft, OpenAI, CrewAI, Google ADK, Pydantic AI, etc.).

Key Architecture:
- Wraps BaseComponent instances with GEPA optimization
- Uses the BaseComponent.variable property as the optimizable prompt/instruction
- Works across all frameworks via the BaseComponent interface
- Provides the same GEPA optimization benefits to all frameworks

Supported Frameworks:
- DSPy
- Microsoft Agent Framework
- OpenAI Agents SDK
- DeepAgents (LangGraph-based)
- CrewAI
- Google ADK
- Pydantic AI

Author: SuperOptiX Team
Version: 0.2.0-dev (Week 3)
"""

import logging
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Protocol, Union

from gepa import GEPAResult, optimize
from gepa.core.adapter import GEPAAdapter, EvaluationBatch

from superoptix.core.base_component import BaseComponent

logger = logging.getLogger(__name__)


# ==============================================================================
# 1. Scoring and Feedback Protocols
# ==============================================================================


class ScoreWithFeedback(Protocol):
    """Score with optional textual feedback."""

    score: float
    feedback: Optional[str]


class UniversalGEPAMetric(Protocol):
    """
    Metric function for Universal GEPA optimizer.

    This function evaluates a component's output and provides feedback.

    Args:
        inputs: Input data provided to the component
        outputs: Output data from the component
        gold: Expected/gold standard output
        component_name: Optional name of component being optimized

    Returns:
        float score or dict with 'score' and 'feedback' fields
    """

    def __call__(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        gold: Dict[str, Any],
        component_name: Optional[str] = None,
    ) -> Union[float, ScoreWithFeedback]: ...


# ==============================================================================
# 2. BaseComponent Adapter for GEPA
# ==============================================================================


class BaseComponentAdapter(GEPAAdapter):
    """
    Adapter that connects GEPA optimizer with BaseComponent instances.

    This adapter allows GEPA to optimize any BaseComponent, regardless of
    the underlying framework (DSPy, Microsoft, OpenAI, CrewAI, Google ADK, etc.).

    Implements the GEPAAdapter interface:
    - evaluate(): Run component on batch and return scores
    - make_reflective_dataset(): Build dataset for reflection
    """

    def __init__(
        self,
        component: BaseComponent,
        metric_fn: UniversalGEPAMetric,
        failure_score: float = 0.0,
        rng: Optional[random.Random] = None,
    ):
        """
        Initialize the BaseComponent adapter.

        Args:
            component: The BaseComponent instance to optimize
            metric_fn: Metric function for evaluation
            failure_score: Score to assign on failures
            rng: Random number generator for reproducibility
        """
        self.component = component
        self.metric_fn = metric_fn
        self.failure_score = failure_score
        self.rng = rng or random.Random(0)

        # Extract component info
        self.component_name = component.name
        self.framework = component.framework

    def evaluate(
        self,
        batch: List[Dict[str, Any]],
        candidate: Dict[str, str],
        capture_traces: bool = False,
    ) -> EvaluationBatch:
        """
        Evaluate a candidate on a batch of examples.

        Args:
            batch: List of examples (DataInst format)
            candidate: Dict mapping component names to their variables
            capture_traces: Whether to capture execution traces

        Returns:
            EvaluationBatch with outputs, scores, and optional trajectories
        """
        # Update component with candidate variable
        component_var = candidate.get(self.component_name, self.component.variable)
        self.component.update(component_var)

        outputs = []
        scores = []
        trajectories = [] if capture_traces else None

        for example in batch:
            try:
                # Extract inputs and gold outputs
                inputs = example.get("inputs", {})
                gold = example.get("outputs", {})

                # Execute component (handle both sync and async)
                import inspect

                if inspect.iscoroutinefunction(self.component.forward):
                    # Async component - need to run in event loop
                    import asyncio

                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # If loop is running, create a task
                            import concurrent.futures

                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                future = executor.submit(
                                    asyncio.run, self.component.forward(**inputs)
                                )
                                output = future.result()
                        else:
                            output = loop.run_until_complete(
                                self.component.forward(**inputs)
                            )
                    except RuntimeError:
                        # No event loop, create one
                        output = asyncio.run(self.component.forward(**inputs))
                else:
                    # Sync component
                    output = self.component.forward(**inputs)
                outputs.append(output)

                # Score the output
                score_result = self.metric_fn(inputs, output, gold, self.component_name)

                # Extract score from ScoreWithFeedback if needed
                if isinstance(score_result, dict) and "score" in score_result:
                    score = score_result["score"]
                    feedback = score_result.get("feedback", f"Score: {score}")
                else:
                    score = float(score_result)
                    feedback = f"Score: {score}"

                scores.append(float(score))

                # Capture trajectory if requested
                if capture_traces:
                    trajectory = {
                        "inputs": inputs,
                        "outputs": output,
                        "gold": gold,
                        "score": score,
                        "feedback": feedback,
                        "component": self.component_name,
                    }
                    trajectories.append(trajectory)

            except Exception as e:
                logger.warning(
                    f"Component {self.component_name} failed on example: {e}"
                )
                outputs.append({"error": str(e)})
                scores.append(self.failure_score)

                if capture_traces:
                    trajectories.append(
                        {
                            "inputs": example.get("inputs", {}),
                            "outputs": {"error": str(e)},
                            "gold": example.get("outputs", {}),
                            "score": self.failure_score,
                            "feedback": f"Execution failed: {str(e)}",
                            "component": self.component_name,
                        }
                    )

        return EvaluationBatch(
            outputs=outputs,
            scores=scores,
            trajectories=trajectories,
        )

    def make_reflective_dataset(
        self,
        candidate: Dict[str, str],
        eval_batch: EvaluationBatch,
        components_to_update: List[str],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Build reflective dataset for instruction refinement.

        Args:
            candidate: The candidate that was evaluated
            eval_batch: Results from evaluate() with capture_traces=True
            components_to_update: Component names to build datasets for

        Returns:
            Dict mapping component names to lists of reflective examples
        """
        reflective_dataset = {}

        for component_name in components_to_update:
            if component_name != self.component_name:
                continue

            component_examples = []

            # Build reflective examples from trajectories
            if eval_batch.trajectories:
                for traj in eval_batch.trajectories:
                    # Format example for reflection
                    example = {
                        "Inputs": traj.get("inputs", {}),
                        "Generated Outputs": traj.get("outputs", {}),
                        "Feedback": traj.get("feedback", ""),
                        "Score": traj.get("score", 0.0),
                    }
                    component_examples.append(example)

            reflective_dataset[component_name] = component_examples

        return reflective_dataset


# ==============================================================================
# 3. Universal GEPA Optimizer
# ==============================================================================


@dataclass
class UniversalGEPAResult:
    """
    Results from Universal GEPA optimization.

    Fields:
    - optimized_component: The optimized BaseComponent
    - best_variable: The best optimized variable (prompt/instruction)
    - best_score: The best score achieved
    - all_scores: All scores from optimization
    - num_iterations: Number of optimization iterations
    - framework: Framework of the optimized component
    """

    optimized_component: BaseComponent
    best_variable: str
    best_score: float
    all_scores: List[float]
    num_iterations: int
    framework: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "best_variable": self.best_variable,
            "best_score": self.best_score,
            "all_scores": self.all_scores,
            "num_iterations": self.num_iterations,
            "framework": self.framework,
            "component_name": self.optimized_component.name,
        }


class UniversalGEPA:
    """
    Universal GEPA Optimizer for all SuperOptiX frameworks.

    This optimizer works with any BaseComponent instance, enabling GEPA
    optimization across DSPy, Microsoft, OpenAI, CrewAI, Google ADK, and more.

    Example:
        ```python
        # Works with ANY framework!
        from superoptix.optimizers.universal_gepa import UniversalGEPA

        # Create component (Microsoft, OpenAI, CrewAI, Google ADK, etc.)
        component = MyAgentComponent(...)

        # Define metric
        def metric(inputs, outputs, gold, component_name=None):
            # Your evaluation logic
            return score  # or {"score": score, "feedback": "..."}

        # Optimize!
        optimizer = UniversalGEPA(
            metric=metric,
            auto="light",  # or "medium", "heavy"
            reflection_lm="gpt-4o",  # for reflection
        )

        result = optimizer.compile(
            component=component,
            trainset=train_examples,
            valset=val_examples,
        )

        print(f"Optimized {result.framework} component!")
        print(f"Best score: {result.best_score}")
        ```

    Args:
        metric: Metric function for evaluation
        auto: Auto budget ("light", "medium", "heavy")
        max_full_evals: Maximum full evaluations
        max_metric_calls: Maximum metric calls
        reflection_lm: LM for reflection (model name or LM instance)
        reflection_minibatch_size: Minibatch size for reflection
        candidate_selection_strategy: "pareto" or "current_best"
        skip_perfect_score: Skip examples with perfect scores
        use_merge: Enable merge-based optimization
        max_merge_invocations: Max merge attempts
        failure_score: Score for failed examples
        perfect_score: Perfect score value
        log_dir: Directory for logs
        track_stats: Track detailed statistics
        seed: Random seed for reproducibility
    """

    def __init__(
        self,
        metric: UniversalGEPAMetric,
        *,
        # Budget configuration
        auto: Literal["light", "medium", "heavy"] | None = None,
        max_full_evals: int | None = None,
        max_metric_calls: int | None = None,
        # Reflection configuration
        reflection_lm: str | Any = None,  # Can be model name or LM instance
        reflection_minibatch_size: int = 3,
        candidate_selection_strategy: Literal["pareto", "current_best"] = "pareto",
        skip_perfect_score: bool = True,
        # Merge configuration
        use_merge: bool = True,
        max_merge_invocations: int | None = 5,
        # Evaluation configuration
        failure_score: float = 0.0,
        perfect_score: float = 1.0,
        # Logging
        log_dir: str = None,
        track_stats: bool = False,
        display_progress: bool = True,
        # Reproducibility
        seed: int | None = 0,
    ):
        """Initialize Universal GEPA optimizer."""

        # Validate budget configuration
        assert (max_metric_calls is not None) + (max_full_evals is not None) + (
            auto is not None
        ) == 1, (
            "Exactly one of max_metric_calls, max_full_evals, auto must be set. "
            f"You set max_metric_calls={max_metric_calls}, "
            f"max_full_evals={max_full_evals}, "
            f"auto={auto}."
        )

        self.metric_fn = metric
        self.auto = auto
        self.max_full_evals = max_full_evals
        self.max_metric_calls = max_metric_calls

        # Reflection configuration
        self.reflection_lm = reflection_lm
        self.reflection_minibatch_size = reflection_minibatch_size
        self.candidate_selection_strategy = candidate_selection_strategy
        self.skip_perfect_score = skip_perfect_score

        # Merge configuration
        self.use_merge = use_merge
        self.max_merge_invocations = max_merge_invocations

        # Evaluation configuration
        self.failure_score = failure_score
        self.perfect_score = perfect_score

        # Logging
        self.log_dir = log_dir
        self.track_stats = track_stats
        self.display_progress = display_progress

        # Reproducibility
        self.seed = seed

    def compile(
        self,
        component: BaseComponent,
        *,
        trainset: List[Dict[str, Any]],
        valset: Optional[List[Dict[str, Any]]] = None,
    ) -> UniversalGEPAResult:
        """
        Optimize a BaseComponent using GEPA.

        Args:
            component: BaseComponent instance to optimize (any framework)
            trainset: Training examples for optimization
                Format: [{"inputs": {...}, "outputs": {...}}, ...]
            valset: Validation examples (optional, uses trainset if not provided)

        Returns:
            UniversalGEPAResult with optimized component and statistics
        """
        assert trainset is not None and len(trainset) > 0, (
            "Trainset must be provided and non-empty"
        )

        logger.info(
            f"🚀 Starting Universal GEPA optimization for {component.framework} component: {component.name}"
        )

        # Use trainset as valset if not provided
        if valset is None:
            logger.warning(
                "No valset provided; using trainset as valset. "
                "For better generalization, provide separate train and val sets."
            )
            valset = trainset

        # Calculate budget
        if self.auto is not None:
            auto_settings = {"light": 6, "medium": 12, "heavy": 18}
            num_candidates = auto_settings[self.auto]
            self.max_metric_calls = self._auto_budget(
                num_components=1,  # Single component optimization
                num_candidates=num_candidates,
                valset_size=len(valset),
            )
        elif self.max_full_evals is not None:
            self.max_metric_calls = self.max_full_evals * (len(trainset) + len(valset))

        logger.info(
            f"📊 Budget: ~{self.max_metric_calls} metric calls "
            f"({self.max_metric_calls / (len(trainset) + len(valset)):.1f} full evals)"
        )

        # Create RNG
        rng = random.Random(self.seed)

        # Create adapter
        adapter = BaseComponentAdapter(
            component=component,
            metric_fn=self.metric_fn,
            failure_score=self.failure_score,
            rng=rng,
        )

        # Create base candidate with current variable
        base_candidate = {component.name: component.variable}

        # Create reflection LM wrapper if string model name provided
        reflection_lm_fn = None
        if self.reflection_lm is not None:
            if isinstance(self.reflection_lm, str):
                # Import here to avoid circular dependency
                try:
                    import dspy

                    # Convert ollama:model_name to ollama_chat/model_name for LiteLLM
                    model_name = self.reflection_lm
                    api_base = None
                    api_key = ""

                    # Detect Ollama models without prefix
                    # Check if model string lacks a known provider prefix
                    known_providers = [
                        "ollama",
                        "openai",
                        "anthropic",
                        "google",
                        "bedrock",
                        "azure",
                        "cohere",
                        "mistral",
                        "deepseek",
                        "groq",
                        "together",
                        "fireworks",
                        "litellm",
                        "gateway",
                    ]
                    has_provider_prefix = any(
                        model_name.startswith(f"{p}:") for p in known_providers
                    )

                    # If no prefix and model contains ':' (like llama3.1:8b), assume Ollama
                    if not has_provider_prefix and ":" in model_name:
                        # Check if it looks like an Ollama model (has version suffix like :8b, :7b, etc.)
                        # or if it's a common Ollama model name
                        ollama_indicators = [
                            ":8b",
                            ":7b",
                            ":13b",
                            ":70b",
                            "llama",
                            "mistral",
                            "codellama",
                            "phi",
                            "gemma",
                            "qwen",
                        ]
                        if any(
                            indicator in model_name.lower()
                            for indicator in ollama_indicators
                        ):
                            model_name = f"ollama:{model_name}"

                    if model_name.startswith("ollama:"):
                        # Convert "ollama:llama3.1:8b" to "ollama_chat/llama3.1:8b"
                        model_name = model_name.replace("ollama:", "ollama_chat/")
                        api_base = "http://localhost:11434"
                        api_key = ""

                    lm = dspy.LM(
                        model=model_name,
                        temperature=1.0,
                        max_tokens=32000,
                        api_base=api_base,
                        api_key=api_key,
                    )

                    def reflection_lm_fn(x):
                        return lm(x)[0]
                except ImportError:
                    logger.warning(
                        "DSPy not available. Reflection LM string model names require DSPy. "
                        "Please install DSPy or provide an LM instance."
                    )
                    reflection_lm_fn = None
            else:
                # Assume it's already an LM instance
                def reflection_lm_fn(x):
                    return self.reflection_lm(x)[0]

        # Run GEPA optimization
        logger.info(f"🔧 Running GEPA optimization...")
        gepa_result: GEPAResult = optimize(
            seed_candidate=base_candidate,
            trainset=trainset,
            valset=valset,
            adapter=adapter,
            # Reflection configuration
            reflection_lm=reflection_lm_fn,
            candidate_selection_strategy=self.candidate_selection_strategy,
            skip_perfect_score=self.skip_perfect_score,
            reflection_minibatch_size=self.reflection_minibatch_size,
            perfect_score=self.perfect_score,
            # Merge configuration
            use_merge=self.use_merge,
            max_merge_invocations=self.max_merge_invocations,
            # Budget
            max_metric_calls=self.max_metric_calls,
            # Logging
            run_dir=self.log_dir,  # GEPA uses 'run_dir' not 'log_dir'
            display_progress_bar=self.display_progress,
            # Reproducibility
            seed=self.seed,
        )

        # Extract best candidate
        best_idx = gepa_result.best_idx
        best_candidate = gepa_result.candidates[best_idx]
        best_variable = best_candidate.get(component.name, component.variable)
        best_score = gepa_result.val_aggregate_scores[best_idx]

        # Update component with best variable
        component.update(best_variable)

        logger.info(
            f"✅ Optimization complete! Best score: {best_score:.3f} "
            f"(from {len(gepa_result.candidates)} candidates)"
        )

        # Return result
        return UniversalGEPAResult(
            optimized_component=component,
            best_variable=best_variable,
            best_score=best_score,
            all_scores=gepa_result.val_aggregate_scores,
            num_iterations=len(gepa_result.candidates),
            framework=component.framework,
        )

    def _auto_budget(
        self, num_components: int, num_candidates: int, valset_size: int
    ) -> int:
        """Calculate automatic budget based on components and candidates."""
        import numpy as np

        num_trials = int(
            max(
                2 * (num_components * 2) * np.log2(num_candidates), 1.5 * num_candidates
            )
        )
        V = valset_size
        N = num_trials
        M = self.reflection_minibatch_size
        m = 5  # full_eval_steps

        # Initial full evaluation
        total = V

        # Bootstrapping
        total += num_candidates * 5

        # Minibatch evaluations
        total += N * M

        # Periodic full evaluations
        if N > 0:
            periodic_fulls = (N + 1) // m + 1
            extra_final = 1 if N < m else 0
            total += (periodic_fulls + extra_final) * V

        return total
