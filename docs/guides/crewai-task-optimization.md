# CrewAI Advanced Task Optimization

## Overview

SuperOptiX supports **combined agent + task optimization** for CrewAI. GEPA optimizes both the agent profile AND task configuration together for maximum agent-task alignment.

**Key Features:**
- Combined optimization: agent profile + task configuration
- Better agent-task alignment
- Improved performance over agent-only optimization
- Automatic parsing and extraction
- Single optimization variable for holistic improvement

---

## 📦 Installation

```bash
pip install superoptix[frameworks-crewai]
```

**Includes:**
- crewai 1.2.0
- SuperOptiX core with GEPA 0.0.17

**Requirements:**
- Python 3.11+
- Git (for DSPy dependency)

---

## What Gets Optimized

### Combined Variable

GEPA optimizes a **single combined variable** containing:

#### Agent Profile
- **role**: Agent's identity and expertise
- **goal**: Agent's primary objective
- **backstory**: Agent's background and capabilities

#### Task Configuration
- **task description**: What the agent should accomplish
- **expected output**: What the agent should produce

### Example Combined Profile

**Before Optimization:**

```
Role: Professional Content Writer
Goal: Create engaging content
Backstory: You are an experienced writer

Task Description: Write about {topic}
Expected Output: A good article
```

**After GEPA Optimization:**

```
Role: Senior Content Strategist specializing in technical communication
Goal: Create highly engaging, SEO-optimized content that educates and converts readers
Backstory: Distinguished content strategist with 10+ years creating award-winning articles for Fortune 500 companies

Task Description: Create comprehensive, research-backed content about {topic}, focusing on:
- Current trends and emerging developments
- Real-world applications and case studies
- Expert insights and authoritative perspectives
- Actionable takeaways for readers
- SEO optimization with natural keyword integration

Expected Output: A publication-ready article containing:
- Captivating headline and hook
- Executive summary with key insights
- 5-7 well-structured sections
- Minimum 3 real-world examples
- Data-driven insights with citations
- Practical recommendations
- Engaging conclusion
- 800-1200 words in markdown format
```

**Impact:** 20-30% improvement in output quality!

---

## Why Combined Optimization Works Better

### Comparison

| Aspect | Agent Only | Combined (Agent + Task) |
|--------|-----------|------------------------|
| **Variables** | role + goal + backstory | role + goal + backstory + task + output |
| **Optimization** | Agent profile only | Agent + Task together |
| **Alignment** | Manual | **Automatic** |
| **Improvement** | +10-15% | **+20-30%** |
| **Quality** | Good | **Excellent** |

### Benefits

1. **Better Alignment**
   - Agent capabilities match task requirements
   - Task instructions leverage agent strengths
   - No mismatch between agent abilities and task expectations

2. **Holistic Improvement**
   - GEPA optimizes both components together
   - Considers agent-task synergy
   - Better than optimizing separately

3. **Clearer Expectations**
   - Task description matches agent expertise
   - Expected output aligns with agent capabilities
   - More consistent results

---

## Quick Start

### Step 1: Pull Demo Agent

```bash
# Pull the content creator demo (combined optimization)
super agent pull content_creator_crew
```

### Step 2: Compile

```bash
super agent compile content_creator_crew --framework crewai
```

### Step 3: Evaluate Baseline

```bash
super agent evaluate content_creator_crew
```

Output:
```
Pass Rate: 75% (3/4 scenarios)
```

### Step 4: Optimize (Combined)

```bash
super agent optimize content_creator_crew --auto medium
```

GEPA optimizes:
- Agent profile (role + goal + backstory)
- Task configuration (description + expected_output)
- Both together for maximum alignment!

### Step 5: Re-evaluate

```bash
super agent evaluate content_creator_crew  # automatically loads optimized weights
```

Output:
```
Pass Rate: 100% (4/4 scenarios)  ← Improved!
```

---

## Creating Combined Optimization Agents

### Playbook Structure

```yaml
# content_creator_playbook.yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: content_creator
spec:
  target_framework: crewai
  
  language_model:
    provider: ollama
    model: llama3.1:8b
  
  # Agent Profile (optimizable)
  persona:
    role: Content Creator
    goal: Create engaging content
    backstory: |
      Experienced writer with content strategy expertise.
  
  # Task Configuration (optimizable)
  tasks:
    - name: write_content
      description: Write compelling content about the given topic
      expected_output: Polished article ready for publication
  
  # BDD Scenarios
  feature_specifications:
    scenarios:
      - name: Write tech article
        input:
          topic: "AI agents"
        expected_output:
          article: "Comprehensive article about AI agents"
          expected_keywords:
            - AI agents
            - automation
            - intelligent systems
```

### How It Works

1. **Compile**: Template extracts both agent profile AND task config
2. **Evaluate**: Tests agent on BDD scenarios
3. **Optimize**: GEPA improves both agent profile AND task config together
4. **Re-evaluate**: Tests improved combined variable

---

## Advanced Configuration

### Multi-Task Agents

```yaml
persona:
  role: Research Analyst
  goal: Conduct comprehensive research
  backstory: Expert analyst with methodology expertise

tasks:
  - name: research
    description: Research the topic thoroughly
    expected_output: Detailed research findings
  
  - name: analyze
    description: Analyze the research findings
    expected_output: Analytical insights and recommendations
```

GEPA optimizes each task's description and expected_output along with the agent profile.

### Custom Tools Integration

