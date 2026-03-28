# Code Review Assistant - Setup Guide

**Quick Setup**: Get the Code Review Assistant working in under 5 minutes!

---

## 🚀 **Quick Start** (3 Commands)

```bash
# 1. Initialize project
super init my_demo
cd my_demo

# 2. Pull the agent
super agent pull code_review_assistant

# 3. Run setup script
python -m superoptix.agents.demo.setup_code_review
```

**That's it!** The setup script automatically copies the knowledge base and dataset.

---

## 📋 **Manual Setup** (If Script Doesn't Work)

### **Step 1: Pull the Agent**
```bash
super agent pull code_review_assistant
```

### **Step 2: Pull the Dataset**
```bash
super dataset pull code_review_examples
```

This copies `code_review_examples.csv` to `./data/`

### **Step 3: Copy Knowledge Base**

Find your SuperOptiX installation:
```bash
python -c "import superoptix; from pathlib import Path; print(Path(superoptix.__file__).parent)"
```

Then copy the knowledge base:
```bash
# Replace /path/to/ with your actual path
cp -r /path/to/superoptix/knowledge/code_review ./knowledge/
```

---

## ✅ **Verification**

After setup, you should have:

```
my_demo/
├── agents/
│   └── code_review_assistant/
│       └── playbook/
│           └── code_review_assistant_playbook.yaml
├── knowledge/
│   └── code_review/
│       ├── security/
│       │   ├── sql_injection.md
│       │   ├── hardcoded_secrets.md
│       │   └── xss_prevention.md
│       ├── python/
│       │   ├── error_handling.md
│       │   └── naming_conventions.md
│       ├── performance/
│       │   └── time_complexity.md
│       └── best_practices/
│           ├── code_smells.md
│           └── solid_principles.md
└── data/
    └── code_review_examples.csv
```

**Verify with**:
```bash
ls -la knowledge/code_review/  # Should show 4 directories
ls -la data/                    # Should show code_review_examples.csv
```

---

## 🎯 **Run the Demo**

```bash
# Compile
super agent compile code_review_assistant

# Evaluate baseline
super agent evaluate code_review_assistant
# Expected: ~37% accuracy

# Optimize
super agent optimize code_review_assistant --auto medium --fresh
# Watch GEPA optimize RAG + Tools + Prompts

# Re-evaluate
super agent evaluate code_review_assistant
# Expected: ~87% accuracy (+50%!)

# Run live
super agent run code_review_assistant
```

---

## 🆘 **Troubleshooting**

### **"Knowledge base not found" error**

**Option A**: Use absolute path in playbook

1. Find your SuperOptiX installation:
   ```bash
   python -c "import superoptix; from pathlib import Path; print(Path(superoptix.__file__).parent / 'knowledge/code_review')"
   ```

2. Edit `agents/code_review_assistant/playbook/code_review_assistant_playbook.yaml`:
   ```yaml
   rag:
     knowledge_base:
       - /absolute/path/to/superoptix/knowledge/code_review/python/*.md
       - /absolute/path/to/superoptix/knowledge/code_review/security/*.md
       - /absolute/path/to/superoptix/knowledge/code_review/performance/*.md
       - /absolute/path/to/superoptix/knowledge/code_review/best_practices/*.md
   ```

**Option B**: Copy manually
```bash
# Find source
python -c "import superoptix; from pathlib import Path; print(Path(superoptix.__file__).parent)"

# Copy
cp -r /path/from/above/knowledge/code_review ./knowledge/
```

### **"Dataset not found" error**

Pull from marketplace:
```bash
super dataset pull code_review_examples
```

Or copy manually:
```bash
# Find source
python -c "import superoptix; from pathlib import Path; print(Path(superoptix.__file__).parent / 'datasets/examples/code_review_examples.csv')"

# Copy
mkdir -p data
cp /path/from/above/code_review_examples.csv ./data/
```

### **"ChromaDB not installed" error**
```bash
pip install chromadb sentence-transformers
```

### **"Ollama model not found" error**
```bash
ollama pull qwen3.5:9b
```

---

## 📊 **What Gets Installed**

### **Knowledge Base** (9 files, ~50 KB)
- **Security**: SQL injection, hardcoded secrets, XSS prevention
- **Python**: Error handling, naming conventions (PEP 8)
- **Performance**: Time complexity, optimization patterns
- **Best Practices**: Code smells, SOLID principles

### **Dataset** (1 file, ~25 KB)
- **50+ code review examples** from real GitHub patterns
- **Categories**: security, performance, style, best practices, code smells
- **Severities**: critical, high, medium, low, info
- **Languages**: Python (extensible to others)

---

## 🎬 **For ODSC Demo**

See complete demo script:
- **File**: `superoptix/agents/demo/ODSC_CODE_REVIEW_DEMO.md`
- **Duration**: 10 minutes
- **Expected improvement**: 37% → 87% accuracy

---

## 💡 **Pro Tips**

### **Use Package Path** (No copying needed!)
```yaml
# In playbook, replace relative paths with package paths:
rag:
  knowledge_base:
    - /full/path/to/superoptix/knowledge/code_review/**/*.md
```

Find path with:
```bash
python -c "import superoptix; from pathlib import Path; print(Path(superoptix.__file__).parent / 'knowledge/code_review')"
```

### **Add Your Own Knowledge**
```bash
# Add company-specific coding standards
mkdir -p knowledge/code_review/custom
echo "# Our Python Standards..." > knowledge/code_review/custom/company_standards.md
```

Then in playbook:
```yaml
rag:
  knowledge_base:
    - ./knowledge/code_review/**/*.md  # Includes custom/
```

### **Extend the Dataset**
```bash
# Add more code review examples
cat >> data/code_review_examples.csv << 'EOF'
"def process():
    data = fetch()
    return transform(data)","Add type hints and docstring for better code documentation.",low,documentation,python
EOF
```

---

## 🚀 **All-in-One Setup Command**

```bash
# Complete setup in one go
super init my_demo && \
cd my_demo && \
super agent pull code_review_assistant && \
super dataset pull code_review_examples && \
python -c "
import shutil
from pathlib import Path
import superoptix

src = Path(superoptix.__file__).parent / 'knowledge/code_review'
dst = Path.cwd() / 'knowledge/code_review'
dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(src, dst)
print('✅ Setup complete!')
" && \
super agent compile code_review_assistant && \
echo "✨ Ready to demo!"
```

---

## 📖 **Next Steps**

1. ✅ Setup complete → Run evaluation
2. 📊 Baseline: ~37% → Optimize with GEPA
3. 🚀 Optimized: ~87% → Demo ready!

See full workflow: `ODSC_CODE_REVIEW_DEMO.md`

---

**Questions? Issues?**  
- GitHub: github.com/superagentic/SuperOptiX/issues
- Discord: superoptix.ai/discord

**Good luck with your demo!** 🎉

