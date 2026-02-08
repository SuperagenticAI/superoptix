# LogFire Integration with Pydantic AI

**LogFire** is an observability platform built by the Pydantic team that provides comprehensive tracing, logging, and metrics for your Pydantic AI agents.

## 🎯 Overview

SuperOptiX includes **native LogFire integration** for Pydantic AI agents, allowing you to:

- **Trace agent executions** with full visibility into LLM calls
- **Monitor tool usage** (MCP tools, regular tools)
- **Track token usage and costs** automatically
- **View conversation history** with rich formatting
- **Analyze performance metrics** (latency, success rates)
- **Debug issues** with detailed span information

The integration is **opt-in** and works gracefully when LogFire is not configured.

---

## 📦 Installation

LogFire is available as a **separate optional dependency** to avoid conflicts with other frameworks:

### Basic Installation

```bash
# Install Pydantic AI support
pip install "superoptix[frameworks-pydantic-ai]"

# Install LogFire observability (separate, optional)
pip install "superoptix[logfire]"
```

Or install both together:
```bash
pip install "superoptix[frameworks-pydantic-ai,logfire]"
```

### Installation with `all` Extra

**Important:** LogFire is **NOT included** in `superoptix[all]` due to dependency conflicts:

```bash
# This installs everything EXCEPT LogFire
pip install "superoptix[all]"

# LogFire must be installed separately if needed
pip install "superoptix[logfire]"

# ⚠️ WARNING: Installing both [all,logfire] will FAIL
# because 'all' includes google-adk which conflicts with LogFire
```

**Why LogFire is separate:**
- LogFire requires `opentelemetry-sdk>=1.39.0,<1.40.0`
- `google-adk` (included in `[all]`) requires `opentelemetry-sdk==1.37.0` (exact version)
- These versions are incompatible

**Safe combinations:**
- `superoptix[frameworks-pydantic-ai,logfire]` - Works!
- `superoptix[frameworks-openai,logfire]` - Works!
- `superoptix[all]` - Works! (LogFire not included)
- `superoptix[all,logfire]` - Fails! (google-adk conflict)

**What gets installed:**
- `pydantic-ai==1.31.0` (from `frameworks-pydantic-ai`)
- `logfire==4.15.0` ✨ (from `logfire` extra)

---

## ⚙️ Configuration

### Playbook Configuration

**📍 Where to Configure LogFire in Your Playbook:**

The `logfire` configuration **MUST** be placed directly under the `spec:` section, at the same level as other top-level configurations like `language_model`, `persona`, `tasks`, etc.

**Playbook Structure:**
```
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: ...
spec:                    ← LogFire goes here
  logfire:               CORRECT LOCATION
    enabled: true
  language_model:        ← Same level
    ...
  persona:               ← Same level
    ...
```

**⚠️ Important:** Do NOT place it under `optimization`, `evaluation`, or other nested sections!

Enable LogFire in your agent playbook:

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Developer Assistant
  version: "1.0.0"
  
spec:
  # LogFire configuration - place it here in the spec section
  logfire:
    enabled: true  # Default: true (auto-detects if LogFire is available)
  
  # Other spec configurations (same level)
  language_model:
    provider: ollama
    model: llama3.1:8b
    api_base: http://localhost:11434
  
  persona:
    role: Software Developer
    goal: Write clean code
  
  # ... rest of your spec configuration
```

**Configuration Options:**

- `enabled: true` - Enable LogFire instrumentation (default)
- `enabled: false` - Disable LogFire even if installed

**Important Notes:**

- ⚠️ **Place `logfire` configuration directly under `spec:`** (not under `optimization` or other sections)
- If `logfire` section is omitted, it defaults to `enabled: true` (auto-detect)
- The configuration is read when the agent is initialized

### Code Configuration

LogFire must be configured **before** the agent is initialized:

#### Option 1: Cloud Dashboard (Recommended for Production)

```bash
# Authenticate with LogFire (one-time setup)
logfire auth

