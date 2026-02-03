# Example Datasets for SuperOptiX

Prebuilt datasets for testing and learning SuperOptiX's dataset import feature.

---

## 📊 **Available Datasets**

### **1. Sentiment Reviews** (sentiment_reviews.csv)
- **Format**: CSV
- **Size**: 30 examples
- **Use Case**: Sentiment analysis
- **Columns**: `text`, `label` (positive/negative/neutral)
- **Perfect For**: Learning sentiment classification

**Example Usage**:
```yaml
datasets:
  - name: reviews
    source: sentiment_reviews.csv
    format: csv
    mapping:
      input: text
      output: label
      input_field_name: text
      output_field_name: sentiment
```

---

### **2. Q&A Pairs** (qa_pairs.json)
- **Format**: JSON
- **Size**: 10 examples
- **Use Case**: Question answering about AI/ML
- **Fields**: `question`, `answer`, `category`
- **Perfect For**: Building Q&A agents

**Example Usage**:
```yaml
datasets:
  - name: qa_data
    source: qa_pairs.json
    format: json
    mapping:
      input: question
      output: answer
      input_field_name: question
      output_field_name: answer
```

---

### **3. Text Classification** (text_classification.jsonl)
- **Format**: JSONL
- **Size**: 20 examples
- **Use Case**: News category classification
- **Fields**: `text`, `category` (technology/business/sports/health/politics/science)
- **Perfect For**: Multi-class classification

**Example Usage**:
```yaml
datasets:
  - name: news_classifier
    source: text_classification.jsonl
    format: jsonl
    mapping:
      input: text
      output: category
      input_field_name: text
      output_field_name: category
```

---

### **4. Code Review Examples** (code_review_examples.csv) ⭐ **NEW!**
- **Format**: CSV
- **Size**: 50+ examples
- **Use Case**: Code review automation, security analysis, best practices
- **Columns**: `code`, `review`, `severity`, `category`, `language`
- **Categories**: security, performance, style, best_practices, code_smells
- **Perfect For**: Code review agents, static analysis training

**Example Usage**:
```yaml
datasets:
  - name: code_reviews
    source: code_review_examples.csv
    format: csv
    mapping:
      input: code
      output: review
      input_field_name: code
      output_field_name: review
```

**Special**: Designed for the Code Review Assistant demo agent!

---

## 🚀 **How to Use**

### **Option 1: Copy to Your Project**

```bash
# Copy example dataset
cp /path/to/superoptix/datasets/examples/sentiment_reviews.csv ./data/

# Use in playbook
spec:
  datasets:
    - source: ./data/sentiment_reviews.csv
      format: csv
      mapping: {input: text, output: label}
```

### **Option 2: Reference Directly** (if SuperOptiX installed)

```bash
# Find installed location
python -c "import superoptix; from pathlib import Path; print(Path(superoptix.__file__).parent / 'datasets/examples')"

# Use absolute path in playbook
datasets:
  - source: /path/to/superoptix/datasets/examples/sentiment_reviews.csv
```

---

## 💡 **Quick Test**

```bash
# Create test agent with example dataset
cat << 'EOF' > test_agent.yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Test Agent
  id: test_agent
spec:
  language_model:
    model: llama3.1:8b
  input_fields:
  - {name: text, type: string}
  output_fields:
  - {name: sentiment, type: string}
  datasets:
  - name: example_data
    source: /full/path/to/sentiment_reviews.csv
    format: csv
    mapping: {input: text, output: label}
    limit: 10
  tasks:
  - name: classify
    instruction: Classify sentiment
EOF

# Compile and test
super agent compile test_agent
super agent dataset preview test_agent
```

---

## 📋 **Dataset Specifications**

### **sentiment_reviews.csv**
```
Format: CSV
Rows: 30
Columns: text (string), label (positive|negative|neutral)
Balance: 10 positive, 10 negative, 10 neutral
Size: ~2 KB
Use: Sentiment analysis training
```

### **qa_pairs.json**
```
Format: JSON
Records: 10
Fields: question (string), answer (string), category (string)
Topics: AI, ML, Deep Learning
Size: ~2 KB
Use: Q&A system training
```

### **text_classification.jsonl**
```
Format: JSONL
Records: 20
Fields: text (string), category (string)
Categories: technology, business, sports, health, politics, science
Size: ~2 KB
Use: Multi-class classification
```

---

## 🎯 **Next Steps**

1. Copy datasets to your project's `data/` directory
2. Configure in your agent playbook
3. Preview with `super agent dataset preview`
4. Use with `super agent evaluate` and `optimize`

---

## 📚 **Learn More**

- [Dataset Import Guide](../../../docs/guides/dataset-import.md)
- [Example Playbooks](../../../examples/dataset_examples/)
- [DatasetLoader API](../loader.py)

---

*Example datasets for testing and learning*  
*Status: Production Ready*  
*Formats: CSV, JSON, JSONL*

