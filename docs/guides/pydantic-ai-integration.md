# 🐍 Pydantic AI Integration

**SuperOptiX supports Pydantic AI with framework-native minimal pipelines and optional optimization workflows.**

**Works with local and cloud models**

**Native MCP (Model Context Protocol) Support** - Built-in tool integration

**Plain Text Output Mode** - Natural responses without JSON formatting issues

**Model Settings** - Full control over generation parameters

**RLM (Experimental)** - Available for testing; unified sandbox support is coming soon.

---

## 🎯 What is Pydantic AI?

Pydantic AI is a modern, type-safe framework for building AI agents with:

- 🎯 **Type Safety**: Structured outputs using Pydantic models
- 🔧 **Tool Integration**: Native MCP (Model Context Protocol) support for tools
- 🌐 **Provider Agnostic**: Works with OpenAI, Ollama, Anthropic, and 100+ LLMs
- ⚡ **Async/Await**: Built-in async support for high-performance applications
- 📊 **Model Settings**: Fine-grained control (max_tokens, top_p, etc.)
- 🔌 **MCP Native**: Direct integration with MCP servers for tool discovery

Perfect for deployment applications requiring type safety and reliable tool integration!

---

## 📦 Installation

```bash
pip install superoptix[frameworks-pydantic-ai]
```

**Includes:**
- pydantic-ai 1.31.0 (exact version pinned)
- SuperOptiX core with GEPA 0.0.17

**Requirements:**
- Python 3.11+
- Git (for DSPy dependency)

---

## 🚀 Quick Start

### Initialize Project

```bash
super init my_project
cd my_project
```

### Pull Demo Agent

```bash
super agent pull developer
```

This pulls the `developer` agent playbook into your project.

### Configure Model

### Runtime Modes (Important)

Pydantic AI in SuperOptiX can run in:
- `direct` mode: provider API directly (recommended for most users)
- `gateway` mode: requires gateway configuration and `PYDANTIC_AI_GATEWAY_API_KEY`

If your playbook/runtime is gateway-mode and the key is missing, run will fail early by design.

### Example Config (Local Ollama)

```yaml
spec:
  language_model:
    provider: ollama
    model: llama3.1:8b  # Pydantic AI auto-adds 'ollama:' prefix if needed
    api_base: http://localhost:11434
```

Run:
```bash
brew install ollama  # macOS
ollama pull llama3.1:8b
super agent compile developer --framework pydantic-ai
super agent run developer --framework pydantic-ai --direct --goal "Implement a user registration API endpoint with email validation"
```

### Example Config (Cloud Google, requires key)
```yaml
# Google Gemini
spec:
  language_model:
    provider: google-genai
    model: gemini-2.5-flash
    # Set: export GOOGLE_API_KEY="..."
```

### Run the Workflow

```bash
super agent compile developer --framework pydantic-ai --cloud --provider google-genai --model gemini-2.5-flash

# Run (direct mode)
super agent run developer --framework pydantic-ai --direct --cloud --provider google-genai --model gemini-2.5-flash --goal "Your task here"

# Optional optimize loop
super agent compile developer --framework pydantic-ai --optimize
super agent optimize developer --framework pydantic-ai --auto light
```

---

## 📋 Creating Your Own Pydantic AI Playbook

### Basic Structure

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: My Assistant
  id: my_assistant
  namespace: custom
  version: 1.0.0
  level: genies

spec:
  language_model:
    provider: ollama
    model: llama3.1:8b
    api_base: http://localhost:11434
  
  input_fields:
    - name: query
      type: str
      description: User query or question
  
  output_fields:
    - name: response
      type: str
      description: Generated response
  
  persona:
    role: Helpful AI Assistant
    goal: Provide clear and helpful responses
    backstory: I am an AI assistant trained to help users with their questions.
  
  # BDD Scenarios
  feature_specifications:
    scenarios:
      - name: Test scenario
        input:
          query: "Hello!"
        expected_output:
          response: "Greeting"
          expected_keywords:
            - hello
  
  optimization:
    optimizer:
      name: GEPA
      params:
        reflection_lm: llama3.1:8b
        auto: medium
```

### Output Configuration

Define what your agent should return:

```yaml
spec:
  output_fields:
    - name: implementation
      type: str
      description: Code implementation
    - name: explanation
      type: str
      description: Brief explanation of the code
```

**Plain Text Mode (Default):**
The agent returns natural text responses, which works reliably with smaller models like `llama3.1:8b`. The output is mapped to your defined fields.

**Example Output:**
```
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Aspect         ┃ Value                                   ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Implementation │ def add_numbers(a, b):                  │
│                │     """Add two numbers together."""     │
│                │     return a + b                        │
└────────────────┴─────────────────────────────────────────┘
```

This approach avoids JSON formatting issues that can occur with smaller models.

### Model Settings

Configure generation parameters (excluding `temperature` as it's deprecated by OpenAI):

```yaml
spec:
  language_model:
    provider: ollama
    model: llama3.1:8b
    max_tokens: 4000  # Default: 4000 (supports detailed responses)
    top_p: 0.9        # Optional: Nucleus sampling (0.0-1.0)
    frequency_penalty: 0.0  # Optional: Reduce repetition (-2.0 to 2.0)
    presence_penalty: 0.0   # Optional: Encourage new topics (-2.0 to 2.0)