# LogFire auto-configures after auth
# No additional code needed!
```

#### Option 2: Local Backend (For Development)

Configure LogFire to send traces to a local OTLP-compatible observability backend:

```python
import os
import logfire

# Set OTLP endpoint for your local backend
os.environ['OTEL_EXPORTER_OTLP_TRACES_ENDPOINT'] = 'http://localhost:4318/v1/traces'

logfire.configure(
    service_name='my-superoptix-agent',
    send_to_logfire=False  # Don't send to cloud
)
```

**Note:** Make sure your local backend supports OTLP HTTP/Protobuf encoding.

---

## 🚀 Usage

### Basic Usage

1. **Configure LogFire** (if using cloud):
   ```bash
   logfire auth
   ```

2. **Run your agent**:
   ```bash
   super agent run developer --goal "Write a Python function to validate emails"
   ```

3. **Traces are captured automatically!** ✨

### Compile and Run Example

```bash
# Initialize project
super init my_project
cd my_project

# Pull agent
super agent pull developer

# Enable LogFire in playbook (edit playbook YAML)
#    Add to spec section:
#    spec:
#      logfire:
#        enabled: true

# Authenticate with LogFire (one-time setup)
logfire auth

# Compile with Pydantic AI
super agent compile developer --framework pydantic-ai

# Run agent (LogFire traces captured automatically)
super agent run developer --goal "Implement a REST API endpoint"

# View traces at https://logfire.pydantic.dev
```

**📋 Step-by-Step Playbook Configuration:**

1. Open your agent's playbook: `swe/agents/developer/playbook/developer_playbook.yaml`
2. Add `logfire` section under `spec:`:

```yaml
spec:
  logfire:              # ← Add this section
    enabled: true       # ← Enable LogFire
  language_model:       # ← Other configs at same level
    ...
```

---

## 📊 Viewing Traces

### Option 1: LogFire Cloud Dashboard (Recommended)

1. **Authenticate** (if not done already):
   ```bash
   logfire auth
   ```

2. **Run your agent**:
   ```bash
   super agent run developer --goal "your task"
   ```

3. **View traces**:
   - Open: https://logfire.pydantic.dev
   - Navigate to your project
   - Click on "Traces" or "Live" section
   - Search for your agent executions

**What you'll see:**
- 🔵 Agent execution spans
- 💬 LLM conversation history
- 🔧 Tool invocations (MCP tools, etc.)
- ⏱️ Performance metrics
- 💰 Token usage and costs
- Errors and exceptions

### Option 2: Other OTLP-Compatible Backends

LogFire uses OpenTelemetry, so you can export to any OTLP-compatible backend:

```python
import os
import logfire

# Set OTLP endpoint for your preferred backend
os.environ['OTEL_EXPORTER_OTLP_TRACES_ENDPOINT'] = 'http://your-backend:4318/v1/traces'

logfire.configure(
    service_name='my-agent',
    send_to_logfire=False
)
```

**Note:** Make sure your OTLP-compatible backend supports HTTP/Protobuf encoding (not gRPC).

---

## 📋 What Gets Traced

When LogFire is enabled, the following are automatically captured:

### Agent Execution
- Agent initialization
- Input processing
- Output generation
- Execution duration

### LLM Interactions
- Model calls (requests/responses)
- Full conversation history
- Token usage
- Cost calculations
- Latency metrics

### Tool Usage
- MCP tool invocations
- Tool parameters and results
- Tool execution time
- Success/failure status

### Structured Output
- Validation events
- Field extraction
- Output formatting

### Errors
- Exception traces
- Error messages
- Stack traces
- Context information

---

## 🎛️ Advanced Configuration

### Custom Service Name

```python
import logfire

logfire.configure(
    service_name='my-custom-service-name',
    service_version='1.0.0',
    environment='production'
)
```

### Filtering and Sampling

```python
import logfire

logfire.configure(
    sampling={
        'default': 0.5  # Sample 50% of traces
    },
    min_level='info'  # Only log info level and above
)
```

### Scrubbing Sensitive Data

```python
import logfire

