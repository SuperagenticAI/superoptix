# GEPA Integration Examples

This guide provides practical examples of integrating GEPA optimization into your SuperOptiX agents across different domains.

## Mathematics Agent with GEPA

Example configuration for advanced mathematical problem solving:

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Advanced Math Solver
  id: math-solver-gepa
spec:
  language_model:
    location: local
    provider: ollama
    model: llama3.1:8b
    temperature: 0.1
  persona:
    role: "Mathematics Specialist"
    goal: "Solve complex mathematical problems with step-by-step reasoning"
    traits: ["analytical", "precise", "methodical"]
  tasks:
    - name: solve_math_problem
      description: Solve mathematical problems with verification
      inputs:
        - name: problem
          type: str
          required: true
      outputs:
        - name: solution
          type: str
        - name: answer
          type: str
        - name: reasoning
          type: str
  optimization:
    optimizer:
      name: GEPA
      params:
        metric: advanced_math_feedback
        auto: light
        reflection_lm: qwen3:8b
        reflection_minibatch_size: 3
        skip_perfect_score: true
  feature_specifications:
    scenarios:
      - name: quadratic_equation
        input:
          problem: "Solve x² - 5x + 6 = 0"
        expected_output:
          answer: "x = 2 or x = 3"
          solution: "Factor as (x-2)(x-3) = 0"
```

## Enterprise Document Analyzer

GEPA configuration for business document processing:

```yaml
spec:
  optimization:
    optimizer:
      name: GEPA
      params:
        metric: multi_component_enterprise_feedback
        auto: light
        reflection_lm: qwen3:8b
        predictor_level_feedback: true
  feature_specifications:
    scenarios:
      - name: urgent_request
        input:
          document: "URGENT: Server room leak affecting critical infrastructure"
        expected_output:
          urgency: "Critical"
          sentiment: "Negative" 
          categories: "facility_maintenance, infrastructure, emergency"
```

## Privacy-Conscious Agent

GEPA setup for secure information handling:

```yaml
spec:
  optimization:
    optimizer:
      name: GEPA
      params:
        metric: privacy_preservation_feedback
        auto: light
        reflection_lm: qwen3:8b
        llm_as_judge_feedback: true
  feature_specifications:
    scenarios:
      - name: pii_redaction
        input:
          user_query: "I'm John Smith, SSN 123-45-6789, need medical advice"
        expected_output:
          redacted_request: "A person needs medical information"
          privacy_assessment: "Removed PII while preserving context"
```

## Security Analysis Agent

GEPA configuration for vulnerability detection:

```yaml
spec:
  optimization:
    optimizer:
      name: GEPA
      params:
        metric: vulnerability_detection_feedback
        auto: light
        reflection_lm: qwen3:8b
        format_failure_feedback: true
  feature_specifications:
    scenarios:
      - name: sql_injection
        input:
          code_or_config: |
            query = "SELECT * FROM users WHERE name = '" + name + "'"
        expected_output:
          vulnerabilities: "Critical: SQL Injection vulnerability"
          risk_assessment: "Critical severity - allows database compromise"
```

## Running GEPA Optimization

### Basic Workflow

```bash
# Pull and set up agent
super agent pull advanced-math-gepa
super agent compile advanced-math-gepa

# Evaluate baseline
super agent evaluate advanced-math-gepa

# Run GEPA optimization
super agent optimize advanced-math-gepa

# Measure improvement
super agent evaluate advanced-math-gepa

# Test optimized agent
super agent run advanced-math-gepa --goal "Solve x² + 3x - 4 = 0"
```

### Memory-Efficient Configuration

For systems with memory constraints:

```yaml
spec:
  language_model:
    model: llama3.1:8b        # ~8GB
  optimization:
    optimizer:
      reflection_lm: qwen3:8b  # ~8GB, different model
      auto: light              # Conservative budget
      reflection_minibatch_size: 3
```

### Progressive Optimization

Start conservative and increase budget if needed:

```bash
# Start with light optimization
super agent optimize your_agent  # Uses auto: light