```

**Configuration Options:**

- **`max_tokens`** (default: `4000`): Maximum number of tokens in the response. 
  - Increase for longer responses (test plans, detailed code, comprehensive explanations)
  - Decrease for shorter responses (faster, cheaper)
  - Recommended values:
    - Quick responses: `1000-2000`
    - Standard responses: `2000-4000` (default)
    - Detailed/comprehensive: `4000-8000`
    - Very detailed: `8000-16000` (may require larger models)

- **`top_p`** (optional): Nucleus sampling threshold (0.0-1.0). Controls diversity of output.
  - `0.9-1.0`: More creative, diverse responses
  - `0.5-0.9`: Balanced
  - `0.0-0.5`: More focused, deterministic

- **`frequency_penalty`** (optional): Reduces repetition (-2.0 to 2.0)
  - Positive values: Reduce repetition
  - Negative values: Allow more repetition

- **`presence_penalty`** (optional): Encourages new topics (-2.0 to 2.0)
  - Positive values: Encourage new topics
  - Negative values: Stay on topic

These settings are passed to Pydantic AI's `ModelSettings` class and control the model's generation behavior.

---

## 🔌 MCP (Model Context Protocol) Integration

Pydantic AI has **native MCP support**! You can connect to MCP servers directly in your playbook.

### Basic MCP Configuration

```yaml
spec:
  mcp:
    enabled: true
    servers:
      - name: filesystem
        type: stdio
        config:
          command: "npx"
          args: ["-y", "@modelcontextprotocol/server-filesystem", "/private/tmp"]  # Use /private/tmp on macOS (or /tmp on Linux)
        tool_prefix: "fs_"  # Optional: prefix to avoid naming conflicts
```

### Supported MCP Server Types

#### Local stdio Server

Runs MCP server as a subprocess:

```yaml
spec:
  mcp:
    enabled: true
    servers:
      - name: filesystem
        type: stdio
        config:
          command: "npx"
          args: ["-y", "@modelcontextprotocol/server-filesystem", "/private/tmp"]  # Use /private/tmp on macOS (or /tmp on Linux)
          env:  # Optional environment variables
            API_KEY: "${MY_API_KEY}"
          timeout: 30  # Optional timeout in seconds
```

#### Remote Streamable HTTP Server

Connects to a remote MCP server over HTTP:

```yaml
spec:
  mcp:
    enabled: true
    servers:
      - name: weather_api
        type: streamable_http
        config:
          url: "https://mcp-server.com/mcp"
        tool_prefix: "weather_"
```

#### Remote SSE Server (Deprecated)

Connects to a remote MCP server using Server-Sent Events:

```yaml
spec:
  mcp:
    enabled: true
    servers:
      - name: legacy_server
        type: sse
        config:
          url: "http://localhost:3001/sse"
```

### Multiple MCP Servers

You can connect multiple MCP servers:

```yaml
spec:
  mcp:
    enabled: true
    servers:
      - name: filesystem
        type: stdio
        config:
          command: "npx"
          args: ["-y", "@modelcontextprotocol/server-filesystem", "/private/tmp"]  # Use /private/tmp on macOS (or /tmp on Linux)
        tool_prefix: "fs_"
      
      - name: weather_api
        type: streamable_http
        config:
          url: "https://mcp-server.com/mcp"
        tool_prefix: "weather_"
```

Each server's tools will be available with their respective prefixes.

### MCP Tool Optimization

> ⚠️ **Resource Warning:** MCP tool optimization runs **two sequential phases**, effectively doubling the resource usage. Only run this if you have adequate GPU/compute resources and understand the cost implications.

SuperOptiX can optimize **both MCP tool descriptions AND agent instructions** in a two-phase optimization process. This ensures your agent uses tools effectively AND understands its role clearly.

#### Enable MCP Tool Optimization

Add the `optimization` section under `mcp` in your playbook:

```yaml
spec:
  mcp:
    enabled: true
    servers:
      - name: filesystem
        type: stdio
        config:
          command: "npx"
          args: ["-y", "@modelcontextprotocol/server-filesystem", "/private/tmp"]  # Use /private/tmp on macOS (or /tmp on Linux)
        tool_prefix: "fs_"  # Tools will be prefixed with fs_ at runtime
    
    # Enable MCP tool description optimization
    optimization:
      optimize_tool_descriptions: true
      # IMPORTANT: Use actual MCP server tool names (WITHOUT prefix)
      # The optimizer queries the server directly to find tools
      tool_names: ["read_file", "write_file", "list_directory"]
```

**Important Notes:**
- **Use actual MCP server tool names WITHOUT prefix** - The optimizer queries the MCP server directly, which returns the original tool names (e.g., `read_file`, not `fs_read_file`)
- The `tool_prefix` only affects how tools appear at runtime in the agent, not how the optimizer finds them
- You can optimize multiple tools from the same server
- Tool optimization uses the same training data (BDD scenarios) as instruction optimization

**Common MCP Filesystem Server Tools:**
| Server Tool Name | Description |
|-----------------|-------------|
| `read_file` | Read file contents |
| `write_file` | Write/create files |
| `list_directory` | List directory contents |
| `create_directory` | Create directories |
| `move_file` | Move/rename files |
| `search_files` | Search for files |

#### Two-Phase Optimization Process

When you run `super agent optimize`, SuperOptiX performs **two sequential optimizations**:

##### Phase 1: MCP Tool Description Optimization

**What Gets Optimized:**
- Tool descriptions for each tool in `tool_names`
- GEPA learns better descriptions that help the model understand:
  - **When** to use each tool
  - **What** each tool does
  - **How** to use each tool effectively

**Example Transformation:**

**Before Optimization:**
```json
{
  "tool_description_fs_read_file": "Tool: fs_read_file",
  "tool_description_fs_write_file": "Tool: fs_write_file",
  "tool_description_fs_list_files": "Tool: fs_list_files"
}
```

**After GEPA Optimization:**
```json
{
  "tool_description_fs_read_file": "Read file contents from the filesystem. Use when user asks to view, show, display, or read file contents. Returns the full text content of the specified file path. Requires a valid file path parameter.",
  "tool_description_fs_write_file": "Write content to files on the filesystem. Use when user asks to create, save, update, or write file contents. Requires file path and content parameters. Overwrites existing files.",
  "tool_description_fs_list_files": "List files and directories in a given path. Use when user asks to see what files are available, browse directories, find files, or explore the filesystem. Returns a list of files and folders in the specified directory."
}
```

**Output File:**
```
{project_name}/agents/{agent_name}/optimized/{agent_name}_mcp_tool_descriptions.json
```

##### Phase 2: Agent Instruction Optimization

**What Gets Optimized:**
- Agent's system prompt/instructions (built from `persona.role`, `persona.goal`, `persona.backstory`, etc.)
- GEPA learns better instructions that help the model:
  - Understand its role more clearly
  - Use tools more effectively
  - Generate better responses

**Output File:**
```
{project_name}/agents/{agent_name}/optimized/{agent_name}_pydantic_ai_optimized.json
```

#### Running Optimization

> ⚠️ **Before Running:**
> - Ensure you have **high-end GPU** or cloud GPU access
> - Understand that optimization makes **many LLM API calls**
> - Use **local Ollama models** (e.g., `ollama/llama3.1:8b`) to minimize costs
> - Cloud models (GPT-4, Claude) will incur **significant API charges**

```bash
# Quick test (super light - ~1-2 minutes, ~20 API calls)
# RECOMMENDED: Use local Ollama to avoid API costs
super agent optimize developer \
  --framework pydantic-ai \
  --max-metric-calls 20 \
  --reflection-lm ollama/llama3.1:8b

