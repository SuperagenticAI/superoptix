# 🔄 CI/CD Integration Guide

SuperOptiX provides comprehensive CI/CD integration capabilities that enable automated testing, optimization, and deployment of AI agents. This guide covers how to integrate SuperOptiX into your CI/CD pipeline for professional-grade agent development.

## 🎯 Overview

CI/CD integration in SuperOptiX follows **BDD/TDD best practices** to ensure reliable, production-ready AI agents. The workflow emphasizes:

- **Baseline Measurement**: Establish performance baselines before optimization
- **Quality Gates**: Automated pass/fail thresholds for deployment
- **Iterative Improvement**: Measure optimization effectiveness quantitatively
- **Production Validation**: Final validation before deployment

## 🚀 CLI Command Options for CI/CD

The `super agent evaluate` command provides comprehensive testing capabilities with multiple output formats for different CI/CD use cases:

### Basic Usage
```bash
# Standard evaluation
super agent evaluate <agent_name>

# Verbose output with detailed results
super agent evaluate <agent_name> --verbose

# Auto-tuning for improved evaluation accuracy
super agent evaluate <agent_name> --auto-tune
```

### Output Formats for Automation
```bash
# Table format (default) - Beautiful console output
super agent evaluate <agent_name> --format table

# JSON format - For CI/CD integration and automation
super agent evaluate <agent_name> --format json

# JUnit format - Compatible with CI/CD systems
super agent evaluate <agent_name> --format junit
```

### Report Generation
```bash
# Save detailed report to file
super agent evaluate <agent_name> --save-report test_results.json

# Combine with JSON format for automation
super agent evaluate <agent_name> --format json --save-report results.json
```

### Development Options
```bash
# Ignore non-essential checks for rapid development
super agent evaluate <agent_name> --ignore-checks

# Verbose mode for detailed analysis
super agent evaluate <agent_name> --verbose
```

## 🔄 Proper BDD/TDD Workflow

The correct CI/CD workflow follows BDD/TDD best practices:

### **Phase 1: Specification-Driven Development**
```bash
# Define BDD scenarios FIRST
vim agents/<agent_name>/Playbook/developer_playbook.yaml
# Add comprehensive feature_specifications

# Compile agent with scenarios
super agent compile developer

# Run baseline evaluation (should show current performance)
super agent evaluate developer
# This gives us baseline metrics before optimization
```

### **Phase 2: Iterative Improvement**
```bash
# Analyze baseline results
# - Identify failing scenarios
# - Understand performance gaps
# - Plan optimization strategy

# Optimize based on evaluation feedback
super agent optimize developer

# Re-evaluate to measure improvement
super agent evaluate developer

# Iterate until quality gates pass
# Repeat steps 5-6 until pass rate ≥ 80%
```

### **Phase 3: Production Deployment**
```bash
# Final validation
super agent evaluate developer --verbose

# Deploy only if quality gates pass
super agent run developer --goal "production task"
```

## 🏗️ CI/CD Platform Integration

> **💡 Note**: The following CI/CD configurations are example setups designed to demonstrate integration patterns. Users should adapt these examples to their specific use cases, environment requirements, and organizational needs. Modify agent names, quality gate thresholds, and deployment strategies according to your project requirements.

### GitHub Actions Integration

```yaml
# .github/workflows/agent-quality.yml
name: Agent Quality Check
on: [push, pull_request]

jobs:
  bdd-workflow:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.11'
      
      - name: Setup SuperOptiX
        run: pip install superoptix
      
      - name: Compile Agent
        run: super agent compile developer
      
      - name: Baseline Evaluation
        run: |
          super agent evaluate developer --format json --save-report baseline.json
          # Check if baseline is acceptable
          pass_rate=$(jq -r '.summary.pass_rate' baseline.json | tr -d '%')
          if (( $(echo "$pass_rate < 40" | bc -l) )); then
            echo "Baseline too low: $pass_rate%"
            exit 1
          fi
      
      - name: Optimize Agent
        run: super agent optimize developer
      
      - name: Final Evaluation
        run: |
          super agent evaluate developer --format json --save-report results.json
          # Quality gate: must improve by at least 20%
          improvement=$(jq -r '.improvement.percentage' results.json | tr -d '%')
          if (( $(echo "$improvement < 20" | bc -l) )); then
            echo "Insufficient improvement: $improvement%"
            exit 1
          fi
      
      - name: Upload Test Results
        uses: actions/upload-artifact@v3
        with:
          name: bdd-spec-results
          path: results.json
```

