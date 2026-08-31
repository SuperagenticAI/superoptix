# ODSC AI West 2025 - Code Review Assistant Demo

**Agent**: Code Review Assistant  
**Duration**: 10 minutes  
**Audience**: Software Engineers, ML Engineers, Data Scientists  
**Features Demonstrated**: RAG + Tools + Datasets + GEPA Optimization

---

## 🎯 **Demo Objective**

Show how SuperOptiX optimizes an **entire agentic pipeline** (not just prompts) using a universally-understood use case: **code review**.

**Key Message**: "While others optimize prompts, SuperOptiX optimizes prompts + RAG retrieval + tool usage + training data"

---

## 📋 **Pre-Demo Setup** (Do Before Presentation)

### 1. Initialize Project
```bash
cd ~
super init odsc_demo
cd odsc_demo
```

### 2. Copy Agent Files
```bash
# Copy the demo agent
cp -r /path/to/superoptix/agents/demo/code_review_assistant_playbook.yaml \
    agents/code_review_assistant/playbook/

# Copy knowledge base
cp -r /path/to/swe/knowledge ./

# Copy dataset
cp /path/to/swe/data/code_review_dataset.csv ./data/
```

### 3. Ensure Ollama is Running
```bash
ollama list  # Verify qwen3.5:9b is installed
ollama pull qwen3.5:9b  # If not installed
```

### 4. Test Compile (5 min before talk)
```bash
super agent compile code_review_assistant
# Verify it compiles successfully
```

---

## 🎬 **LIVE DEMO SCRIPT** (10 minutes)

### **ACT 1: The Hook** (1 min)

**SAY**:  
"Raise your hand if you've ever written code that looked like this..."

**SHOW SLIDE** (Bad Code Example):
```python
def get_user(username):
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    return db.execute(query)
```

[Wait for chuckles/groans]

**SAY**:  
"SQL injection - still the #1 OWASP vulnerability in 2025. We need better code review.  
But here's the thing: optimizing AI code reviewers isn't just about prompt engineering.  
Let me show you what I mean."

---

### **ACT 2: Show the Agent** (2 min)

**SAY**:  
"This is our Code Review Assistant. Let me show you what makes it interesting."

#### **Command 1**: Show Configuration
```bash
cat agents/code_review_assistant/playbook/code_review_assistant_playbook.yaml
```

**SCROLL TO**:
```yaml
# RAG Configuration
rag:
  enabled: true
  knowledge_base:
    - ./knowledge/security/*.md
    - ./knowledge/python/*.md
    - ./knowledge/best_practices/*.md

# Tools Configuration
tools:
  enabled: true
  specific_tools:
    - complexity_calculator
    - security_scanner
    - performance_analyzer

# External Dataset
datasets:
  - name: github_code_reviews
    source: ./data/code_review_dataset.csv
    limit: 100
```

**SAY**:  
"See that? RAG for best practices, tools for analysis, and trained on 100 real GitHub code reviews.  
This agent doesn't just generate text - it retrieves knowledge, runs analysis, and learns from data."

---

### **ACT 3: Baseline Performance** (2 min)

**SAY**:  
"Let's see how well it works out of the box."

#### **Command 2**: Evaluate Baseline
```bash
super agent evaluate code_review_assistant
```

**EXPECTED OUTPUT** (show on screen):
```
🔍 Evaluating Code Review Assistant...

Testing 8 BDD scenarios:

❌ SQL Injection Detection: FAIL
   Expected: Detect SQL injection with parameterized solution
   Got: Generic "check your SQL" response

✅ Complexity Analysis: PASS

❌ Security + Hardcoded Credentials: FAIL
   Expected: Identify hardcoded secrets
   Got: Missed the API key

✅ Performance - Nested Loop: PASS

❌ Multiple Issues: FAIL
   Expected: Comprehensive review of all issues
   Got: Only found 2 out of 4 issues

❌ Error Handling: FAIL

✅ Code Duplication: PASS

❌ Best Practices: FAIL

────────────────────────────────────────────────
Overall: 3/8 PASS (37.5%)
────────────────────────────────────────────────
```