# Light mode for better results (~5-10 minutes, ~50-100 API calls)
# Use local Ollama: --reflection-lm ollama/llama3.1:8b
# Cloud models (costly): --reflection-lm openai/gpt-4o
super agent optimize developer \
  --framework pydantic-ai \
  --auto light \
  --reflection-lm ollama/llama3.1:8b
```

**What You'll See:**

```
🔧 Phase 1: Optimizing MCP Tool Descriptions
   Optimizing 3 tool(s): fs_read_file, fs_write_file, fs_list_files
   MCP tool optimization complete!
   Best score: 0.850
   Saved to: .../developer_mcp_tool_descriptions.json

⚡ Phase 2: Running GEPA optimization for instructions...
   Budget: light
   Training examples: 5
   Validation examples: 0
   Optimization complete!
   Best score: 0.920
   Saved to: .../developer_pydantic_ai_optimized.json
```

#### Using Optimized Results

The generated pipeline **automatically loads** optimized values:

1. **Tool Descriptions**: Applied when MCP servers are initialized
2. **Instructions**: Loaded when the agent is created

You don't need to manually apply the optimizations - the pipeline handles it automatically!

#### Complete Example

```yaml
spec:
  language_model:
    provider: ollama
    model: llama3.1:8b  # Works great with plain text output mode
  
  mcp:
    enabled: true
    servers:
      - name: filesystem
        type: stdio
        config:
          command: "npx"
          args: ["-y", "@modelcontextprotocol/server-filesystem", "/private/tmp"]  # Use /private/tmp on macOS (or /tmp on Linux)
        tool_prefix: "fs_"  # Runtime prefix (tools become fs__read_file, etc.)
    
    # Enable tool optimization
    optimization:
      optimize_tool_descriptions: true
      # Use actual MCP server tool names (WITHOUT prefix)
      tool_names: ["read_file", "write_file", "list_directory"]
  
  # Agent instruction optimization (always runs)
  optimization:
    optimizer:
      name: GEPA
      params:
        auto: light
        reflection_lm: ollama/llama3.1:8b  # Use forward slash for LiteLLM
```

#### Best Practices

> ⚠️ **When to Skip Optimization:**
> - Your agent already performs well (pass rate > 80%)
> - You don't have high-end GPU or cloud GPU access
> - You want to avoid API costs
> - You're in early development/testing phase
> 
> **Optimization is optional** - many agents work great without it!

1. **Use Tool Prefixes**: Prevents naming conflicts when using multiple MCP servers
   ```yaml
   tool_prefix: "fs_"  # Tools become fs_read_file, fs_write_file, etc.
   ```

2. **Optimize Key Tools**: Focus on tools that are used frequently or are critical to your agent's functionality

3. **Reflection Model**: Use a smaller, faster model for reflection (GEPA runs it many times):
   ```bash
   --reflection-lm ollama/llama3.1:8b  # Fast, good enough for reflection, FREE!
   ```
   ⚠️ **Avoid cloud models** (GPT-4, Claude) unless you understand the costs - they can cost $5-100+ per optimization run!

4. **Task Model**: Use a larger model for the actual agent (better quality):
   ```yaml
   model: llama3.1:8b  # Works well with plain text mode (local, free)
   # or gpt-oss:120b for better quality (requires GPU)
   ```

5. **Training Data**: Ensure your BDD scenarios include examples that use MCP tools:
   ```yaml
   feature_specifications:
     scenarios:
       - name: read_config_file
         input:
           feature_requirement: "Read /private/tmp/config.json and tell me what database host is configured"  # Use /private/tmp on macOS
         expected_output:
           implementation: "localhost"  # Should use fs_read_file tool
   ```

#### Benefits of Two-Phase Optimization

**Better Tool Usage**: Optimized descriptions help the model choose the right tool at the right time  
**Better Instructions**: Optimized prompts improve overall agent behavior  
**Compound Effect**: Both optimizations work together for maximum performance  
**Automatic**: Pipeline automatically applies both optimizations when available

#### Troubleshooting

**Issue**: Tool optimization fails with "None of the specified tools found"

**Solution**: Use actual MCP server tool names **without** prefix:
```yaml
# Wrong - uses prefixed names
tool_names: ["fs_read_file", "fs_write_file"]

