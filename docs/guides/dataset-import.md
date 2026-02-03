# Dataset Import Guide

Import external datasets for agent training and evaluation, scaling beyond YAML scenarios to thousands of examples.

---

## 🎯 **Overview**

SuperOptiX now supports importing external datasets in addition to BDD scenarios. This allows you to:
- ✅ Use existing datasets (CSV, JSON, Parquet, HuggingFace)
- ✅ Scale to 10,000+ examples (vs 5-10 YAML scenarios)
- ✅ Leverage standard ML workflows
- ✅ Access HuggingFace's 100,000+ datasets
- ✅ Mix datasets with BDD scenarios for best results

---

## 🚀 **Quick Start**

### **1. Create a Dataset**

```bash
# Create CSV file
cat << 'EOF' > data/sentiment_train.csv
text,label
"This is amazing!",positive
"This is terrible",negative
"It's okay",neutral
EOF
```

### **2. Configure in Playbook**

```yaml
# agent_playbook.yaml
spec:
  datasets:
    - name: training_data
      source: ./data/sentiment_train.csv
      format: csv
      mapping:
        input: text
        output: label
        input_field_name: text
        output_field_name: sentiment
      limit: 1000
      shuffle: true
```

### **3. Preview Dataset**

```bash
super agent dataset preview my_agent --limit 5
```

### **4. Use It**

```bash
super agent compile my_agent
# → 📊 Loaded 1000 examples from dataset!

super agent evaluate my_agent
# → Uses all 1000 examples!

super agent optimize my_agent --auto light
# → GEPA trains on all 1000 examples!
```

---

## 📋 **Supported Formats**

### **CSV Files**

```yaml
datasets:
  - name: csv_training
    source: ./data/train.csv
    format: csv
    mapping:
      input: text_column
      output: label_column
      input_field_name: text
      output_field_name: sentiment
    limit: 5000
    shuffle: true
```

**Requirements**: pandas (already installed)

---

### **JSON Files**

```yaml
datasets:
  - name: json_training
    source: ./data/train.json
    format: json
    mapping:
      input: question_field
      output: answer_field
```

**JSON Format**:
```json
[
  {"question": "What is AI?", "answer": "Artificial Intelligence"},
  {"question": "What is ML?", "answer": "Machine Learning"}
]
```

---

### **JSONL Files** (Recommended for Large Datasets)

```yaml
datasets:
  - name: jsonl_training
    source: ./data/train.jsonl
    format: jsonl
    mapping:
      input: text
      output: label
    limit: 10000
```

**JSONL Format** (one JSON per line):
```jsonl
{"text": "Great product!", "label": "positive"}
{"text": "Poor quality", "label": "negative"}
{"text": "It's okay", "label": "neutral"}
```

---

### **Parquet Files** (Best for Big Data)

```yaml
datasets:
  - name: parquet_training
    source: ./data/train.parquet
    format: parquet
    mapping:
      input: text
      output: label
```

**Requirements**: pandas, pyarrow (already installed)

**Benefits**:
- Compressed (smaller files)
- Fast loading
- Preserves data types
- Industry standard for big data

---

### **HuggingFace Datasets** 🔥

```yaml
datasets:
  - name: imdb_sentiment
    source: huggingface:imdb
    format: huggingface
    mapping:
      input: text
      output: label
    split: train
    limit: 10000
    shuffle: true
```

**Popular Datasets**:
- `huggingface:imdb` - Movie reviews (50K)
- `huggingface:ag_news` - News classification (120K)
- `huggingface:sst2` - Sentiment (67K)
- `huggingface:squad` - Q&A (87K)
- `huggingface:glue:sst2` - With subset
- ... 100,000+ more!

**Requirements**: `pip install datasets`

---

## 🎯 **Advanced Usage**

### **Multi-Column Mapping**

```yaml
datasets:
  - name: qa_dataset
    source: ./data/qa.csv
    format: csv
    mapping:
      input:
        question: question_column
        context: context_column
      output:
        answer: answer_column
        confidence: confidence_column
```

---

### **Multiple Datasets**

```yaml
datasets:
  # Training data
  - name: train_set
    source: ./data/train.csv
    format: csv
    mapping: {input: text, output: label}
    limit: 10000
  
  # Test data
  - name: test_set
    source: ./data/test.csv
    format: csv
    mapping: {input: text, output: label}
    limit: 1000
  
  # HuggingFace data
  - name: hf_data
    source: huggingface:imdb
    format: huggingface
    mapping: {input: text, output: label}
    split: train
    limit: 5000
```

**Result**: 16,000 total examples!

---

### **Mix Datasets + BDD Scenarios** (Recommended!)

```yaml
# Bulk training data from datasets
datasets:
  - name: training_data
    source: ./data/large_dataset.csv
    format: csv
    mapping: {input: text, output: label}
    limit: 10000

# Specific edge cases from BDD scenarios
feature_specifications:
  scenarios:
  - name: sarcasm_test
    input: {text: "Oh great, another bug"}
    expected_output: {sentiment: negative}
  
  - name: mixed_sentiment
    input: {text: "Good product but poor service"}
    expected_output: {sentiment: neutral}
```