**SAY**:  
"37.5% accuracy. Not production-ready.  
Why? Because the baseline prompts don't know WHEN to search docs, WHEN to use tools, or HOW to combine findings.  
Let's fix that."

---

### **ACT 4: GEPA Optimization** (3 min)

**SAY**:  
"Now watch GEPA - Genetic-Pareto - optimize this entire pipeline."

#### **Command 3**: Optimize
```bash
super agent optimize code_review_assistant --auto medium --fresh
```

**EXPECTED OUTPUT** (narrate as it runs):
```
🔄 GEPA Optimization Starting...
📊 Training on 100 code review examples from dataset

Iteration 1/10:
  Baseline accuracy: 37.5%
  Testing candidate prompts...
  Current best: 37.5%

Iteration 2/10:
  Testing improved prompts...
  Current best: 50.0% (+12.5%)
  
Iteration 3/10:
  🧠 REFLECTION: "Need to search security docs before analyzing SQL queries"
  Adjusting RAG retrieval strategy...
  Current best: 62.5% (+25%)

Iteration 5/10:
  🧠 REFLECTION: "Should use complexity_calculator for nested conditions"
  Optimizing tool selection logic...
  Current best: 75.0% (+37.5%)

Iteration 7/10:
  🧠 REFLECTION: "Combine findings from multiple tools for comprehensive review"
  Current best: 87.5% (+50%)

Iteration 9/10:
  🧠 REFLECTION: "Always check knowledge base for code smell patterns"
  Current best: 87.5%

Iteration 10/10:
  Final accuracy: 87.5%

✅ Optimization Complete!
   Improvement: +50% (37.5% → 87.5%)
   
💾 Saving optimized weights to:
   agents/code_review_assistant/optimized/code_review_assistant.json
```

**SAY (during optimization)**:  
"See those reflections? GEPA isn't just tuning prompts - it's learning:  
- WHEN to search the knowledge base  
- WHICH tools to use for each issue  
- HOW to combine multiple findings  

This is what I mean by optimizing the ENTIRE pipeline."

---

### **ACT 5: Re-Evaluation** (1 min)

**SAY**:  
"Let's see if it actually learned."

#### **Command 4**: Re-evaluate
```bash
super agent evaluate code_review_assistant
```

**EXPECTED OUTPUT**:
```
🔍 Evaluating Optimized Code Review Assistant...

Testing 8 BDD scenarios:

✅ SQL Injection Detection: PASS
   ✓ Identified SQL injection
   ✓ Suggested parameterized queries
   ✓ Cited OWASP documentation

✅ Complexity Analysis: PASS
   ✓ Calculated cyclomatic complexity
   ✓ Suggested refactoring strategies

✅ Security + Hardcoded Credentials: PASS
   ✓ Found hardcoded API key
   ✓ Recommended environment variables

✅ Performance - Nested Loop: PASS
   ✓ Identified O(n²) complexity
   ✓ Suggested O(n) solution with Counter

✅ Multiple Issues: PASS
   ✓ Comprehensive review with all 4 issues
   ✓ Prioritized by severity

✅ Error Handling: PASS
   ✓ Recommended try-except blocks
   ✓ Cited error handling best practices

✅ Code Duplication: PASS
   ✓ Detected DRY violation
   ✓ Suggested extraction

❌ Best Practices: FAIL
   (Still room for improvement!)

────────────────────────────────────────────────
Overall: 7/8 PASS (87.5%)
Improvement: +50% (37.5% → 87.5%)
────────────────────────────────────────────────
```

**SAY**:  
"87.5% accuracy. Production-ready.  
From vague responses to detailed, actionable reviews with code examples."

---

### **ACT 6: Live Query** (1 min)

**SAY**:  
"Let me show you what that looks like in practice."

#### **Command 5**: Run Live Query
```bash
super agent run code_review_assistant
```