# Correct - uses actual server tool names
tool_names: ["read_file", "write_file", "list_directory"]
```

The optimizer queries the MCP server directly, which returns unprefixed tool names. The `tool_prefix` only affects runtime tool naming in the agent.

**Issue**: Tool optimization fails but instruction optimization succeeds

**Solution**: Check that:
- Tool names match actual MCP server tool names (without prefix)
- MCP server is accessible and tools are available
- Training scenarios include tool usage examples

**Issue**: Optimization takes too long

**Quick Solutions**:
- **Super Light**: Use `--max-metric-calls 20` for fastest test (~1-2 minutes)
- **Light Mode**: Use `--auto light` for balanced speed/quality (~5-10 minutes)
- Use smaller reflection model: `--reflection-lm ollama/llama3.1:8b`
- Reduce number of tools to optimize

---

## 🎬 MCP Demo Tutorial

For a complete step-by-step demo of MCP with Pydantic AI, including:
- Quick start with `pydantic-mcp` demo agent
- Setting up filesystem MCP server
- Testing file operations (read, write, list)
- Verified working examples with `llama3.1:8b`
- Troubleshooting common issues

See: [**Pydantic AI MCP Demo Guide**](pydantic-ai-mcp-demo.md)

**Quick Start:**
```bash
super init swe && cd swe
super agent pull pydantic-mcp
super agent compile pydantic-mcp --framework pydantic-ai
super agent run pydantic-mcp --goal "List all files in /private/tmp"  # Use /private/tmp on macOS
```

---

## 🎯 GEPA Optimization

> ⚠️ **IMPORTANT: Resource Requirements**
> 
> **GEPA optimization is resource-intensive and should only be run when:**
> - You have a **high-end GPU** (or cloud GPU access)
> - You understand the **cost implications** (many LLM API calls)
> - You have adequate **time budget** (5-60 minutes depending on settings)
> 
> **Resource Usage:**
> - Makes **many LLM API calls** (reflection + evaluation)
> - Can consume significant **GPU memory** and **compute resources**
> - Cloud API costs can add up quickly (especially with GPT-4, Claude, etc.)
> 
> **For local testing:** Use `--max-metric-calls 20` with `ollama/llama3.1:8b` to minimize resource usage.

### What Gets Optimized

Pydantic AI has one main optimizable variable:
- **`instructions`**: The agent's system prompt (built from `persona.role`, `persona.goal`, `persona.backstory`, etc.)

### How GEPA Optimizes Pydantic AI Agents

GEPA optimizes the **instructions** field by:

1. **Analyzing BDD test scenarios** to understand success criteria
2. **Generating variations** of the instructions prompt
3. **Testing each variation** against your evaluation scenarios
4. **Selecting the best performer** based on pass rate

**Example transformation:**

```yaml
# Original (from playbook)
persona:
  role: Software Developer
  goal: Write clean, efficient code
  backstory: I am an experienced developer

→ instructions = "Software Developer\nGoal: Write clean, efficient code\nBackstory: I am an experienced developer"
```

```yaml
# After GEPA optimization
→ instructions = "You are a Software Developer.

When writing code:
1. Ensure it is clean and maintainable
2. Follow best practices and conventions
3. Include proper error handling
4. Write comprehensive tests

Goal: Write clean, efficient code that meets requirements and is deployment-ready.

Backstory: I am an experienced developer with expertise in multiple programming languages and frameworks."
```

GEPA typically expands the instructions to be more explicit and structured, which improves agent behavior consistency.

### Optimization Command

> ⚠️ **Resource & Cost Warning:**
> 
> GEPA optimization is **resource-intensive** and makes **many LLM API calls**:
> - **Super Light**: ~20 API calls (~$0.10-2.00 with cloud models)
> - **Light**: ~50-100 API calls (~$0.50-10.00 with cloud models)  
> - **Medium**: ~150-300 API calls (~$5-50 with cloud models)
> - **Heavy**: ~300-600 API calls (~$20-100+ with cloud models)
> 
> **Recommendations:**
> - Use **local Ollama models** (`ollama/llama3.1:8b`) to avoid API costs
> - Only optimize when you have **high-end GPU** or cloud GPU access
> - Start with `--max-metric-calls 20` to test
> - Avoid cloud models (GPT-4, Claude) unless you understand the costs

#### Quick Test (Super Light) ⚡

> ⚠️ **Resource Warning:** Even "super light" optimization makes LLM API calls and can take time.

> 💡 **Tip:** If your playbook has `auto: light` or `max_full_evals` set, the CLI `--max-metric-calls` argument will override it. CLI arguments always take precedence.

For fastest optimization to test if it works:

```bash
# Very fast: only 3 metric calls (~30 seconds - 1 minute)
super agent optimize my_agent \
  --framework pydantic-ai \
  --max-metric-calls 3 \
  --reflection-lm ollama/llama3.1:8b

# Quick test: 10 metric calls (~1-2 minutes)
super agent optimize my_agent \
  --framework pydantic-ai \
  --max-metric-calls 10 \
  --reflection-lm ollama/llama3.1:8b

# Light optimization: 20 metric calls (~2-3 minutes)
super agent optimize my_agent \
  --framework pydantic-ai \
  --max-metric-calls 20 \
  --reflection-lm ollama/llama3.1:8b
```

**Use this when:**
- Testing if optimization works
- Limited resources/time
- Quick iteration during development
- Just need to verify the process
- **Using local Ollama models** (recommended to avoid API costs)

> **Note:** `--max-metric-calls 20` limits total evaluations more precisely than `--max-full-evals 1`, ensuring faster completion.
> 
> **Cost Tip:** Use local `ollama/llama3.1:8b` for reflection_lm to avoid API costs. Cloud models (GPT-4, Claude) will incur charges.

#### Recommended (Balanced)

```bash
super agent optimize my_agent \
  --framework pydantic-ai \
  --auto light \
  --reflection-lm ollama/llama3.1:8b