logfire.configure(
    scrubbing={
        'patterns': [
            r'password=\w+',
            r'api_key=\w+'
        ]
    }
)
```

---

## 🔍 Troubleshooting

### Traces Not Appearing

**Issue:** Traces don't show up in LogFire dashboard.

**Solutions:**
1. Verify LogFire is authenticated: `logfire auth`
2. Check if LogFire is configured: LogFire should be configured before agent initialization
3. Verify `logfire.enabled: true` in playbook (or omit it, defaults to true)
4. Check network connectivity (for cloud dashboard)

### ImportError: No module named 'logfire'

**Issue:** LogFire is not installed.

**Solution:**
```bash
pip install "superoptix[frameworks-pydantic-ai]"
# OR
pip install logfire==4.15.0
```

### Instrumentation Not Working

**Issue:** Agent runs but LogFire doesn't capture traces.

**Solutions:**
1. Ensure LogFire is configured **before** agent initialization
2. Check that `logfire.enabled: true` in playbook
3. Verify agent was compiled after LogFire was configured
4. Re-compile agent: `super agent compile developer --framework pydantic-ai`

### Graceful Fallback

If LogFire is not installed or not configured, the integration **silently skips** instrumentation. Your agent will work normally without errors.

This is intentional behavior - LogFire is optional and won't break your workflow.

---

## 📚 Example Playbook

Complete example with LogFire enabled, showing **exact placement** in the playbook:

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Developer Assistant
  version: "1.0.0"
  
spec:
  # LogFire Configuration - MUST be under spec: (same level as other configs)
  logfire:
    enabled: true  # Auto-detects if LogFire is available and configured
  
  # Model Configuration
  language_model:
    provider: ollama
    model: llama3.1:8b
    api_base: http://localhost:11434
  
  # Input/Output Fields
  input_fields:
    - name: feature_requirement
      type: string
      description: Description of feature to implement
  
  output_fields:
    - name: implementation
      type: string
      description: Code implementation
  
  # Persona Configuration
  persona:
    role: Software Developer
    goal: Write clean, efficient code
  
  # Tasks, evaluation, optimization, etc.
  tasks:
    - name: implement_feature
      instruction: Implement the requested feature
  
  # ... rest of your configuration
```

**⚠️ Common Mistakes to Avoid:**

**Wrong - LogFire under wrong section:**
```yaml
spec:
  optimization:
    logfire:  # WRONG - don't put it here
      enabled: true
```

**Wrong - LogFire outside spec:**
```yaml
metadata:
  logfire:  # WRONG - must be under spec:
    enabled: true
spec:
  language_model:
    ...
```

**Correct - LogFire directly under spec:**
```yaml
spec:
  logfire:  # CORRECT - directly under spec:
    enabled: true
  language_model:
    ...
```

---

## 🔗 Resources

- **LogFire Documentation**: https://logfire.pydantic.dev/docs/
- **LogFire Dashboard**: https://logfire.pydantic.dev
- **Pydantic AI Documentation**: https://ai.pydantic.dev/
- **OpenTelemetry**: https://opentelemetry.io/

---

## 💡 Best Practices

1. **Use Cloud Dashboard for Production**: Authenticate with `logfire auth` for production deployments
2. **Configure Before Initialization**: Always configure LogFire before creating agents
4. **Monitor Costs**: LogFire tracks token usage and costs - useful for budgeting
5. **Use Service Names**: Set meaningful `service_name` for better trace organization

---

## 🎉 Summary

LogFire integration in SuperOptiX provides:

- **Zero-configuration** - Works out of the box when LogFire is installed
- **Graceful fallback** - No errors if LogFire is not available
- **Rich observability** - Full visibility into agent execution
- **Production-ready** - Works with LogFire cloud or any OTLP backend
- **Framework-native** - Built specifically for Pydantic AI

Enable LogFire in your playbook and start getting insights into your agent behavior! 🚀