**INPUT** (paste this):
```python
password = "admin123"
def login(user):
    query = "SELECT * FROM users WHERE username='" + user + "'"
    result = db.execute(query)
    if result:
        if result['password'] == password:
            if result['active']:
                if result['verified']:
                    return True
    return False
```

**EXPECTED OUTPUT**:
```
🔍 Code Review Results
═══════════════════════════════════════════════════════

SEVERITY: 🔴 CRITICAL

📋 FINDINGS:

1. **SQL Injection Vulnerability** 🔴 CRITICAL
   Line: query = "SELECT * FROM users WHERE username='" + user + "'"
   
   Issue: User input concatenated directly into SQL query
   
   Solution:
   ```python
   query = "SELECT * FROM users WHERE username = ?"
   result = db.execute(query, (user,))
   ```
   
   [Retrieved from: knowledge/security/sql_injection.md]
   [OWASP Rank: #1 Web Security Risk]

2. **Hardcoded Credentials** 🔴 CRITICAL
   Line: password = "admin123"
   
   Issue: Sensitive credentials stored in code
   
   Solution:
   ```python
   import os
   PASSWORD = os.environ.get('ADMIN_PASSWORD')
   ```
   
   [Retrieved from: knowledge/security/hardcoded_secrets.md]
   [CVSS Score: 9.0+]

3. **High Cyclomatic Complexity** 🟡 MEDIUM
   Function: login()
   Complexity: 5 (threshold: 4)
   
   [Calculated by: complexity_calculator tool]
   
   Issue: Too many nested conditions
   
   Solution: Use early returns:
   ```python
   if not result:
       return False
   if result['password'] != password:
       return False
   if not result['active']:
       return False
   if not result['verified']:
       return False
   return True
   ```
   
   [Retrieved from: knowledge/best_practices/code_smells.md]

4. **Plain Text Password Comparison** 🔴 CRITICAL
   Line: if result['password'] == password
   
   Issue: Passwords should be hashed, never compared as plain text
   
   Solution:
   ```python
   import bcrypt
   if bcrypt.checkpw(password.encode(), result['password_hash']):
       return True
   ```

═══════════════════════════════════════════════════════

📊 METRICS:
   Security Issues: 3
   Performance Issues: 0
   Maintainability Issues: 1
   Lines Analyzed: 11
   Review Time: 2.3s

🎯 RECOMMENDATIONS:
   Priority 1: Fix SQL injection (CRITICAL)
   Priority 2: Remove hardcoded password (CRITICAL)
   Priority 3: Hash password comparison (CRITICAL)
   Priority 4: Reduce complexity (MEDIUM)

📚 REFERENCES:
   - OWASP Top 10: https://owasp.org/Top10
   - SQL Injection Prevention: [local knowledge base]
   - Cyclomatic Complexity: [analysis tools]
```

**SAY**:  
"See that? It:  
1. Searched security docs (RAG)  
2. Calculated complexity (Tool)  
3. Provided executable solutions  
4. Prioritized by severity  
5. Cited sources  

All because we optimized HOW it retrieves, WHEN it analyzes, and WHAT it recommends."

---

## 🎤 **CLOSING** (30 seconds)

**SAY**:  
"So what just happened here?  

We went from 37% to 87% accuracy - not by manually tuning prompts, but by letting GEPA optimize:  
✓ RAG retrieval strategies  
✓ Tool selection logic  
✓ Response synthesis  
✓ All trained on real GitHub data  

This is what I mean by 'The Optimization Layer for Agentic AI.'  

Other tools optimize prompts. SuperOptiX optimizes the ENTIRE pipeline.  

And it works across any framework - DSPy, LangChain, CrewAI, your custom stack.  

Thank you!"

[END]

---

## 📊 **Key Metrics to Emphasize**

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Accuracy | 37.5% | 87.5% | +50% |
| Security Detection | 33% | 100% | +67% |
| Actionable Recommendations | Low | High | +++  |

---

## 🎯 **Talking Points During Q&A**

### "How does this compare to GitHub Copilot?"
"Copilot suggests code. This reviews it. Complementary, not competitive. Plus, Copilot doesn't optimize itself - this does."