```

**Budget Options:**
- `--auto light`: Fast optimization (~2-5 iterations, ~5-10 minutes) ⭐ **Recommended**
- `--auto medium`: Balanced optimization (~5-10 iterations, ~15-30 minutes)
- `--auto heavy`: Thorough optimization (~10-20 iterations, ~30-60 minutes)
- `--max-full-evals N`: Specify exact number of iterations (use `1` for super quick test)
- `--max-metric-calls N`: Limit total metric evaluations

### Optimization Results

Optimized instructions are saved to:
```
{project_name}/agents/{agent_name}/optimized/{agent_name}_pydantic_ai_optimized.json
```

The generated pipeline automatically loads optimized instructions if available.

---

## 🔍 Field Description Optimization

> ⚠️ **IMPORTANT: Resource Requirements**
> 
> Field description optimization is resource-intensive and should only be run when:
> - You have a **high-end GPU** (or cloud GPU access)
> - You understand the **cost implications** (additional LLM API calls)
> - You plan to use **structured output mode** (required for optimized descriptions to take effect)

### What Gets Optimized

**Field Description Optimization** uses GEPA to optimize Pydantic model field descriptions (`Field(description=...)`) for structured output. This improves the model's understanding of what each output field should contain.

**Requires:**
- `output_fields` defined in your playbook
- `optimize_field_descriptions: true` in optimization config
- Structured output mode enabled (`output_mode: structured`) to use optimized descriptions

### How It Works

GEPA optimizes field descriptions by:

1. **Extracting field descriptions** from `output_fields` in your playbook
2. **Creating evaluation scenarios** based on your BDD test cases
3. **Generating variations** of each field description
4. **Testing each variation** to see which descriptions lead to better structured outputs
5. **Selecting the best descriptions** that improve structured data extraction accuracy

### Example Transformation

**Before Optimization:**
```yaml
spec:
  output_fields:
    - name: implementation
      type: string
      description: The code implementation of the feature
```

**After GEPA Optimization:**
```json
{
  "original_descriptions": {
    "implementation": "The code implementation of the feature"
  },
  "optimized_descriptions": {
    "implementation": "Complete, deployment-ready code implementation with proper imports, error handling, and documentation. Include full function/class definitions, not pseudocode or descriptions."
  },
  "score": 0.95,
  "iterations": 3
}
```

The optimized description is more explicit about what the model should produce, leading to better structured output quality.

### Enable Field Description Optimization

Add to your playbook's `optimization` section:

```yaml
spec:
  output_fields:
    - name: implementation
      type: string
      description: The code implementation of the feature
      required: true
  
  optimization:
    optimize_field_descriptions: true  # Enable field description optimization
    optimizer:
      name: GEPA
      params:
        auto: light
        reflection_lm: ollama/llama3.1:8b
```

**Important Notes:**
- Field description optimization runs as **Phase 1.5** (between MCP tool optimization and instruction optimization)
- It only runs if `output_fields` are defined in your playbook
- Optimized descriptions are saved but **only used when structured output mode is enabled**

### Running Field Description Optimization

```bash
# Quick test (super light - ~1-2 minutes)
super agent optimize developer \
  --framework pydantic-ai \
  --max-metric-calls 20 \
  --reflection-lm ollama/llama3.1:8b

# Light mode (~5-10 minutes)
super agent optimize developer \
  --framework pydantic-ai \
  --auto light \
  --reflection-lm ollama/llama3.1:8b
```

**What You'll See:**

```
🔧 Phase 1: Optimizing MCP Tool Descriptions (if enabled)
   ...

📋 Phase 1.5: Optimizing Field Descriptions
   Optimizing 1 field descriptions:
     - implementation: The code implementation of the feature
   
   Field description optimization complete!
   Best score: 0.95
   Saved to: .../developer_field_descriptions_optimized.json

⚡ Phase 2: Running GEPA optimization for instructions...
   ...
```

### Output File

Optimized field descriptions are saved to:
```
{project_name}/agents/{agent_name}/optimized/{agent_name}_field_descriptions_optimized.json
```

**File Format:**
```json
{
  "original_descriptions": {
    "implementation": "The code implementation of the feature"
  },
  "optimized_descriptions": {
    "implementation": "Complete, deployment-ready code implementation..."
  },
  "score": 0.95,
  "iterations": 3
}
```

### Using Optimized Field Descriptions

Optimized descriptions are **automatically used** when:
1. Structured output mode is enabled (`output_mode: structured`)
2. The optimization file exists in the `optimized/` directory
3. You've run `super agent optimize` with `optimize_field_descriptions: true`

The generated pipeline automatically loads and applies optimized descriptions when creating the BaseModel for structured output.

### Benefits

**Better Structured Output**: More explicit field descriptions improve the model's understanding  
**Improved Accuracy**: Optimized descriptions lead to better structured data extraction  
**Type Safety**: Works seamlessly with Pydantic's BaseModel validation  
**Automatic**: Pipeline automatically applies optimized descriptions when available

### When to Use

**Use field description optimization when:**
- You're using structured output mode
- Your structured outputs aren't accurate enough
- You have well-defined BDD test scenarios
- You have adequate GPU/compute resources

**Skip field description optimization when:**
- You're using plain text output mode (descriptions won't be used)
- Your structured outputs already work well
- You don't have resources for additional optimization
- `output_fields` aren't defined in your playbook

---

## 📊 Structured Output Mode

Pydantic AI supports **structured output** using Pydantic BaseModel for type-safe, validated responses. SuperOptiX provides an opt-in structured output mode that uses optimized field descriptions when available.

### What is Structured Output?

**Structured Output** uses Pydantic BaseModel to enforce type-safe responses:
- **Type Validation**: Responses are validated against the BaseModel schema
- **Field Descriptions**: Each field has a description that guides the model
- **Type Safety**: Python type hints ensure correct data types
- **Automatic Parsing**: Responses are automatically parsed into BaseModel instances

**Default Mode (Plain Text):**
- Agent returns plain text strings
- No JSON structure enforcement
- Works great for code generation, explanations, etc.
- Better compatibility with smaller models (8b)

**Structured Output Mode (Opt-in):**
- Agent returns validated BaseModel instances
- Type-safe, structured data
- Uses optimized field descriptions when available
- Requires larger models (70b+) for reliable results

### Enable Structured Output

Add `output_mode: structured` to your playbook:

```yaml
spec:
  output_mode: structured  # Enable structured output (opt-in, defaults to plain)
  output_fields:
    - name: implementation
      type: string
      description: The code implementation of the feature
      required: true