```yaml
persona:
  role: Data Analyst
  tools:
    - web_search
    - calculator
    - file_reader

tasks:
  - name: analyze_data
    description: Analyze data using available tools
    expected_output: Data analysis report with charts
```

---

## How GEPA Parses Combined Variables

GEPA automatically extracts and updates:

```python
# Example parsing
combined_profile = """
Role: Content Creator
Goal: Create content
Backstory: Expert writer

Task Description: Write about topic
Expected Output: Article
"""

# GEPA extracts:
role = extract("Role:", profile)
goal = extract("Goal:", profile)
backstory = extract("Backstory:", profile)
task_description = extract("Task Description:", profile)
expected_output = extract("Expected Output:", profile)

# GEPA optimizes each, then recombines
```

---

## Optimization Results

### Example: Content Creator

**Baseline:**
```
Pass Rate: 75% (3/4 scenarios)
Average Quality: 7.2/10
```

**After Combined Optimization:**
```
Pass Rate: 100% (4/4 scenarios)  ← +25%
Average Quality: 9.5/10           ← +2.3 points
```

**Improvements:**
- More specific and targeted role
- Clearer goal with measurable outcomes
- Richer backstory with relevant expertise
- Detailed task instructions
- Structured expected output specifications

---

## Best Practices

### Define Clear Tasks

```yaml
# Good: Specific task
tasks:
  - name: write_article
    description: Write a 1000-word article about {topic} with examples
    expected_output: Article with intro, body, conclusion, examples

# Bad: Vague task
tasks:
  - name: write
    description: Write something
    expected_output: Text
```

### Match Agent to Task

```yaml
# Agent expertise should match task requirements
persona:
  role: Technical Writer        # ← Matches task
  backstory: Expert in technical documentation

tasks:
  - name: write_docs
    description: Write technical documentation  # ← Matches agent
```

### Use BDD Scenarios

```yaml
feature_specifications:
  scenarios:
    - name: Test real use case
      input:
        topic: "Actual topic you'll use"
      expected_output:
        article: "Actual format you need"
```

### Start Simple, Optimize

```yaml
# Start with basic task
tasks:
  - description: Research topic
    expected_output: Research report

# Let GEPA optimize to:
# description: "Conduct systematic research on {topic} including..."
# expected_output: "Comprehensive report with: executive summary, findings, recommendations..."
```

---

## Backward Compatibility

### Agent-Only Optimization

Old playbooks still work! If you don't specify tasks, GEPA optimizes agent profile only:

```yaml
# Agent-only (still supported)
persona:
  role: Assistant
  goal: Help users
  backstory: Helpful agent
# No tasks section - uses agent profile only
```

### Combined Optimization

New playbooks with tasks get combined optimization:

```yaml
# Combined (recommended)
persona:
  role: Assistant
  goal: Help users
  backstory: Helpful agent

tasks:
  - description: "Detailed task..."
    expected_output: "Specific output..."
# Has tasks section - uses combined optimization
```

---

## Example: Research Agent

### Initial Configuration

```yaml
persona:
  role: Researcher
  goal: Find information
  backstory: Research professional

tasks:
  - description: Research topic
    expected_output: Research results
```

**Initial Results**: 60% pass rate

### After Optimization

```yaml
persona:
  role: Senior Research Analyst with academic methodology expertise
  goal: Conduct comprehensive, evidence-based research with systematic approach
  backstory: Distinguished research professional with PhD-level training...

tasks:
  - description: |
      Conduct systematic research on {topic}:
      1. Identify key sources
      2. Analyze credibility
      3. Extract insights
      4. Synthesize findings
      5. Provide citations
    expected_output: |
      Comprehensive research report containing:
      - Executive summary
      - Methodology explanation
      - Key findings with evidence
      - Analysis and insights
      - Recommendations
      - Full source citations
```

**Optimized Results**: 95% pass rate (+35%)

---

## CLI Commands

```bash
# Basic workflow
super agent pull content_creator_crew
super agent compile content_creator_crew
super agent evaluate content_creator_crew
super agent optimize content_creator_crew --auto medium
super agent evaluate content_creator_crew  # automatically loads optimized weights

# Advanced options
super agent optimize content_creator_crew \
  --auto intensive \
  --reflection-lm qwen3:8b \
  --minibatch-size 5

# Run optimized agent
super agent run content_creator_crew  # automatically loads optimized weights
```

---

## Troubleshooting

### Issue: Low Pass Rate After Optimization

**Solution**: Check BDD scenarios are realistic

```yaml
# Good scenarios
scenarios:
  - input: {topic: "AI agents"}
    expected_output:
      article: "Article about AI agents"
      expected_keywords: ["AI", "agents", "automation"]
```

### Issue: Agent Not Using Task Instructions

**Solution**: Ensure tasks are properly defined in playbook

```yaml
# Must have tasks section
tasks:
  - name: my_task
    description: "Clear description"
    expected_output: "Specific output format"
```

---

## Next Steps

1. **Try combined optimization**: Pull `content_creator_crew` demo
2. **Create your own**: Add tasks to your CrewAI playbooks
3. **Compare results**: Test agent-only vs combined optimization
4. **Read more**: See [CrewAI Integration Guide](crewai-integration.md)

### Related Guides

- [CrewAI Integration](crewai-integration.md)
- [GEPA Optimization](gepa-optimization.md)
- [Multi-Framework Guide](multi-framework.md)
- [Evaluation & Testing](evaluation-testing.md)

---

**CrewAI with SuperOptiX offers the most advanced agent + task optimization available!**