**Benefits**:
- 10,000 examples for robust training
- Specific edge cases for testing
- Best of both worlds!

---

## 🛠️ **CLI Commands**

### **Preview Dataset**

```bash
super agent dataset preview my_agent --limit 10
```

**Output**:
```
Preview: training_data (showing 10 of 5000)
╭──────┬────────────────────────────┬───────────────╮
│ #    │ Input: text                │ Output: label │
├──────┼────────────────────────────┼───────────────┤
│ 1    │ This is amazing!           │ positive      │
│ 2    │ Terrible experience        │ negative      │
│ ...  │ ...                        │ ...           │
╰──────┴────────────────────────────┴───────────────╯
```

---

### **Dataset Info**

```bash
super agent dataset info my_agent
```

**Output**:
```
╭──────────────────── 📊 training_data ────────────────────╮
│ Name: training_data                                      │
│ Source: ./data/train.csv                                 │
│ Format: csv                                              │
│ Total Examples: 5000                                     │
│ Split: train                                             │
│ Shuffled: True                                           │
│ Input Fields: text                                       │
│ Output Fields: sentiment                                 │
╰──────────────────────────────────────────────────────────╯

Total Examples Across All Datasets: 5000
```

---

### **Validate Dataset**

```bash
super agent dataset validate my_agent
```

**Output**:
```
Validating 1 dataset(s)...
✅ training_data: Valid
✅ All datasets valid!
```

---

## 📊 **Examples**

### **Example 1: Sentiment Analysis with CSV**

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Sentiment Analyzer
  id: sentiment_analyzer
spec:
  language_model:
    model: llama3.1:8b
  
  input_fields:
  - name: text
    type: string
  
  output_fields:
  - name: sentiment
    type: string
  
  datasets:
  - name: reviews
    source: ./data/customer_reviews.csv
    format: csv
    mapping:
      input: review_text
      output: sentiment_label
      input_field_name: text
      output_field_name: sentiment
    limit: 5000
    shuffle: true
  
  tasks:
  - name: classify
    instruction: Classify sentiment as positive, negative, or neutral
```

---

### **Example 2: Q&A with HuggingFace**

```yaml
spec:
  datasets:
  - name: squad_qa
    source: huggingface:squad
    format: huggingface
    mapping:
      input:
        question: question
        context: context
      output:
        answer: answer
    split: train
    limit: 10000
```

---

### **Example 3: Multi-Format Mix**

```yaml
datasets:
  # Main training data (CSV)
  - name: main_training
    source: ./data/train.csv
    format: csv
    mapping: {input: text, output: label}
    limit: 8000
  
  # Validation data (JSON)
  - name: validation
    source: ./data/val.json
    format: json
    mapping: {input: text, output: label}
    limit: 1000
  
  # External data (HuggingFace)
  - name: external
    source: huggingface:sst2
    format: huggingface
    mapping: {input: sentence, output: label}
    split: train
    limit: 5000
```

**Total**: 14,000 examples from 3 sources!

---

## 🎓 **Best Practices**

### **1. Start Small, Scale Up**

```yaml
# Development
datasets:
  - source: ./data/train.csv
    limit: 100  # Small for fast iteration

# Production
datasets:
  - source: ./data/train.csv
    limit: 10000  # Full dataset
```

---

### **2. Always Shuffle**

```yaml
datasets:
  - shuffle: true  # Prevents ordering bias
```

---

### **3. Use Limits**

```yaml
datasets:
  - limit: 5000  # Control training time/cost
```

---

### **4. Validate First**

```bash
super agent dataset validate my_agent
super agent dataset preview my_agent
super agent dataset info my_agent
```

---

### **5. Mix Datasets + BDD**

```yaml
datasets:        # Bulk data
  - source: ./data/train.csv
    limit: 5000

feature_specifications:  # Edge cases
  scenarios:
  - name: edge_case_1
  - name: edge_case_2
```

---

## 🔧 **Troubleshooting**

### **Issue: File Not Found**

```
❌ Failed to load dataset: No such file or directory
```

**Fix**: Use absolute paths or check relative path from playbook location

```yaml
# Use absolute path
source: /full/path/to/data.csv

# Or relative from playbook location
source: ../../data/data.csv
```

---

### **Issue: Column Not Found**

```
❌ Error: Column 'text_column' not found
```

**Fix**: Check your CSV/JSON column names match mapping

```bash
# Check column names
head -1 data.csv

# Update mapping to match
mapping:
  input: actual_column_name  # Must match CSV header
```

---

### **Issue: Import Error**

```
❌ Dataset import feature not available
```

**Fix**: Reinstall SuperOptiX

```bash
cd /path/to/SuperOptiX
pip install -e .
```

---

### **Issue: HuggingFace Download Slow**

```yaml
# Use limit for faster download
datasets:
  - source: huggingface:imdb
    limit: 1000  # Downloads only 1000 examples