```

**Requirements:**
- `output_fields` must be defined
- Requires larger models (70b+) for reliable structured output
- Works best with optimized field descriptions

### Example Playbook

```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: Developer Assistant
  id: developer
spec:
  # Enable structured output
  output_mode: structured
  
  language_model:
    provider: ollama
    model: llama3.1:70b  # Larger model recommended for structured output
    api_base: http://localhost:11434
  
  output_fields:
    - name: implementation
      type: string
      description: The code implementation of the feature
      required: true
  
  optimization:
    optimize_field_descriptions: true  # Optimize field descriptions
    optimizer:
      name: GEPA
      params:
        auto: light
        reflection_lm: ollama/llama3.1:8b
```

### How It Works

When structured output is enabled:

1. **BaseModel Creation**: A Pydantic BaseModel is created from `output_fields`
2. **Optimized Descriptions**: If available, optimized field descriptions are used
3. **Agent Configuration**: Agent is configured with `output_type=BaseModel`
4. **Response Validation**: Model responses are validated against the BaseModel
5. **Type-Safe Output**: Responses are returned as BaseModel instances

**Generated Code:**
```python
# BaseModel created from output_fields
class DeveloperOutput(BaseModel):
    implementation: str = Field(
        description="Complete, deployment-ready code implementation..."  # Optimized description if available
    )

# Agent configured with structured output
agent = Agent(
    model=model,
    instructions=instructions,
    output_type=DeveloperOutput  # Structured output enabled
)
```

### Verification

When running an agent with structured output, you'll see:

```
Using structured output mode (BaseModel)
   Output Model: DeveloperOutput
   Using optimized field descriptions
```

**Response Output:**
```
Structured Output Received!
   Type: DeveloperOutput
   Model: DeveloperOutput
   📊 Pydantic v2 model validated successfully
   📋 Structured Data (JSON):
   {
     "implementation": "...actual code here..."
   }
```

### Benefits

**Type Safety**: Responses are validated against Pydantic models  
**Better Structure**: Enforces consistent output format  
**Optimized Descriptions**: Uses GEPA-optimized field descriptions  
**Validation**: Automatic validation ensures correct data types  
**Integration**: Works seamlessly with Pydantic AI's native structured output

### When to Use Structured Output

**Use structured output when:**
- You need type-safe, validated responses
- You're using larger models (70b+)
- You have well-defined output schemas
- You've optimized field descriptions
- You need consistent data structure

**Use plain text output when:**
- You're using smaller models (8b)
- You want maximum compatibility
- Output format is flexible
- You don't need structured validation
- **Default mode** - works great for most use cases

### Switching Between Modes

**Enable structured output:**
```yaml
spec:
  output_mode: structured
```

**Disable (use plain text - default):**
```yaml
spec:
  # output_mode: plain  # Default, can omit
  # or remove output_mode entirely
```

**Important:** Always recompile after changing `output_mode`:
```bash
super agent compile developer --framework pydantic-ai
```

---

## 📈 Performance Characteristics

### Baseline Performance

**Task:** Code generation and explanation
**Model:** Ollama llama3.1:8b
**Framework:** Pydantic AI

Pydantic AI achieves good baseline performance with local Ollama models. Results vary based on:
- Hardware capabilities (RAM, CPU/GPU)
- Model size and quality (8b vs 70b)
- BDD scenario complexity
- Model settings (max_tokens, top_p, etc.)

### Framework Comparison

**Pydantic AI strengths:**
- Type-safe structured outputs (validated by Pydantic)
- Native MCP support (no extra configuration)
- Modern async/await API
- Clean, simple architecture
- Works seamlessly with Ollama

**DSPy strengths:**
- More optimization targets (all signatures)
- Better for focused, well-defined tasks
- Greater improvement potential through optimization

**OpenAI SDK strengths:**
- Built-in multi-agent handoffs
- Session management
- Guardrails support

---

## 🏗️ Architecture

```
SuperSpec YAML Playbook
        ↓
    Compiler (AgentCompiler)
        ↓
Pydantic AI Pipeline Template (pydantic_ai_pipeline.py.jinja2)
        ↓
Generated Python Pipeline
        ├─ MyAssistantComponent (BaseComponent wrapper)
        │   ├─ _initialize_model() → infer_model() (Pydantic AI)
        │   ├─ _initialize_mcp_servers() → [MCPServerStdio, ...] (if enabled)
        │   ├─ _get_model_settings() → ModelSettings
        │   ├─ _initialize_agent() → Agent(
        │   │                         model,
        │   │                         instructions,  ← Optimized by GEPA!
        │   │                         model_settings,
        │   │                         toolsets=[...]  ← MCP servers
        │   │                       )
        │   └─ forward() → agent.run() (async, plain text output)
        └─ MyAssistantPipeline
            ├─ run()
            ├─ evaluate()
            ├─ optimize_with_gepa() ← Universal GEPA
            └─ run_bdd_test_suite()
```

**Note:** The template uses plain text output mode (no `output_type` parameter) for reliable responses with smaller models.

---

## 🔄 Model Configuration

### Ollama (Local) - RECOMMENDED ⭐

```yaml
spec:
  language_model:
    provider: ollama
    model: llama3.1:8b  # or llama3.1:70b for better quality
    api_base: http://localhost:11434
    max_tokens: 4000  # Adjust based on response length needs (default: 4000)
    top_p: 0.9  # Optional: Control output diversity
```

**Setup:**
```bash
# Install Ollama
brew install ollama  # macOS
# or download from https://ollama.com

