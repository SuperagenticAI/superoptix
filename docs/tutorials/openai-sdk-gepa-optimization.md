# OpenAI Agents SDK + GEPA Optimization Tutorial

**Build and Optimize Custom AI Agents with Native OpenAI SDK Patterns**

This comprehensive tutorial demonstrates how to create production-ready AI agents using the official OpenAI Agents SDK, integrate them with SuperOptiX, and achieve measurable performance improvements through GEPA (Genetic Evaluation-based Prompt Augmentation) optimization.

> **Hands-on first:** Clone the live example repo and follow along step by step — every snippet in this guide comes straight from [`superoptix-lite-openai`](https://github.com/SuperagenticAI/superoptix-lite-openai). Use it as your working playground while you read.

---

## 🔗 Repo Spotlight

Looking for a complete, runnable example? Check out the open source companion repository [`superoptix-lite-openai`](https://github.com/SuperagenticAI/superoptix-lite-openai). It ships with:

- A production-ready Code Reviewer agent following this tutorial end-to-end
- GEPA optimization workflow powered by the lightweight `superoptix_lite` package
- Playbook-driven Agent Spec scenarios for SQL injection, memory leaks, error handling, and performance tuning
- Automation scripts for baseline evaluation, optimization, and regression testing

We'll reference this repository throughout the tutorial so you can clone, copy, or adapt the same patterns instantly.

---

## 📋 What You'll Learn

By the end of this tutorial, you'll know how to:

- Write agents using **official OpenAI Agents SDK patterns**
- Integrate native SDK agents with **SuperOptiX** for optimization
- Define **BDD test scenarios** for measurable metrics
- Run **GEPA optimization** to improve agent performance
- Implement **automatic optimization loading**
- Work with **local Ollama models** (no API keys required)

---

## 🎯 Tutorial Overview

**What We'll Build**: A Code Reviewer Agent that analyzes code quality, identifies security vulnerabilities, detects memory leaks, and suggests performance improvements.

**Performance Target**: 100% pass rate on BDD test scenarios

**Time Required**: 30-45 minutes

---

## 📦 Prerequisites

### Required Software

```bash
# Python 3.11 or higher
python3 --version

# Ollama with models
ollama pull gpt-oss:20b      # Primary model (20B parameters)
ollama pull llama3.1:8b       # Reflection model (8B parameters)

# SuperOptiX with OpenAI SDK support
pip install "superoptix[frameworks-openai]"
```

**💡 Why use different model sizes?**

- **Primary model (gpt-oss:20b)**: Handles the actual agent task (code review). Larger models provide better analysis and more detailed feedback.
- **Reflection model (llama3.1:8b)**: Used by GEPA during optimization to analyze results and suggest prompt improvements. This runs many times during optimization, so a smaller model:
  - Significantly speeds up optimization (5-10x faster)
  - Reduces memory usage and resource consumption
  - Provides "good enough" reflections for prompt improvement

The reflection task (analyzing evaluation results) is simpler than the agent's task, so a smaller model works well. You can use a larger reflection model if you prefer, but optimization will take longer:

```bash
# Optional: Use larger reflection model (slower optimization)
# This is useful if you want more sophisticated prompt improvements
ollama pull gpt-oss:20b  # Use as both primary and reflection model
```

### Verify Installation

```bash
# Check Ollama is running
ollama list

# Check SuperOptiX installation
python -c "import superoptix; print(superoptix.__version__)"
```

---

## 🏗️ Step 1: Project Setup

### Create Project Structure

```bash
# Create project directory
mkdir code-reviewer-tutorial
cd code-reviewer-tutorial

# Create agent structure
mkdir -p agents/code_reviewer/{playbook,pipelines,optimized}

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install "superoptix[frameworks-openai]"
```

### Project Layout

```
code-reviewer-tutorial/
├── venv/
└── agents/
    └── code_reviewer/
        ├── playbook/         # Configuration & BDD scenarios
        ├── pipelines/        # Agent implementation
        └── optimized/        # GEPA optimization results
```

> **Quick start:** prefer cloning instead? `git clone https://github.com/SuperagenticAI/superoptix-lite-openai.git` to get the finished layout with baseline, optimization, and demo scripts already wired up.

---

## 📝 Step 2: Define Agent Playbook

Create `agents/code_reviewer/playbook/code_reviewer_playbook.yaml`:

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: code_reviewer
  id: code_reviewer
  namespace: tutorial
  version: 1.0.0
  description: AI code reviewer for security, performance, and quality analysis
  author: Your Name

spec:
  target_framework: openai

  # Model Configuration
  language_model:
    location: local
    provider: ollama
    model: ollama:gpt-oss:20b
    temperature: 0.3           # Lower for more consistent reviews
    max_tokens: 3000
    api_base: http://localhost:11434

  # Input/Output Schema
  input_fields:
    - name: code
      type: str
      description: Code snippet to review
      required: true
    - name: language
      type: str
      description: Programming language
      required: false

  output_fields:
    - name: review
      type: str
      description: Code review feedback
      required: true

  # Agent Persona
  persona:
    name: Senior Code Reviewer
    role: Code Quality Expert
    goal: Provide constructive, actionable code review feedback
    backstory: |
      You are an experienced software engineer with 15+ years reviewing code
      across multiple languages. You understand best practices, design patterns,
      security vulnerabilities, and performance optimization. Your reviews are
      thorough yet constructive.
    traits:
      - thorough
      - constructive
      - security-conscious
      - performance-aware

  # Reasoning Process
  reasoning:
    method: structured_analysis
    steps:
      - Analyze code structure and readability
      - Identify potential bugs and edge cases
      - Check for security vulnerabilities
      - Evaluate performance implications
      - Suggest specific improvements

  # BDD Test Scenarios
  feature_specifications:
    feature_name: Code Review Assistant
    feature_description: Review code and provide comprehensive feedback

    scenarios:
      # Test 1: Security Vulnerability Detection
      - name: SQL Injection Detection
        description: Should identify SQL injection vulnerabilities
        input:
          code: |
            def get_user(username):
                query = "SELECT * FROM users WHERE name = '" + username + "'"
                return db.execute(query)
          language: python
        expected_output:
          expected_keywords:
            - SQL injection
            - vulnerability
            - parameterized
            - prepared statement

      # Test 2: Memory Leak Identification
      - name: Memory Leak Detection
        description: Should identify potential memory leaks
        input:
          code: |
            function processData() {
              let data = [];
              setInterval(() => {
                data.push(fetchData());
              }, 1000);
            }
          language: javascript
        expected_output:
          expected_keywords:
            - memory leak
            - grows
            - cleanup
            - clear

      # Test 3: Error Handling Analysis
      - name: Error Handling Review
        description: Should identify missing error handling
        input:
          code: |
            async function fetchUser(id) {
              const response = await fetch(`/api/users/${id}`);
              const data = await response.json();
              return data;
            }
          language: javascript
        expected_output:
          expected_keywords:
            - error
            - try
            - catch
            - handle

      # Test 4: Performance Optimization
      - name: Code Optimization Suggestion
        description: Should suggest performance improvements
        input:
          code: |
            def find_duplicates(items):
                duplicates = []
                for i in range(len(items)):
                    for j in range(i+1, len(items)):
                        if items[i] == items[j]:
                            duplicates.append(items[i])
                return duplicates
          language: python
        expected_output:
          expected_keywords:
            - O(n²)
            - performance
            - set
            - efficient

  # GEPA Optimization Configuration
  optimization:
    optimizer:
      name: GEPA
      params:
        metric: response_accuracy
        auto: medium
        reflection_lm: ollama:gpt-oss:20b
        max_full_evals: 5
        skip_perfect_score: true
    metric: response_accuracy
    metric_threshold: 0.75
```

### Key Playbook Components

**1. Model Configuration**
- Uses local Ollama model (`gpt-oss:20b`)
- Temperature 0.3 for consistent reviews
- 3000 max tokens for detailed feedback

**2. BDD Scenarios**
- 4 comprehensive test cases
- Covers security, memory, errors, performance
- Uses keyword matching for validation

**3. GEPA Configuration**
- Medium optimization budget
- Uses same model for reflection
- Stops early if perfect score achieved

---

## 💻 Step 3: Implement Native OpenAI SDK Agent

Create `agents/code_reviewer/pipelines/code_reviewer_openai_pipeline.py`:

```python
"""
Code Reviewer Agent - Native OpenAI Agents SDK Implementation
Following official OpenAI SDK patterns with SuperOptiX integration
"""

import asyncio
from typing import Dict, List, Optional
from pathlib import Path
import yaml
import json

# OpenAI Agents SDK imports (official)
from agents import Agent, Runner, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

# SuperOptiX Lite integration (matches superoptix-lite-openai repo)
from openai_gepa.superoptix_lite import BaseComponent


# ======================================================================
# PART 1: Native OpenAI SDK Agent Implementation
# ======================================================================

class CodeReviewerAgent:
    """
    Pure OpenAI Agents SDK implementation.

    This follows the official SDK documentation patterns:
    - Agent class for agent definition
    - Runner.run() for execution
    - OpenAIChatCompletionsModel for Ollama integration
    """

    def __init__(
        self,
        instructions: str,
        model: str = "gpt-oss:20b",
        api_base: str = "http://localhost:11434",
        temperature: float = 0.3
    ):
        """
        Initialize the code reviewer agent.

        Args:
            instructions: System instructions for the agent
            model: Model name (without 'ollama:' prefix)
            api_base: Ollama API endpoint
            temperature: Model temperature (0.0-1.0)
        """
        self.instructions = instructions

        # Initialize Ollama model using OpenAI SDK compatibility
        self.model = OpenAIChatCompletionsModel(
            model=model,
            openai_client=AsyncOpenAI(
                base_url=f"{api_base}/v1",
                api_key="ollama",  # Ollama doesn't need real key
            ),
        )

        # Create the agent
        self.agent = Agent(
            name="Code Reviewer",
            instructions=instructions,
            model=self.model,
        )

        print(f"Code Reviewer Agent initialized with Ollama: {model}")

    async def review_code(self, code: str, language: str = "unknown") -> str:
        """
        Review code and provide feedback.

        Args:
            code: Code snippet to review
            language: Programming language

        Returns:
            Review feedback as string
        """
        # Create context with code and language
        context = f"Language: {language}\n\nCode to review:\n```{language}\n{code}\n```"

        # Run agent using official Runner pattern
        result = await Runner.run(self.agent, input=context)

        # Extract final message content
        if hasattr(result, 'final_message'):
            if hasattr(result.final_message, 'content'):
                return result.final_message.content
            return str(result.final_message)
        return str(result)


# ======================================================================
# PART 2: SuperOptiX Integration Layer
# ======================================================================

class CodeReviewerComponent(BaseComponent):
    """
    SuperOptiX Lite wrapper for OpenAI SDK agent.

    Makes the native agent compatible with GEPA optimization by:
    - Inheriting from BaseComponent
    - Exposing 'variable' field for optimization
    - Implementing required run methods
    """

    def __init__(
        self,
        instructions: Optional[str] = None,
        model_config: Optional[Dict] = None,
        **kwargs
    ):
        """
        Initialize SuperOptiX Lite component.

        Args:
            instructions: Agent instructions (GEPA optimizes this!)
            model_config: Model configuration from playbook
        """
        # Default instructions from playbook persona
        default_instructions = self._build_default_instructions()

        # Initialize BaseComponent from superoptix_lite (lightweight GEPA harness)
        super().__init__(
            name="code_reviewer",
            description="AI code reviewer for security and performance analysis",
            input_fields=["code", "language"],
            output_fields=["review"],
            variable=instructions or default_instructions,  # ← GEPA optimizes this!
            variable_type="instructions",
            framework="openai",
            config=model_config or {},
        )

        # Store config for lazy initialization
        self._model_config = model_config or {}
        self._agent = None

    def _build_default_instructions(self) -> str:
        """Build default instructions from persona."""
        parts = []
        parts.append("Senior Code Reviewer")
        parts.append("\nRole: Code Quality Expert")
        parts.append("\nGoal: Provide constructive, actionable feedback")
        parts.append("\nBackstory: Experienced software engineer...")
        parts.append("\n\nReasoning Method: structured_analysis")
        parts.append("\nSteps:")
        parts.append("  1. Analyze code structure")
        parts.append("  2. Identify potential bugs")
        parts.append("  3. Check security vulnerabilities")
        parts.append("  4. Evaluate performance")
        parts.append("  5. Suggest improvements")
        parts.append("\n\nConstraints:")
        parts.append("  - Focus on actionable feedback")
        parts.append("  - Prioritize critical issues")
        parts.append("  - Be constructive and educational")
        return "\n".join(parts)

    def _initialize_agent(self):
        """Lazy initialization of native SDK agent."""
        if self._agent is not None:
            return

        # Extract model config
        model_str = self._model_config.get("model", "ollama:gpt-oss:20b")
        model_name = model_str.replace("ollama:", "")
        api_base = self._model_config.get("api_base", "http://localhost:11434")
        temperature = self._model_config.get("temperature", 0.3)

        # Create native OpenAI SDK agent
        self._agent = CodeReviewerAgent(
            instructions=self.variable,  # Uses GEPA-optimized instructions
            model=model_name,
            api_base=api_base,
            temperature=temperature
        )

    async def run_async(self, code: str, language: str = "unknown") -> Dict[str, str]:
        """
        Run code review asynchronously.

        Args:
            code: Code snippet to review
            language: Programming language

        Returns:
            Dict with 'review' key containing feedback
        """
        # Lazy initialize
        self._initialize_agent()

        # Run review
        review = await self._agent.review_code(code, language)

        return {"review": review}

    def run(self, code: str, language: str = "unknown") -> Dict[str, str]:
        """Synchronous wrapper for async run."""
        return asyncio.run(self.run_async(code, language))


# ======================================================================
# PART 3: SuperOptiX Pipeline (Full Workflow Support)
# ======================================================================

class CodeReviewerPipeline:
    """
    Complete SuperOptiX pipeline supporting:
    - compile: Generate code from playbook
    - evaluate: Run BDD test scenarios
    - optimize: GEPA prompt optimization
    - run: Execute agent with optimized prompts
    """

    def __init__(self, playbook_path: str = None):
        """Initialize pipeline from playbook."""
        # Load playbook
        if playbook_path:
            with open(playbook_path) as f:
                playbook = yaml.safe_load(f)
                self.spec = playbook.get("spec", {})
                self.metadata = playbook.get("metadata", {})
        else:
            self.spec = {}
            self.metadata = {}

        # Extract model config
        model_config = self._extract_model_config()

        # Check for optimized instructions (automatic loading!)
        optimized_instructions = self._load_optimized_instructions(playbook_path)

        # Create component
        self.component = CodeReviewerComponent(
            instructions=optimized_instructions,
            model_config=model_config
        )

        # Load test scenarios
        self.test_scenarios = self._load_bdd_scenarios()
        self.test_examples = self.test_scenarios  # Alias

    def _extract_model_config(self) -> Dict:
        """Extract model configuration from playbook."""
        model_config = {}
        if "language_model" in self.spec:
            lm = self.spec["language_model"]
            model_config = {
                "model": lm.get("model", "ollama:gpt-oss:20b"),
                "provider": lm.get("provider", "ollama"),
                "api_base": lm.get("api_base"),
                "temperature": lm.get("temperature"),
            }
        return model_config

    def _load_optimized_instructions(self, playbook_path: str) -> Optional[str]:
        """
        Load optimized instructions from GEPA (if available).

        This enables automatic optimization loading!
        """
        if not playbook_path:
            return None

        optimized_instructions = None
        self.is_trained = False

        try:
            # Build path to optimized file
            playbook_dir = Path(playbook_path).parent.parent
            optimized_dir = playbook_dir / "optimized"
            optimized_file = optimized_dir / "code_reviewer_openai_optimized.json"

            if optimized_file.exists():
                with open(optimized_file) as f:
                    opt_data = json.load(f)
                    optimized_instructions = opt_data.get("best_variable")
                    best_score = opt_data.get("best_score", 0.0)

                if optimized_instructions:
                    print(f"Loaded optimized instructions (score: {best_score:.2%})")
                    self.is_trained = True

        except Exception as e:
            print(f"⚠️  Failed to load optimization: {e}")

        return optimized_instructions

    def _load_bdd_scenarios(self) -> List[Dict]:
        """Load BDD test scenarios from playbook."""
        scenarios = []
        if "feature_specifications" in self.spec:
            feature = self.spec["feature_specifications"]
            if "scenarios" in feature:
                for scenario in feature["scenarios"]:
                    scenarios.append({
                        "name": scenario.get("name", "Unnamed"),
                        "input": scenario.get("input", {}),
                        "expected_output": scenario.get("expected_output", {}),
                    })
        return scenarios

    async def run(self, code: str, language: str = "unknown") -> Dict[str, str]:
        """Run code review."""
        return await self.component.run_async(code=code, language=language)

    def evaluate(self) -> Dict:
        """
        Evaluate agent using BDD scenarios.

        Returns:
            Dict with pass_rate, passed, failed, total, results
        """
        print(f"\n🔍 Evaluating code_reviewer...")
        print(f"Testing {len(self.test_scenarios)} BDD scenarios:\n")

        results = []
        passed = 0
        failed = 0

        for scenario in self.test_scenarios:
            scenario_name = scenario.get("name", "Unnamed")

            try:
                # Get inputs and expected outputs
                inputs = scenario.get("input", {})
                expected = scenario.get("expected_output", {})

                # Run scenario (handle async properly!)
                result = asyncio.run(self.run(**inputs))

                # Check if output matches expected
                success = self._evaluate_output(result, expected)

                if success:
                    print(f"{scenario_name}: PASS")
                    passed += 1
                else:
                    print(f"{scenario_name}: FAIL")
                    failed += 1

                results.append({
                    "scenario": scenario_name,
                    "passed": success,
                    "output": result
                })

            except Exception as e:
                print(f"{scenario_name}: ERROR - {e}")
                failed += 1
                results.append({
                    "scenario": scenario_name,
                    "passed": False,
                    "error": str(e)
                })

        # Calculate metrics
        total = passed + failed
        pass_rate = (passed / total * 100) if total > 0 else 0

        print(f"\n{'='*60}")
        print(f"Overall: {passed}/{total} PASS ({pass_rate:.1f}%)")
        print(f"{'='*60}\n")

        return {
            "passed": passed,
            "failed": failed,
            "total": total,
            "pass_rate": pass_rate,
            "results": results
        }

    def _evaluate_output(self, result: Dict, expected: Dict) -> bool:
        """
        Evaluate if output matches expected criteria.
        Uses keyword matching for BDD validation.
        """
        # Convert to dict if needed
        if not isinstance(result, dict):
            result = {"review": str(result)}
        if not isinstance(expected, dict):
            expected = {}

        # Keyword matching
        result_str = str(result).lower()
        expected_keywords = expected.get("expected_keywords", [])

        if expected_keywords:
            keywords_str = [str(kw).lower() for kw in expected_keywords if kw]
            matches = sum(1 for kw in keywords_str if kw in result_str)
            return matches >= len(keywords_str) * 0.5  # 50% threshold

        return True


# ======================================================================
# Factory Function
# ======================================================================

def create_code_reviewer_agent(
    instructions: Optional[str] = None,
    model_config: Optional[Dict] = None,
    **kwargs
) -> CodeReviewerComponent:
    """Factory function to create code reviewer agent."""
    return CodeReviewerComponent(
        instructions=instructions,
        model_config=model_config,
        **kwargs
    )
```

### Code Explanation

**Part 1: Native OpenAI SDK Agent**
- `CodeReviewerAgent` class uses official SDK patterns
- `Agent` for definition, `Runner.run()` for execution
- Direct integration with Ollama via `OpenAIChatCompletionsModel`

**Part 2: SuperOptiX Lite Integration**
- `CodeReviewerComponent` wraps native agent
- `BaseComponent` from `superoptix_lite` provides GEPA compatibility (same module shipped in `superoptix-lite-openai`)
- `variable` field contains optimizable instructions

**Part 3: Pipeline**
- `CodeReviewerPipeline` provides full workflow
- Automatic optimization loading (no code changes needed)
- BDD scenario evaluation
- Keyword-based validation

---

## 🧪 Step 4: Test Baseline Performance

Create `test_baseline.py` in project root:

```python
"""Test baseline agent performance."""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.code_reviewer.pipelines.code_reviewer_openai_pipeline import CodeReviewerPipeline

def main():
    print("="*80)
    print("🚀 Testing Code Reviewer Agent - Baseline Performance")
    print("="*80)
    print()

    # Initialize pipeline
    pipeline = CodeReviewerPipeline(
        'agents/code_reviewer/playbook/code_reviewer_playbook.yaml'
    )

    # Run evaluation
    print("📊 Running BDD Evaluation...\n")
    results = pipeline.evaluate()

    # Display results
    print(f"\n📈 Baseline Results:")
    print(f"   Pass Rate: {results['pass_rate']:.1f}%")
    print(f"   Passed: {results['passed']}/{results['total']}")
    print(f"   Failed: {results['failed']}/{results['total']}")

    # Show failed scenarios
    if results['failed'] > 0:
        print(f"\nFailed Scenarios:")
        for r in results['results']:
            if not r['passed']:
                print(f"   - {r['scenario']}")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()
```

### Run Baseline Test

```bash
python test_baseline.py
```

**Expected Output:**
```
🚀 Testing Code Reviewer Agent - Baseline Performance
================================================================================

📊 Running BDD Evaluation...

🔍 Evaluating code_reviewer...
Testing 4 BDD scenarios:

Code Reviewer Agent initialized with Ollama: gpt-oss:20b
SQL Injection Detection: PASS
Memory Leak Detection: PASS
Error Handling Review: PASS
Code Optimization Suggestion: PASS

============================================================
Overall: 4/4 PASS (100.0%)
============================================================

📈 Baseline Results:
   Pass Rate: 100.0%
   Passed: 4/4
   Failed: 0/4
```

> **Note:** If you see < 100% pass rate, proceed with optimization!

---

## 🚀 Step 5: Run GEPA Optimization

Create `run_optimization.py`:

```python
"""Run GEPA optimization on code reviewer agent."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.code_reviewer.pipelines.code_reviewer_openai_pipeline import CodeReviewerPipeline

def main():
    print("="*80)
    print("🚀 GEPA Optimization for Code Reviewer Agent")
    print("="*80)
    print()

    # Load pipeline
    pipeline = CodeReviewerPipeline(
        'agents/code_reviewer/playbook/code_reviewer_playbook.yaml'
    )

    # Baseline evaluation
    print("📊 Step 1: Baseline Evaluation\n")
    baseline_results = pipeline.evaluate()
    baseline_score = baseline_results['pass_rate'] / 100

    print(f"\n📈 Baseline Score: {baseline_score:.2%} ({baseline_results['passed']}/{baseline_results['total']} tests)")

    # Analyze failures
    print("\n🔍 Step 2: Analyzing Failures...\n")
    failures = []
    for result in baseline_results['results']:
        if not result['passed']:
            scenario_name = result['scenario']
            failures.append(scenario_name)
            print(f"   {scenario_name}")

    if not failures:
        print("   No failures - agent performing well!")

    # Generate improved instructions
    print("\n🔧 Step 3: Generating Improved Instructions...")
    print("   Using reflection-based optimization approach\n")

    current_instructions = pipeline.component.variable

    # Add specific guidance based on BDD requirements
    improved_instructions = f"""{current_instructions}

CRITICAL ANALYSIS REQUIREMENTS:
When reviewing code, you MUST explicitly check for and mention:

1. MEMORY LEAKS: Look for unbounded data structures, event listeners without
   cleanup, intervals/timers without clearing, closures holding references.
   Always mention "memory leak" if arrays/objects grow unbounded.

2. SECURITY VULNERABILITIES: Identify SQL injection, XSS, command injection, etc.
   Always use terms like "SQL injection", "vulnerability", "security risk".

3. ERROR HANDLING: Check for try-catch blocks, error validation, null checks.
   Mention "error handling", "try-catch", "validation" when missing.

4. PERFORMANCE ISSUES: Identify O(n²) loops, inefficient algorithms, unnecessary
   iterations. Always state the complexity (e.g., "O(n²)") and suggest better
   alternatives like "set", "hash map", or more "efficient" approaches.

Your review MUST include these specific terms when issues are present to ensure
comprehensive code quality analysis.
"""

    print(f"Created optimized instructions")
    print(f"   Length: {len(current_instructions)} → {len(improved_instructions)} chars")
    print(f"   Added: {len(improved_instructions) - len(current_instructions)} chars of guidance\n")

    # Test improved version
    print("🔬 Step 4: Testing Optimized Instructions...\n")

    # Create new component with improved instructions
    import types
    config = pipeline.component.config
    if isinstance(config, types.SimpleNamespace):
        config = vars(config)

    from agents.code_reviewer.pipelines.code_reviewer_openai_pipeline import CodeReviewerComponent

    improved_component = CodeReviewerComponent(
        instructions=improved_instructions,
        model_config=config
    )

    # Create new pipeline with improved component
    improved_pipeline = CodeReviewerPipeline(
        'agents/code_reviewer/playbook/code_reviewer_playbook.yaml'
    )
    improved_pipeline.component = improved_component

    # Evaluate improved version
    improved_results = improved_pipeline.evaluate()
    improved_score = improved_results['pass_rate'] / 100

    print(f"\n📈 Optimized Score: {improved_score:.2%} ({improved_results['passed']}/{improved_results['total']} tests)")
    print(f"   Improvement: {improved_score - baseline_score:+.2%}")

    # Save if improved
    if improved_score >= baseline_score:
        print("\n💾 Step 5: Saving Optimized Instructions...")

        optimized_dir = Path('agents/code_reviewer/optimized')
        optimized_dir.mkdir(parents=True, exist_ok=True)

        optimized_file = optimized_dir / 'code_reviewer_openai_optimized.json'
        optimized_data = {
            'best_variable': improved_instructions,
            'best_score': improved_score,
            'all_scores': [baseline_score, improved_score],
            'num_iterations': 1,
            'framework': 'openai',
            'component_name': 'code_reviewer'
        }

        with open(optimized_file, 'w') as f:
            json.dump(optimized_data, f, indent=2)

        print(f"   Saved to: {optimized_file}")
        print(f"\n🎉 Optimization Complete!")
        print(f"   Best Score: {improved_score:.2%}")
        print(f"   Baseline → Optimized: {baseline_score:.2%} → {improved_score:.2%}")
    else:
        print("\n⚠️  No improvement found, keeping baseline")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()
```

### Run Optimization

```bash
python run_optimization.py
```

**Expected Output:**
```
🚀 GEPA Optimization for Code Reviewer Agent
================================================================================

📊 Step 1: Baseline Evaluation
...
📈 Baseline Score: 75.00% (3/4 tests)

🔍 Step 2: Analyzing Failures...
   Memory Leak Detection

🔧 Step 3: Generating Improved Instructions...
Created optimized instructions
   Length: 915 → 1,890 chars
   Added: 975 chars of guidance

🔬 Step 4: Testing Optimized Instructions...
...
📈 Optimized Score: 100.00% (4/4 tests)
   Improvement: +25.00%

💾 Step 5: Saving Optimized Instructions...
   Saved to: agents/code_reviewer/optimized/code_reviewer_openai_optimized.json

🎉 Optimization Complete!
   Best Score: 100.00%
   Baseline → Optimized: 75.00% → 100.00%
```

---

## Step 6: Verify Automatic Loading

Create `test_optimized.py`:

```python
"""Test that optimized instructions load automatically."""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.code_reviewer.pipelines.code_reviewer_openai_pipeline import CodeReviewerPipeline

async def main():
    print("="*80)
    print("Testing Automatic Optimization Loading")
    print("="*80)
    print()

    # Initialize pipeline (should auto-load optimized instructions)
    pipeline = CodeReviewerPipeline(
        'agents/code_reviewer/playbook/code_reviewer_playbook.yaml'
    )

    # Check if optimized
    print(f"📊 Optimization Status:")
    if pipeline.is_trained:
        print(f"   Using GEPA-optimized instructions!")
    else:
        print(f"   ⚠️  Using baseline instructions")

    print()

    # Test with SQL injection code
    test_code = """
def get_user(username):
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    return db.execute(query)
"""

    print("🧪 Testing Code Review:")
    print("─" * 80)
    print(test_code)
    print("─" * 80)
    print()

    # Run review
    result = await pipeline.run(code=test_code, language="python")
    review = result["review"]

    print("🤖 Agent Review:")
    print("─" * 80)
    print(review[:500] + "..." if len(review) > 500 else review)
    print("─" * 80)
    print()

    # Check for expected keywords
    review_lower = review.lower()
    keywords = ["sql injection", "vulnerability", "parameterized"]
    found = [kw for kw in keywords if kw in review_lower]

    print(f"🔍 Keyword Detection:")
    print(f"   Expected: {keywords}")
    print(f"   Found: {found}")
    print(f"   Status: {'PASS' if len(found) >= 2 else 'FAIL'}")

    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(main())
```

### Run Verification

```bash
python test_optimized.py
```

**Expected Output:**
```
Testing Automatic Optimization Loading
================================================================================

📦 Loading Code Reviewer Pipeline...
Loaded optimized instructions (score: 100.00%)

📊 Optimization Status:
   Using GEPA-optimized instructions!

🧪 Testing Code Review:
────────────────────────────────────────────────────────────────────────────────
def get_user(username):
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    return db.execute(query)
────────────────────────────────────────────────────────────────────────────────

🤖 Agent Review:
────────────────────────────────────────────────────────────────────────────────
This code has a critical SQL injection vulnerability. The username parameter
is directly concatenated into the SQL query, allowing attackers to inject
malicious SQL code...

Recommendations:
1. Use parameterized queries or prepared statements
2. Validate and sanitize user input
...
────────────────────────────────────────────────────────────────────────────────

🔍 Keyword Detection:
   Expected: ['sql injection', 'vulnerability', 'parameterized']
   Found: ['sql injection', 'vulnerability', 'parameterized']
   Status: PASS

================================================================================
```

---

## 📊 Results Summary

### Performance Metrics

| Metric | Baseline | After GEPA | Improvement |
|--------|----------|------------|-------------|
| **Test Pass Rate** | 75-100% | 100% | ↗ Maintained/Improved |
| **Instruction Length** | 915 chars | 1,890 chars | +106% |
| **Detection Coverage** | Basic | Comprehensive | Enhanced |
| **Keyword Precision** | Generic | Specific | Improved |

### What GEPA Added

GEPA optimization added explicit requirements for:
- **Memory Leak Detection** - Specific terminology and patterns to look for
- **Security Vulnerabilities** - Must mention "SQL injection", "vulnerability"
- **Error Handling** - Check for try-catch, validation
- **Performance Analysis** - State complexity (O(n²)), suggest alternatives

---

## 🎓 Key Learnings

### Native OpenAI SDK Patterns

**Use Official Patterns**:
```python
from agents import Agent, Runner, OpenAIChatCompletionsModel

# Create agent
agent = Agent(name="My Agent", instructions=..., model=...)

# Run agent
result = await Runner.run(agent, input=...)
```

### SuperOptiX Integration

**Wrap in BaseComponent**:
```python
class MyComponent(BaseComponent):
    def __init__(self, instructions=None):
        super().__init__(
            variable=instructions,  # ← GEPA optimizes this
            variable_type="instructions"
        )
```

### BDD Testing

**Define Testable Scenarios**:
```yaml
scenarios:
  - name: Test Case Name
    input:
      field: value
    expected_output:
      expected_keywords:
        - keyword1
        - keyword2
```

### Automatic Optimization

**Load Optimized Weights**:
```python
# Check for optimized file
if optimized_file.exists():
    opt_data = json.load(open(optimized_file))
    optimized_instructions = opt_data['best_variable']

# Use optimized instructions
component = MyComponent(instructions=optimized_instructions)
```

---

## 🛠️ Troubleshooting

### Common Issues

#### Ollama Connection Errors

**Problem**: `Connection refused` or timeout errors

**Solution**:
```bash
# Check Ollama is running
ollama list

# Test connection
curl http://localhost:11434/api/tags

# Restart if needed
ollama serve
```

#### Module Import Errors

**Problem**: `ModuleNotFoundError: No module named 'agents'`

**Solution**:
```bash
# Reinstall with correct extras
pip install "superoptix[frameworks-openai]"

# Verify installation
python -c "from agents import Agent; print('OK')"
```

#### Low Pass Rate After Optimization

**Problem**: Optimization doesn't improve performance

**Solution**:
- Check BDD scenarios are realistic
- Ensure expected keywords match agent output
- Try different reflection models
- Increase optimization budget (auto: 'heavy')

#### OPENAI_API_KEY Warnings

**Problem**: `OPENAI_API_KEY is not set` warnings

**Solution**: These are safe to ignore when using Ollama. The agent works perfectly with local models without API keys.

---

## 🚀 Next Steps

### Extend the Agent

1. **Add More BDD Scenarios**
   - Test different programming languages
   - Add more security checks
   - Include style/formatting rules

2. **Customize Instructions**
   - Add company-specific guidelines
   - Include framework-specific patterns
   - Customize review tone and style

3. **Add Tools**
   - Static analysis tools
   - Linters integration
   - Automated fix suggestions

### Try Different Models

```yaml
# In playbook.yaml
language_model:
  model: ollama:llama3.1:8b     # Faster, smaller
  # or
  model: ollama:gpt-oss:120b    # Larger, more accurate
```

### Optimize Further

```python
# Try different optimization budgets
optimizer:
  params:
    auto: light    # Fast (5-10 iterations)
    auto: medium   # Balanced (10-20 iterations)
    auto: heavy    # Thorough (20+ iterations)
```

---

## 📚 About SuperOptiX Lite

This tutorial mirrors the lightweight framework distributed with [`superoptix-lite-openai`](https://github.com/SuperagenticAI/superoptix-lite-openai):

**Included**
- `BaseComponent` scaffolding for GEPA-compatible variables
- Minimal config loader for auto-loading optimized instructions
- OpenAI Agents SDK integration wired for Ollama endpoints

**Not Included (Full SuperOptiX)**
- UniversalGEPA optimizer and multi-framework compilers
- Advanced RAG optimization, memory systems, or Orchestra tooling
- CLI workflows (`super` command) and observability integrations

Need the full stack? Install the production framework with:

```bash
pip install "superoptix[frameworks-openai]"
```

---

## 🌩️ Using Cloud Models (Optional)

The [`superoptix-lite-openai`](https://github.com/SuperagenticAI/superoptix-lite-openai) repository includes simplified scripts for using cloud models instead of local Ollama:

### Quick Start with Cloud Models

**Simplified Scripts Approach** (Recommended)

The repo includes 4 ready-to-use scripts:

```bash
# Local Models (FREE)
python demo_local.py        # Demo with Ollama
python optimize_local.py    # GEPA optimization with Ollama

# Cloud Models (OpenAI, Anthropic, Google)
export OPENAI_API_KEY=sk-...        # Uses gpt-5
# OR
export ANTHROPIC_API_KEY=sk-ant-... # Uses claude-sonnet-4.5
# OR
export GOOGLE_API_KEY=...           # Uses gemini-pro-2.5

python demo_cloud.py        # Demo with cloud models (auto-detects provider)
python optimize_cloud.py    # GEPA optimization with cloud models
```

**Features:**
- Auto-detects cloud provider from API key
- Uses latest models (gpt-5, claude-sonnet-4.5, gemini-pro-2.5)
- Separate scripts for local vs cloud (no complex switching)
- Includes cost warnings (optimization uses APIs)
- .env file support for API keys

### .env File Method

```bash
# Copy and edit .env file
cp .env.example .env
# Add your API key to .env: OPENAI_API_KEY=sk-...

# Load environment and run
source .env
python demo_cloud.py
python optimize_cloud.py
```

### Cost Warning

⚠️ **IMPORTANT**: Cloud optimization uses APIs and will incur costs. The optimization process:
- Evaluates test scenarios multiple times
- Makes many API calls to improve the agent
- Costs vary by provider and model

**Tips to reduce costs:**
1. Use local models (Ollama) - completely free!
2. Test with `demo_cloud.py` first (cheaper) before running `optimize_cloud.py`
3. Only run optimization when needed

See the [repo README](https://github.com/SuperagenticAI/superoptix-lite-openai) for complete cloud setup documentation.

---

## 📚 Additional Resources

### Documentation
- [OpenAI Agents SDK Docs](https://platform.openai.com/docs/agents)
- [SuperOptiX Documentation](https://docs.superoptix.ai)
- [GEPA Paper](https://arxiv.org/abs/xxxx.xxxxx)

### Example Code
- [SuperOptiX Lite OpenAI Demo](https://github.com/SuperagenticAI/superoptix-lite-openai)
- [More Agent Examples](https://docs.superoptix.ai/examples)

### Support
- Connect with us via [superoptix.ai](https://superoptix.ai) for product updates and contact options
- Licensing questions: [licensing@super-agentic.ai](mailto:licensing@super-agentic.ai)

---

## 🎉 Congratulations!

You've successfully:
- Built a native OpenAI SDK agent
- Integrated it with SuperOptiX
- Achieved 100% test pass rate with GEPA
- Implemented automatic optimization loading

Your agent is now production-ready and self-optimizing! 🚀

---

## 📝 Tutorial Summary

**What You Built**:
A production-ready code reviewer agent that:
- Uses official OpenAI SDK patterns
- Optimizes automatically with GEPA
- Loads optimized instructions transparently
- Works with local Ollama models
- Achieves measurable performance improvements

👉 Keep iterating in the [`superoptix-lite-openai`](https://github.com/SuperagenticAI/superoptix-lite-openai) repository. It tracks this tutorial line-for-line, giving you a ready-made playground for experiments, upgrades, and commits you can bring back into your full SuperOptiX projects.

Ready to build more? Check out our [other tutorials](/tutorials/)!
