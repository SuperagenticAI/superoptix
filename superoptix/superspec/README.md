# SuperSpec DSL - Agent Playbook Definition Language

**SuperSpec** is a comprehensive Domain-Specific Language (DSL) for defining Oracle and Genie tier agent playbooks in the SuperOptiX framework. It provides a structured, validated approach to creating AI agents with clear tier-based capabilities.

## Overview

SuperSpec (Super Specification eXtended) brings declarative configuration to AI agent development, similar to how Kubernetes revolutionized container orchestration. It ensures proper tier compliance, validates configurations, and provides rich tooling for agent playbook management.

## Key Features

### 🎯 **Tier-Based Design**
- **Oracle Tier**: Basic question-answering with Chain of Thought reasoning
- **Genie Tier**: Advanced agents with tools, memory, and RAG capabilities

### 🔒 **Validation & Compliance**
- Automatic tier feature validation
- Current version limitation enforcement
- Schema-based configuration validation
- Playbook linting and error detection

### 🛠️ **Rich Tooling**
- Template generation for common use cases
- Playbook parsing and analysis
- Validation and linting tools
- JSON/YAML format support

### 📚 **Comprehensive Schema**
- Complete DSL specification
- Tier-specific feature matrices
- Validation rules and constraints
- Documentation generation

## Agent Tiers

### Oracle Tier (Free)
```yaml
metadata:
  level: oracles
features:
  - Question-answering with basic thinking
  - Chain of Thought reasoning  
  - Basic evaluation (exact match, F1)
  - Basic optimization (BootstrapFewShot)
  - Sequential task orchestration
```

### Genie Tier (Free)
```yaml
metadata:
  level: genies
features:
  - All Oracle capabilities plus:
  - Tool integration and ReAct reasoning
  - RAG (knowledge retrieval)
  - Agent memory (short-term and episodic)
  - Basic streaming responses
```

## Quick Start

### 1. Generate a Basic Oracle Agent

```python
from superoptix.superspec import SuperSpecXGenerator

generator = SuperSpecXGenerator()

# Generate Oracle tier agent
oracle_agent = generator.generate_oracle_template(
    name="Math Tutor",
    namespace="education", 
    role="Mathematics Teacher",
    description="Helps students learn mathematics concepts"
)

# Save to file
generator.save_template(oracle_agent, "math_tutor_oracle.yaml")
```

### 2. Generate an Advanced Genie Agent

```python
# Generate Genie tier agent with tools and memory
genie_agent = generator.generate_genie_template(
    name="Code Assistant", 
    namespace="software",
    role="Senior Developer",
    enable_memory=True,
    enable_tools=True,
    enable_rag=False
)

generator.save_template(genie_agent, "code_assistant_genie.yaml")
```

### 3. Validate Playbooks

```python
from superoptix.superspec import SuperSpecXValidator

validator = SuperSpecXValidator()

# Validate a playbook file
result = validator.validate_file("math_tutor_oracle.yaml")

if result["valid"]:
    print("✅ Playbook is valid!")
else:
    print("❌ Validation errors:")
    for error in result["errors"]:
        print(f"  - {error}")
```

### 4. Parse and Analyze Playbooks

```python
from superoptix.superspec import SuperSpecXParser

parser = SuperSpecXParser()

# Parse a single playbook
spec = parser.parse_file("code_assistant_genie.yaml")
print(f"Agent: {spec.metadata.name} (Tier: {spec.metadata.level})")

# Parse all playbooks in a directory
specs = parser.parse_directory("agents/", "*.yaml")
summary = parser.get_parsing_summary()
print(f"Parsed {summary['total_parsed']} agents")
print(f"Tier distribution: {summary['tier_distribution']}")
```

## Playbook Structure

### Basic Structure
```yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: "Agent Name"
  id: "agent-id"
  namespace: "domain"
  level: "oracle|genie"
  version: "1.0.0"
spec:
  language_model:
    provider: "ollama"
    model: "llama3.2:1b"
  persona:
    role: "Assistant Role"
    goal: "Agent objective"
  tasks:
    - name: "main_task"
      instruction: "Task instruction"
      inputs: [...]
      outputs: [...]
  agentflow:
    - name: "step1"
      type: "Think"
      task: "main_task"
```

### Oracle-Specific Features
```yaml
spec:
  agentflow:
    - type: "Think"      # ✅ Allowed
    - type: "Generate"   # ✅ Allowed  
    - type: "Compare"    # ✅ Allowed
    - type: "Route"      # ✅ Allowed
    # - type: "ActWithTools"  # ❌ Requires Genie
    # - type: "Search"        # ❌ Requires Genie
  
  # These features are forbidden in Oracle tier:
  # memory: {...}         # ❌ Requires Genie
  # tool_calling: {...}   # ❌ Requires Genie  
  # retrieval: {...}      # ❌ Requires Genie
```