### GitLab CI Integration

```yaml
# .gitlab-ci.yml
stages:
  - test
  - optimize
  - validate

agent-test:
  stage: test
  image: python:3.11
  script:
    - pip install superoptix
    - super agent compile developer
    - super agent evaluate developer --format json --save-report baseline.json
    - |
      # Extract pass rate for quality gate
      PASS_RATE=$(python -c "
      import json
      with open('baseline.json') as f:
          data = json.load(f)
      print(data['summary']['pass_rate'].replace('%', ''))
      ")
      echo "Pass rate: $PASS_RATE%"
      if [ "$PASS_RATE" -lt 40 ]; then
          echo "Baseline too low: $PASS_RATE%"
          exit 1
      fi
  artifacts:
    reports:
      junit: test-results.xml
    paths:
      - baseline.json

agent-optimize:
  stage: optimize
  image: python:3.11
  script:
    - pip install superoptix
    - super agent optimize developer
  dependencies:
    - agent-test

agent-validate:
  stage: validate
  image: python:3.11
  script:
    - pip install superoptix
    - super agent evaluate developer --format json --save-report final.json
    - |
      # Quality gate check
      IMPROVEMENT=$(python -c "
      import json
      with open('final.json') as f:
          data = json.load(f)
      print(data.get('improvement', {}).get('percentage', '0').replace('%', ''))
      ")
      echo "Improvement: $IMPROVEMENT%"
      if [ "$IMPROVEMENT" -lt 20 ]; then
          echo "Insufficient improvement: $IMPROVEMENT%"
          exit 1
      fi
  dependencies:
    - agent-optimize
```

### Jenkins Pipeline Integration

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install superoptix'
            }
        }
        
        stage('Compile') {
            steps {
                sh 'super agent compile developer'
            }
        }
        
        stage('Baseline Test') {
            steps {
                sh 'super agent evaluate developer --format json --save-report baseline.json'
                script {
                    def baseline = readJSON file: 'baseline.json'
                    def passRate = baseline.summary.pass_rate.replace('%', '').toInteger()
                    if (passRate < 40) {
                        error "Baseline too low: ${passRate}%"
                    }
                }
            }
        }
        
        stage('Optimize') {
            steps {
                sh 'super agent optimize developer'
            }
        }
        
        stage('Final Test') {
            steps {
                sh 'super agent evaluate developer --format json --save-report final.json'
                script {
                    def final = readJSON file: 'final.json'
                    def improvement = final.improvement?.percentage?.replace('%', '')?.toInteger() ?: 0
                    if (improvement < 20) {
                        error "Insufficient improvement: ${improvement}%"
                    }
                }
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: '*.json', fingerprint: true
            publishTestResults testResultsPattern: 'test-results.xml'
        }
    }
}
```



### CircleCI Integration

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  test-agent:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run:
          name: Install SuperOptiX
          command: pip install superoptix
      - run:
          name: Compile Agent
          command: super agent compile developer
      - run:
          name: Baseline Evaluation
          command: |
            super agent evaluate developer --format json --save-report baseline.json
            # Check baseline quality gate
            PASS_RATE=$(python -c "
            import json
            with open('baseline.json') as f:
                data = json.load(f)
            print(data['summary']['pass_rate'].replace('%', ''))
            ")
            if [ "$PASS_RATE" -lt 40 ]; then
                echo "Baseline too low: $PASS_RATE%"
                exit 1
            fi
      - run:
          name: Optimize Agent
          command: super agent optimize developer
      - run:
          name: Final Evaluation
          command: |
            super agent evaluate developer --format json --save-report final.json
            # Check improvement quality gate
            IMPROVEMENT=$(python -c "
            import json
            with open('final.json') as f:
                data = json.load(f)
            print(data.get('improvement', {}).get('percentage', '0').replace('%', ''))
            ")
            if [ "$IMPROVEMENT" -lt 20 ]; then
                echo "Insufficient improvement: $IMPROVEMENT%"
                exit 1
            fi
      - store_artifacts:
          path: *.json
          destination: test-results

workflows:
  version: 2
  test:
    jobs:
      - test-agent
```