### "Can it handle other languages?"
"Yes! The playbook configures Python, but the same approach works for JavaScript, Java, Go, etc. Just add language-specific knowledge bases."

### "How long does optimization take?"
"10 iterations took ~5 minutes. For production, you'd run overnight with more data. One-time cost for ongoing improvement."

### "What if I don't use DSPy?"
"Universal GEPA works with any framework. We have adapters for LangChain, CrewAI, Semantic Kernel, and you can build custom adapters."

### "Does it work offline?"
"Yes! Using local Ollama models, local vector database (ChromaDB), and local optimization. No API calls required."

### "Can it learn from our internal code standards?"
"Absolutely! Just add your coding standards to the knowledge base. The agent will retrieve and apply them during reviews."

---

## 🚀 **Follow-Up Demo Options** (If Time Permits)

### Option 1: Show Configuration Flexibility
```bash
# Show how easy it is to customize
vim agents/code_review_assistant/playbook/code_review_assistant_playbook.yaml

# Point out:
# - Can change model (qwen3.5:2b -> qwen3.5:9b)
# - Can add more knowledge sources
# - Can adjust optimization parameters
```

### Option 2: Show Observability
```bash
# Show what was tracked
super observe dashboard

# Point out:
# - Traces of each evaluation
# - GEPA optimization metrics
# - Tool usage patterns
```

### Option 3: Show Dataset Marketplace
```bash
# Show how to get more training data
super dataset list

# Pull additional code review examples
super dataset pull code_review_examples
```

---

## 🎁 **Leave-Behind Resources**

**SAY at end**:  
"Want to try this yourself?  

1. **Installation**:  
   ```bash
   uv pip install superoptix
   super init my_project
   super agent pull code_review_assistant
   ```

2. **Documentation**:  
   GitHub: github.com/superagentic/SuperOptiX  
   Docs: superoptix.ai/docs  

3. **Join Community**:  
   Discord: superoptix.ai/discord  
   Twitter: @SuperOptiX  

Thank you!"

---

## 📝 **Preparation Checklist**

### **1 Week Before**:
- [ ] Test full workflow end-to-end
- [ ] Verify all commands work
- [ ] Practice timing (should be <10 min)
- [ ] Prepare backup slides if demo fails

### **1 Day Before**:
- [ ] Test on presentation laptop
- [ ] Verify internet connection (for Ollama pull)
- [ ] Have backup: pre-recorded video
- [ ] Test projector/screen sharing

### **1 Hour Before**:
- [ ] Start Ollama
- [ ] Verify qwen3.5:9b is loaded
- [ ] Do a quick test compile
- [ ] Clear terminal history
- [ ] Set terminal font size (big!)

### **During Demo**:
- [ ] Speak slowly (audience following terminal)
- [ ] Pause for effect during GEPA reflections
- [ ] Point out key concepts on screen
- [ ] Make eye contact, not just terminal
- [ ] Have fun!

---

## 🎬 **Backup Plan** (If Live Demo Fails)

### Option 1: Pre-recorded Video
Have a 5-minute video showing the full workflow

### Option 2: Slides with Screenshots
Show static screenshots of each step with narration

### Option 3: Code Walkthrough
If network fails, show the generated code and explain what would happen

**Important**: Always have a backup. Live demos are risky!

---

## 🎯 **Success Metrics**

**You nailed it if**:
- ✅ Audience understands "optimizing the entire pipeline"
- ✅ Clear visual improvement (37% → 87%)
- ✅ At least 3 questions during Q&A
- ✅ Someone tweets/posts about it
- ✅ GitHub stars increase after talk

---

**Good luck! You've got this! 🚀**

**Remember**: The goal isn't a perfect demo. The goal is showing the *concept* of end-to-end optimization in a way everyone understands.

---

**TOTAL TIME**: 10 minutes  
**COMPLEXITY**: Medium  
**IMPACT**: 🔥🔥🔥🔥🔥 (Maximum!)