### Genie-Specific Features
```yaml
spec:
  # All Oracle features plus:
  
  agentflow:
    - type: "ActWithTools"  # ✅ Tool usage
    - type: "Search"        # ✅ Knowledge retrieval
  
  memory:                   # ✅ Agent memory
    enabled: true
    short_term:
      capacity: 100
    episodic:
      enabled: true
  
  tool_calling:             # ✅ Tool integration
    enabled: true
    available_tools: ["calculator", "web_search"]
  
  retrieval:                # ✅ RAG capabilities
    enabled: true
    retriever_type: "ChromaDB"
```

## Validation Rules

### Tier Compliance
- Oracle agents cannot use Genie-only features
- Agentflow steps must match tier capabilities
- Memory, tools, and RAG require Genie tier

### Current Version Limitations
- Only BootstrapFewShot optimization allowed
- Sequential orchestration only
- No advanced enterprise features

### Schema Validation
- Required fields must be present
- Field types must match specification
- Enum values must be from allowed lists
- Semantic versioning for versions

## Namespaces

SuperSpec supports organized agent development through namespaces:

```yaml
# Supported namespaces
software          # Development, DevOps, Architecture
education         # Tutoring, Teaching, Training  
healthcare        # Medical, Wellness, Pharmacy
finance           # Banking, Investment, Insurance
marketing         # Campaigns, Content, Social Media
legal             # Contracts, Compliance, Research
consulting        # Strategy, Business Analysis
retail            # Sales, Customer Service, Inventory
manufacturing     # Production, Quality, Safety
transportation    # Logistics, Fleet, Route Planning
```

## CLI Integration

```bash
# Generate templates
superoptix agent generate --tier oracle --name "Math Tutor" --namespace education

# Validate playbooks  
superoptix agent validate agents/math_tutor.yaml

# Lint multiple playbooks
superoptix agent lint agents/*.yaml

# Show agent information
superoptix agent info agents/math_tutor.yaml
```

## Advanced Usage

### Custom Template Generation
```python
# Generate templates for an entire namespace
generator = SuperSpecXGenerator()
files = generator.generate_namespace_templates(
    namespace="healthcare",
    output_dir="./healthcare_agents",
    tiers=["oracles", "genies"]
)

print(f"Generated {len(files)} playbook templates")
```

### Batch Validation
```python
# Validate all playbooks in a directory
validator = SuperSpecXValidator()
results = []

for file_path in Path("agents/").glob("*.yaml"):
    result = validator.validate_file(str(file_path))
    results.append(result)

summary = validator.get_validation_summary(results)
print(f"Validation rate: {summary['validation_rate']:.1%}")
```

### Schema Introspection
```python
from superoptix.superspec import SuperSpecXSchema

# Get tier-specific features
oracle_features = SuperSpecXSchema.get_tier_features("oracles")
genie_features = SuperSpecXSchema.get_tier_features("genies")

# Check feature compatibility
issues = SuperSpecXSchema.validate_tier_compatibility(
    tier="oracles", 
    features=["memory", "tools"]
)
```

## Best Practices

### 1. **Start with Oracle**
Begin with Oracle tier for simple use cases, upgrade to Genie when you need tools or memory.

### 2. **Use Namespaces**
Organize agents by domain for better discoverability and maintenance.

### 3. **Validate Early**
Use validation tools during development to catch issues early.

### 4. **Follow Naming Conventions**
- Use descriptive agent names
- Use kebab-case for IDs
- Follow semantic versioning

### 5. **Document Your Agents**
- Add clear descriptions
- Define proper input/output schemas
- Include usage examples

## Integration with SuperOptiX

SuperSpec DSL integrates seamlessly with SuperOptiX components:

```python
from superoptix.superspec import SuperSpecXParser
from superoptix.compiler import AgentCompiler

# Parse playbook
parser = SuperSpecXParser()
spec = parser.parse_file("my_agent.yaml")

# Compile to executable agent
compiler = AgentCompiler()
agent = compiler.compile_agent(spec)

# Run the agent
result = agent.run(input_data={"query": "Hello, world!"})
```

## Troubleshooting

### Common Validation Errors

**Error**: `Feature 'memory' requires Genie tier`
**Solution**: Either upgrade to Genie tier or remove the memory configuration.

**Error**: `Invalid agentflow step type 'ActWithTools' for oracle tier`
**Solution**: Use only Oracle-allowed step types: Generate, Think, Compare, Route.

**Error**: `Missing required metadata field: version`
**Solution**: Add a semantic version field to metadata section.

### Performance Tips

- Use caching for large-scale validation
- Parse directories in parallel when possible
- Enable validation sampling for huge codebases

## Contributing

The SuperSpec DSL is part of the SuperOptiX project.

### Adding New Features
1. Update the schema definitions
2. Add validation rules
3. Update template generators
4. Add tests and documentation

### Extending Namespaces
1. Add namespace to `VALID_NAMESPACES`
2. Create namespace-specific templates
3. Add validation rules if needed

## License

SuperSpec DSL is released under the MIT License as part of SuperOptiX.

---

**Ready to build amazing AI agents?** Start with SuperSpec DSL!

- 💬 **Discussions**: https://github.com/SuperagenticAI/superoptix/discussions  
- 🐛 **Issues**: https://github.com/SuperagenticAI/superoptix/issues 