## 🎯 Quality Gates Implementation

### Automated Quality Gates

For custom CI/CD scripts, you can implement quality gates:

```bash
#!/bin/bash
# quality-gate.sh

# Set minimum thresholds
MIN_PASS_RATE=80
MIN_IMPROVEMENT=20

# Run evaluation and extract metrics
super agent evaluate developer --format json --save-report results.json

# Extract pass rate
PASS_RATE=$(jq -r '.summary.pass_rate' results.json | tr -d '%')

# Extract improvement percentage
IMPROVEMENT=$(jq -r '.improvement.percentage' results.json | tr -d '%')

echo "Pass Rate: $PASS_RATE%"
echo "Improvement: $IMPROVEMENT%"

# Quality gate checks
if [ "$PASS_RATE" -lt "$MIN_PASS_RATE" ]; then
    echo "Quality gate failed: $PASS_RATE% < $MIN_PASS_RATE%"
    exit 1
fi

if [ "$IMPROVEMENT" -lt "$MIN_IMPROVEMENT" ]; then
    echo "Improvement gate failed: $IMPROVEMENT% < $MIN_IMPROVEMENT%"
    exit 1
fi

echo "All quality gates passed!"
```

### Quality Gate Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| **Baseline Pass Rate** | ≥ 40% | Continue to optimization |
| **Final Pass Rate** | ≥ 80% | Deploy to production |
| **Improvement** | ≥ 20% | Accept optimization |
| **Response Time** | < 30s | Performance check |

## 🔧 Advanced CI/CD Features

### Multi-Agent Testing

Test multiple agents in parallel:

```yaml
# .github/workflows/multi-agent-test.yml
name: Multi-Agent Testing
on: [push, pull_request]

jobs:
  test-agents:
    strategy:
      matrix:
        agent: [developer, customer-service, data-analyst]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.11'
      
      - name: Setup SuperOptiX
        run: pip install superoptix
      
      - name: Test Agent
        run: |
          super agent compile ${{ matrix.agent }}
          super agent evaluate ${{ matrix.agent }} --format json --save-report ${{ matrix.agent }}_results.json
      
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.agent }}-results
          path: ${{ matrix.agent }}_results.json
```

### Conditional Optimization

Only optimize when needed:

```yaml
# .github/workflows/conditional-optimization.yml
name: Conditional Optimization
on: [push, pull_request]

jobs:
  evaluate-and-optimize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup SuperOptiX
        run: pip install superoptix
      
      - name: Baseline Evaluation
        run: |
          super agent evaluate developer --format json --save-report baseline.json
          PASS_RATE=$(jq -r '.summary.pass_rate' baseline.json | tr -d '%')
          echo "PASS_RATE=$PASS_RATE" >> $GITHUB_ENV
      
      - name: Optimize if Needed
        if: env.PASS_RATE < 80
        run: |
          super agent optimize developer
          super agent evaluate developer --format json --save-report final.json
      
      - name: Skip Optimization
        if: env.PASS_RATE >= 80
        run: |
          echo "Pass rate already at $PASS_RATE%, skipping optimization"
          cp baseline.json final.json
```

### Automated Deployment

Deploy only after quality gates pass:

```yaml
# .github/workflows/deploy.yml
name: Deploy Agent
on:
  workflow_run:
    workflows: ["Agent Quality Check"]
    types: [completed]

jobs:
  deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup SuperOptiX
        run: pip install superoptix
      
      - name: Download Test Results
        uses: actions/download-artifact@v3
        with:
          name: bdd-spec-results
          path: ./
      
      - name: Verify Quality Gates
        run: |
          PASS_RATE=$(jq -r '.summary.pass_rate' results.json | tr -d '%')
          if [ "$PASS_RATE" -lt 80 ]; then
            echo "Quality gate failed: $PASS_RATE% < 80%"
            exit 1
          fi
      
      - name: Deploy to Production
        run: |
          # Your deployment commands here
          echo "Deploying agent to production..."
```

## 📊 Monitoring and Reporting

### Test Results Dashboard

Create a dashboard for test results:

```yaml
# .github/workflows/dashboard.yml
name: Test Results Dashboard
on:
  workflow_run:
    workflows: ["Agent Quality Check"]
    types: [completed]

jobs:
  update-dashboard:
    runs-on: ubuntu-latest
    steps:
      - name: Download Results
        uses: actions/download-artifact@v3
        with:
          name: bdd-spec-results
          path: ./
      
      - name: Generate Dashboard
        run: |
          # Generate HTML dashboard from JSON results
          python -c "
          import json
          with open('results.json') as f:
              data = json.load(f)
          # Generate HTML dashboard
          "
      
      - name: Deploy Dashboard
        run: |
          # Deploy dashboard to GitHub Pages or other hosting
          echo "Dashboard updated"
```

### Slack Notifications

Send notifications to Slack:

```yaml
# .github/workflows/notifications.yml
name: Notifications
on:
  workflow_run:
    workflows: ["Agent Quality Check"]
    types: [completed]

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Download Results
        uses: actions/download-artifact@v3
        with:
          name: bdd-spec-results
          path: ./
      
      - name: Send Slack Notification
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ github.event.workflow_run.conclusion }}
          text: |
            Agent Quality Check: ${{ github.event.workflow_run.conclusion }}
            Pass Rate: $(jq -r '.summary.pass_rate' results.json)
            Improvement: $(jq -r '.improvement.percentage' results.json)
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 🚀 Best Practices

### **DO's**
1. **Always evaluate before optimizing**
2. **Set clear quality gates**
3. **Measure improvement quantitatively**
4. **Iterate based on evaluation feedback**
5. **Use scenarios as both training data and test cases**
6. **Automate everything**
7. **Monitor trends over time**

### **DON'Ts**
1. **Don't optimize without baseline**
2. **Don't skip evaluation after optimization**
3. **Don't deploy without quality gates**
4. **Don't ignore failing scenarios**
5. **Don't deploy on failing tests**

## 🔍 Troubleshooting

### Common CI/CD Issues

#### **Quality Gate Failures**
```bash
# Check baseline quality
super agent evaluate developer --format json --save-report baseline.json
jq '.summary.pass_rate' baseline.json

# Check improvement
super agent evaluate developer --format json --save-report final.json
jq '.improvement.percentage' final.json
```

#### **Optimization Failures**
```bash
# Check if agent is compiled
super agent compile developer

# Check if scenarios exist
super agent evaluate developer --verbose

# Force re-optimization
super agent optimize developer --force
```

#### **Deployment Failures**
```bash
# Verify quality gates locally
./quality-gate.sh

# Check agent status
super agent inspect developer

# Test agent manually
super agent run developer --goal "test task"
```

## 📚 Related Resources

- [Evaluation & Testing Guide](evaluation-testing.md) - Detailed testing information
- [Optimization Guide](optimization.md) - Agent optimization techniques
- [BDD Guide](bdd.md) - Behavior-Driven Development practices
- [Agent Development Guide](agent-development.md) - Agent development workflow

**🎯 Key Takeaway**: CI/CD integration ensures reliable, production-ready AI agents through automated testing, quality gates, and iterative improvement. Always evaluate before optimizing and deploy only when quality gates pass. 