# Pull model
ollama pull llama3.1:8b

# Set environment (optional, auto-configured by pipeline)
# Note: The pipeline automatically sets these if api_base is provided in playbook
export OLLAMA_BASE_URL=http://localhost:11434/v1
export OLLAMA_API_KEY=ollama  # Placeholder key (Ollama doesn't require real key)
```

The pipeline automatically:
- Adds `ollama:` prefix if missing
- Sets `OLLAMA_BASE_URL` with `/v1` suffix
- Uses Pydantic AI's `infer_model()` for automatic model creation

### OpenAI (Cloud)

```yaml
spec:
  language_model:
    provider: openai
    model: gpt-4o
    max_tokens: 4000  # Adjust as needed (default: 4000)
    top_p: 0.9  # Optional
```

**Setup:**
```bash
export OPENAI_API_KEY="sk-..."
```

Pydantic AI automatically detects OpenAI from the model string or provider field.

### Anthropic (Cloud)

```yaml
spec:
  language_model:
    provider: anthropic
    model: claude-3-5-sonnet
    max_tokens: 4000  # Adjust as needed (default: 4000)
    top_p: 0.9  # Optional (Anthropic may ignore this)
```

**Setup:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Other Providers

Pydantic AI supports 100+ providers via LiteLLM. Just specify the provider and model:

```yaml
spec:
  language_model:
    provider: google  # or groq, together, bedrock, etc.
    model: gemini-pro
```

---

## 🐛 Troubleshooting

### Model Not Found

**Symptom:** `Unknown provider: llama3.1` or `ModelHTTPError: 404`

**Solutions:**
1. Ensure model string has provider prefix: `ollama:llama3.1:8b`
2. Check `OLLAMA_BASE_URL` includes `/v1`: `http://localhost:11434/v1`
3. Verify Ollama is running: `curl http://localhost:11434/api/tags`
4. Check model is downloaded: `ollama list`

The pipeline auto-detects Ollama models, but explicit prefix is safer.

### Low Pass Rate in Evaluation

**Symptom:** Evaluation scenarios failing

**Solutions:**
1. Check BDD scenario keywords are realistic
2. Lower threshold in evaluate() method (default is 0.6)
3. Run GEPA optimization to improve instructions
4. Try different model (llama3.1:70b for more capability)
5. Adjust model settings in playbook:
   ```yaml
   spec:
     language_model:
       max_tokens: 8000  # Increase for longer responses
       top_p: 0.9
   ```

### MCP Server Connection Issues

**Symptom:** `Failed to initialize MCP server` or tools not available

**Solutions:**
1. **For stdio servers:**
   - Verify command exists: `which npx`
   - Check args are correct
   - Ensure MCP server package is installed
   
2. **For remote servers:**
   - Verify URL is accessible: `curl https://mcp-server.com/mcp`
   - Check network connectivity
   - Verify server is running

3. **General:**
   - Check server logs for errors
   - Verify `mcp` package is installed: `pip install mcp`
   - Test server independently first

### Import Error

**Symptom:** `ModuleNotFoundError: No module named 'pydantic_ai'`

**Solution:**
```bash
pip install superoptix[frameworks-pydantic-ai]
# or
pip install pydantic-ai==1.31.0
```

### Optimization Takes Too Long

**Symptom:** Optimization never completes or takes too long

> ⚠️ **Note:** Optimization is inherently resource-intensive. If it's taking too long, consider if optimization is necessary for your use case. Many agents work well without optimization.

**Quick Solutions:**

1. **Ultra Fast (~30s-1m, ~3 API calls)**: Minimal metric calls for quick verification:
   ```bash
   # Use local Ollama to avoid API costs
   super agent optimize developer --framework pydantic-ai --max-metric-calls 3 --reflection-lm ollama/llama3.1:8b
   ```

2. **Super Light (~1-2 minutes, ~10 API calls)**: Limit total metric calls:
   ```bash
   # Use local Ollama to avoid API costs
   super agent optimize developer --framework pydantic-ai --max-metric-calls 10 --reflection-lm ollama/llama3.1:8b
   ```

3. **Light Mode (Recommended - ~5-10 minutes, ~50-100 API calls)**:
   ```bash
   # Use local Ollama for cost-free optimization
   super agent optimize developer --framework pydantic-ai --auto light --reflection-lm ollama/llama3.1:8b
   ```
   
   **Cloud models are costly:**
   ```bash
   # NOT RECOMMENDED - Expensive!
   super agent optimize developer --framework pydantic-ai --auto light --reflection-lm openai/gpt-4o
   # This can cost $5-20+ per optimization run!
   ```

3. **Reduce iterations in playbook**:
   ```yaml
   optimization:
     optimizer:
       params:
         max_metric_calls: 20  # Limit total evaluations
         reflection_lm: ollama/llama3.1:8b
   ```

4. Use smaller reflection model: `--reflection-lm ollama/llama3.1:8b`
5. Reduce training dataset size (fewer BDD scenarios)

### JSON Metadata Instead of Content

**Symptom:** Agent returns JSON like `{"action": "do_something", "params": {...}}` instead of actual content

**Solution:** This was fixed in SuperOptiX 0.2.1. The template now uses plain text output mode:
```bash
pip install --upgrade superoptix
super agent compile your_agent --framework pydantic-ai  # Recompile
```

### MCP Server Not Initializing

**Symptom:** No "🛠️ Initialized MCP stdio server" message during run

**Solutions:**
1. Check playbook filename uses underscores: `my_agent_playbook.yaml` (not hyphens)
2. Verify `mcp.enabled: true` in playbook
3. Check MCP server command is correct:
   ```yaml
   mcp:
     enabled: true
     servers:
       - name: filesystem
         type: stdio
         config:
           command: npx
           args: ["-y", "@modelcontextprotocol/server-filesystem", "/private/tmp"]  # Use /private/tmp on macOS (or /tmp on Linux)
   ```