```

---

## 📚 **Complete Example: Production Sentiment Analyzer**

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Production Sentiment Analyzer
  id: sentiment_prod
  namespace: analysis
  version: 2.0.0
spec:
  language_model:
    provider: ollama
    model: llama3.1:8b
    temperature: 0.3
  
  input_fields:
  - name: text
    type: string
  
  output_fields:
  - name: sentiment
    type: string
  
  # Import 15,000 examples from 3 sources!
  datasets:
  # Custom CSV data (8,000 examples)
  - name: customer_reviews
    source: ./data/reviews_2024.csv
    format: csv
    mapping:
      input: review_text
      output: sentiment_label
      input_field_name: text
      output_field_name: sentiment
    limit: 8000
    shuffle: true
  
  # Validation data (2,000 examples)
  - name: validation_set
    source: ./data/validation.jsonl
    format: jsonl
    mapping:
      input: text
      output: label
      input_field_name: text
      output_field_name: sentiment
    limit: 2000
  
  # HuggingFace IMDB dataset (5,000 examples)
  - name: imdb_reviews
    source: huggingface:imdb
    format: huggingface
    mapping:
      input: text
      output: label
      input_field_name: text
      output_field_name: sentiment
    split: train
    limit: 5000
  
  # Keep BDD scenarios for edge cases
  feature_specifications:
    scenarios:
    - name: sarcasm_detection
      input: {text: "Oh great, another delay"}
      expected_output: {sentiment: negative}
    
    - name: mixed_sentiment
      input: {text: "Good food but slow service"}
      expected_output: {sentiment: neutral}
  
  tasks:
  - name: analyze
    instruction: Classify sentiment as positive, negative, or neutral
  
  optimization:
    optimizer:
      name: GEPA
      params:
        auto: medium  # More data = use medium budget
        reflection_lm: llama3.1:8b
```

**Result**: 15,002 total examples (15,000 from datasets + 2 BDD scenarios)!

---

## 🎬 **Demo Workflow**

```bash
# 1. Preview your data
super agent dataset preview sentiment_prod

# 2. Validate configuration
super agent dataset validate sentiment_prod

# 3. See dataset stats
super agent dataset info sentiment_prod

# 4. Compile
super agent compile sentiment_prod
# → "📊 Loaded 15,000 examples from datasets!"

# 5. Evaluate
super agent evaluate sentiment_prod
# → Uses all 15,002 examples

# 6. Optimize
super agent optimize sentiment_prod --auto medium --fresh
# → GEPA trains on 15,000 examples (better results!)

# 7. Re-evaluate
super agent evaluate sentiment_prod
# → See improvement from massive dataset!
```

---

## 💡 **Tips & Tricks**

### **Tip 1: Start with HuggingFace**

Don't have data? Use HuggingFace!

```yaml
datasets:
  - name: quick_start
    source: huggingface:imdb
    format: huggingface
    mapping: {input: text, output: label}
    limit: 1000  # Quick download
```

Browse datasets: https://huggingface.co/datasets

---

### **Tip 2: Use JSONL for Large Files**

```yaml
# Bad: Single JSON file (loads all in memory)
format: json

# Good: JSONL (streams line by line)
format: jsonl
```

---

### **Tip 3: Shuffle for Better Training**

```yaml
datasets:
  - shuffle: true  # ✅ Prevents ordering bias
    limit: 5000
```

---

### **Tip 4: Validate Before Training**

```bash
# Always validate first!
super agent dataset validate my_agent

# Then preview
super agent dataset preview my_agent

# Then use
super agent compile my_agent
```

---

## 📖 **API Reference**

### **Dataset Configuration Schema**

```yaml
datasets:
  - name: string              # Required
    source: string            # Required (file path or huggingface:name)
    format: enum              # csv|json|jsonl|parquet|huggingface
    mapping:                  # Required
      input: string|object
      output: string|object
      input_field_name: string   # Optional
      output_field_name: string  # Optional
    split: enum               # train|test|validation|all
    limit: integer            # Optional (max examples)
    shuffle: boolean          # Optional (default: true)
```

---

### **Mapping Formats**

**Simple Mapping** (single field):
```yaml
mapping:
  input: column_name
  output: column_name
  input_field_name: text    # Agent field name
  output_field_name: label  # Agent field name
```

**Complex Mapping** (multiple fields):
```yaml
mapping:
  input:
    question: question_col
    context: context_col
  output:
    answer: answer_col
    score: score_col
```

---

## 🎉 **Summary**

**Dataset Import enables**:
- ✅ Import from 5 formats (CSV, JSON, JSONL, Parquet, HuggingFace)
- ✅ Scale to 10,000+ examples
- ✅ Use existing datasets
- ✅ Standard ML workflows
- ✅ Better GEPA optimization
- ✅ Mix with BDD scenarios

**Get Started**:
```bash
# Add datasets to your playbook
# Run: super agent dataset preview my_agent
# Compile and use!
```

---

**Supported Formats**: CSV, JSON, JSONL, Parquet, HuggingFace