# If results are promising, increase budget
# Edit playbook: auto: medium
super agent compile your_agent
super agent optimize your_agent --force

# For production, consider heavy optimization
# Edit playbook: auto: heavy
super agent optimize your_agent --force
```

## GEPA Output Analysis

### Successful GEPA Logs

```
INFO dspy.teleprompt.gepa.gepa: Running GEPA for approx 400 metric calls
INFO dspy.evaluate.evaluate: Average Metric: 2.0 / 5 (40.0%)
INFO dspy.teleprompt.gepa.gepa: Iteration 0: Base program score: 0.4
INFO dspy.evaluate.evaluate: Average Metric: 3.0 / 3 (100.0%)
INFO dspy.teleprompt.gepa.gepa: Iteration 2: Proposed new text for predictor
```

This indicates:
- GEPA started with appropriate budget
- Baseline performance measured (40%)
- Iterative improvements occurring
- Score improvements achieved (100%)
- New prompts being generated

### Understanding Timeout Behavior

GEPA optimization often exceeds 2-minute timeouts:

```
Error: Command timed out after 2m 0.0s
INFO dspy.teleprompt.gepa.gepa: Running GEPA for approx 400 metric calls
```

This is **normal behavior** because:
- GEPA prioritizes quality over speed
- Multiple reflection and generation cycles
- Typical completion time: 3-5 minutes for light budget

### Extending Timeout

```bash
# Allow more time for GEPA completion
super agent optimize your_agent --timeout 300  # 5 minutes
```

## Comparison: Before and After GEPA

### Before GEPA Optimization

```
Agent Response:
"To solve x² - 5x + 6 = 0, we can factor: (x-2)(x-3) = 0, so x = 2 or x = 3."
```

### After GEPA Optimization

```
Agent Response:
"**Method 1: Factoring**
Step 1: Factor x² - 5x + 6 into (x-2)(x-3) = 0
Finding factors: need two numbers that multiply to 6 and add to -5
These are -2 and -3, so: (x-2)(x-3) = 0

**Method 2: Quadratic Formula**
Using x = (-b ± √(b²-4ac)) / 2a where a=1, b=-5, c=6
x = (5 ± √(25-24)) / 2 = (5 ± 1) / 2
x = 3 or x = 2

**Verification:**
For x=2: (2)² - 5(2) + 6 = 4 - 10 + 6 = 0 ✓
For x=3: (3)² - 5(3) + 6 = 9 - 15 + 6 = 0 ✓"
```

GEPA optimization resulted in:
- Multiple solution methods
- Step-by-step explanations
- Solution verification
- Better pedagogical structure

## Best Practices

### Choose Appropriate Metrics

Match metrics to your domain:

```yaml
# Mathematics
metric: advanced_math_feedback

# Business documents  
metric: multi_component_enterprise_feedback

# Security analysis
metric: vulnerability_detection_feedback
```

### Start Conservative

Begin with light budgets:

```yaml
optimization:
  optimizer:
    auto: light  # Start here
    # Increase to medium/heavy if justified
```

### Quality Training Data

Provide comprehensive scenarios:

```yaml
feature_specifications:
  scenarios:
    - name: comprehensive_test
      description: Cover main use cases and edge cases
      input:
        problem: "Realistic, well-defined problem"
      expected_output:
        answer: "Complete expected response"
```

### Monitor Progress

Watch for improvement indicators:

- Score improvements in logs
- Quality of generated prompts
- Performance on evaluation scenarios

### Validate Results

Always measure GEPA effectiveness:

```bash
# Before optimization
super agent evaluate your_agent  # Note baseline

# After optimization  
super agent evaluate your_agent  # Compare improvement
```

## Related Documentation

- [GEPA Optimization Guide](../guides/gepa-optimization.md) - Complete GEPA reference
- [Optimization Guide](../guides/optimization.md) - General optimization techniques
- [Agent Development Guide](../guides/agent-development.md) - Development workflow