---

## 🔬 Under the Hood

### Model Initialization

The pipeline uses Pydantic AI's `infer_model()` for automatic model creation:

```python
from pydantic_ai.models import infer_model

# Auto-detects provider from model string
model = infer_model("ollama:llama3.1:8b")
# or
model = infer_model("openai:gpt-4o")
```

For Ollama, it automatically:
- Adds `ollama:` prefix if missing
- Sets `OLLAMA_BASE_URL` environment variable
- Configures OpenAI-compatible API endpoint

### Plain Text Output Mode

The template uses plain text output for reliable responses with all model sizes:

```python
# Agent configured for plain text output
agent = Agent(
    model=model,
    instructions=instructions,
    # No output_type - uses plain text mode
    toolsets=[server] if server else None,  # ← MCP servers as toolsets
)

# Result is plain text mapped to output fields
result = await agent.run(input_text)
response_text = str(result.output)

# Mapped to first output field
return {"implementation": response_text}
```

**Why Plain Text Mode?**
- Works reliably with 8b models
- No JSON formatting issues
- Natural, readable responses
- Better for code generation and documentation tasks

### MCP Server Integration

MCP servers are registered as `toolsets` on the Agent:

```python
from pydantic_ai.mcp import MCPServerStdio

server = MCPServerStdio(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/private/tmp"],  # Use /private/tmp on macOS (or /tmp on Linux)
)

agent = Agent(
    model=model,
    instructions=instructions,
    toolsets=[server],  # ← MCP tools automatically available!
)
```

### Agent Execution Flow

1. User input received
2. Component's `forward()` called (async method)
3. Agent initialized (lazy, cached)
4. `await agent.run(input)` executed (async execution)
5. Agent processes with model + tools
6. Returns `result.output` (validated BaseModel or str)
7. Mapped to output fields dict

---

## 🎯 The SuperOptiX Multi-Framework Advantage

### One Playbook, Multiple Frameworks

SuperOptiX allows you to write your agent specification once and compile to any supported framework:

```bash
# Same playbook, different frameworks
super agent compile my_agent --framework pydantic-ai
super agent compile my_agent --framework openai
super agent compile my_agent --framework deepagents

# GEPA optimization works across all frameworks
super agent optimize my_agent --framework pydantic-ai --max-metric-calls 20  # Super light test
# or
super agent optimize my_agent --framework pydantic-ai --auto light  # Recommended
```

### When to Use Pydantic AI

**Choose Pydantic AI when:**
- You need type-safe structured outputs
- You want native MCP tool integration
- You prefer modern async/await APIs
- You're building deployment applications
- You need validated, reliable responses

**Choose DSPy when:**
- You need maximum optimization flexibility
- You want to optimize multiple components
- You have well-defined, focused tasks
- You want proven optimization improvements

**Choose OpenAI SDK when:**
- You need multi-agent handoffs
- You want built-in session management
- You need guardrails support
- You prefer simple, straightforward API

---

## 📚 Additional Resources

- [Pydantic AI Documentation](https://ai.pydantic.dev)
- [Pydantic AI GitHub](https://github.com/pydantic/pydantic-ai)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [SuperOptiX Multi-Framework Guide](multi-framework.md)
- [GEPA Optimization Guide](gepa-optimization.md)
- [MCP Optimization Tutorial](../tutorials/mcp-optimization.md)

---

## 🎉 Next Steps

1. **Try the demo:** `super agent pull developer && super agent compile developer --framework pydantic-ai`
2. **Add MCP tools:** Configure MCP servers in your playbook
3. **Optimize (Optional):** Run GEPA optimization to improve performance
   - ⚠️ **Only run if:** You have high-end GPU AND understand the costs
   - ⚠️ **Resource Warning:** Makes many LLM API calls (20-600+ depending on settings)
   - ⚠️ **Cost Warning:** Use local `ollama/llama3.1:8b` to avoid API charges ($0 vs $5-100+)
   - Ultra fast: `--max-metric-calls 3` (~30s-1m, ~3 API calls)
   - Quick test: `--max-metric-calls 10` (~1-2 minutes, ~10 API calls)
   - Recommended: `--auto light` (~5-10 minutes, ~50-100 API calls)
   - **Skip optimization** if your agent already works well - it's optional!
4. **Deploy:** Use the generated pipeline in your application

### 📊 Optimization Time Guide

| Option | Command | Time | API Calls | Use Case |
|--------|---------|------|-----------|----------|
| **Ultra Fast** | `--max-metric-calls 3` | ~30s-1m | ~3 calls | Verify optimization works |
| **Super Light** | `--max-metric-calls 10` | ~1-2 min | ~10 calls | Quick test |
| **Light** | `--max-metric-calls 20` | ~2-3 min | ~20 calls | Quick test, verify it works |
| **Light** | `--auto light` | ~5-10 min | ~50-100 calls | ⭐ **Recommended** - Balanced speed/quality |
| **Medium** | `--auto medium` | ~15-30 min | ~150-300 calls | Better results, more iterations |
| **Heavy** | `--auto heavy` | ~30-60 min | ~300-600 calls | Maximum quality, deployment ready |

> ⚠️ **Cost Estimates** (with cloud models like GPT-4o):
> - Super Light: ~$0.10-2.00
> - Light: ~$0.50-10.00
> - Medium: ~$5-50.00
> - Heavy: ~$20-100+
> 
> 💡 **Save money:** Use `--reflection-lm ollama/llama3.1:8b` for **free** local optimization!

---

## 📊 Observability with LogFire

SuperOptiX includes **native LogFire integration** for Pydantic AI agents, providing comprehensive observability for your agents. See the **[LogFire Integration Guide](logfire-integration.md)** for:

- Tracing agent executions
- Monitoring LLM calls and tool usage
- Tracking token usage and costs
- Viewing traces in LogFire dashboard or local backends (Jaeger)

Happy building! 🚀
