"""Embedded knowledge base access for conversational CLI.

Hybrid approach:
1. Hardcoded curated knowledge (fast, always available)
2. Direct markdown file reading (live docs)
3. MCP filesystem client (tool calling support)

No vector DB required - uses simple keyword matching + file reading.
"""

import warnings
from pathlib import Path
from typing import List, Dict, Optional

# Suppress warnings
warnings.filterwarnings("ignore")


class EmbeddedKnowledgeAccess:
    """Hybrid knowledge access: curated + docs + MCP."""

    def __init__(self):
        """Initialize embedded knowledge access."""
        self.knowledge = self._load_curated_knowledge()
        self.docs_cache = {}
        self.project_root = self._find_project_root()

        # Try to initialize MCP client (optional)
        self.mcp_client = None
        self._init_mcp_client()

    def _find_project_root(self) -> Path:
        """Find SuperOptiX project root."""
        current = Path(__file__).parent
        while current.parent != current:
            if (current / "docs").exists() or (current / "superoptix").exists():
                return current
            current = current.parent
        return Path.cwd()

    def _init_mcp_client(self):
        """Initialize MCP client for filesystem access (optional)."""
        try:
            from .mcp_client import get_mcp_client

            self.mcp_client = get_mcp_client()
        except Exception as e:
            self.mcp_client = None

    def _load_curated_knowledge(self) -> Dict:
        """Load curated knowledge (for now, hardcoded examples)."""
        # This will be replaced with actual embedded KB loaded from file
        # For now, providing curated examples

        return {
            "memory_configuration": {
                "topic": "memory_configuration",
                "question": "How do I add memory to my agent?",
                "answer": """To add memory to your agent, update your playbook's spec:

```yaml
spec:
  memory:
    enabled: true
    enable_context_optimization: true
    max_context_tokens: 2000
```

This enables GEPA-optimized context selection.

See also: docs/guides/agent-optimization/memory.md""",
                "docs_link": "docs/guides/agent-optimization/memory.md",
            },
            "rag_configuration": {
                "topic": "rag_configuration",
                "question": "How do I add RAG to my agent?",
                "answer": """To add RAG (Retrieval-Augmented Generation), update your playbook:

```yaml
spec:
  rag:
    enabled: true
    knowledge_base: "./knowledge/docs"
    vector_database: "chroma"
    top_k: 5
```

Place your documents in the knowledge_base directory.

See also: docs/guides/agent-optimization/rag.md""",
                "docs_link": "docs/guides/agent-optimization/rag.md",
            },
            "tools_configuration": {
                "topic": "tools_configuration",
                "question": "How do I add tools to my agent?",
                "answer": """To add tools to your agent:

```yaml
spec:
  tools:
    enabled: true
    specific_tools:
      - calculator
      - web_search
```

SuperOptiX includes 29+ built-in tools across 17 categories.

See also: docs/guides/agent-optimization/tools.md""",
                "docs_link": "docs/guides/agent-optimization/tools.md",
            },
            "gepa_optimization": {
                "topic": "gepa_optimization",
                "question": "What is GEPA and how does it work?",
                "answer": """GEPA (Genetic-Pareto) is SuperOptiX's universal optimizer.

It works by:
1. Analyzing agent performance
2. Learning from examples
3. Optimizing instructions and tool usage

To use GEPA:
```bash
super agent optimize your_agent --auto medium
```

Improvement typically: 30-50% accuracy increase

See also: docs/guides/gepa-optimization.md""",
                "docs_link": "docs/guides/gepa-optimization.md",
            },
            "superspec_format": {
                "topic": "superspec_format",
                "question": "What is SuperSpec format?",
                "answer": """SuperSpec is SuperOptiX's YAML-based specification language.

Two main parts:

1. **Agent Specification** (spec section):
   - persona (role, goal, expertise)
   - tools (which tools to use)
   - rag (knowledge retrieval)
   - memory (context management)

2. **Feature Specifications** (RSpec-style BDD):
   - scenarios (test cases)
   - input/output examples

Example:
```yaml
name: my_agent

spec:
  persona:
    role: "Data Analyst"
  rag:
    enabled: true

feature_specifications:
  scenarios:
    - name: quarterly_report
      input:
        query: "Q1 sales summary"
      expected_output:
        report: "Total sales: $1.2M..."
```

See also: docs/guides/superspec.md""",
                "docs_link": "docs/guides/superspec.md",
            },
            "agent_tiers": {
                "topic": "agent_tiers",
                "question": "What's the difference between oracles and genies?",
                "answer": """SuperOptiX has two agent tiers:

**Oracles** (Basic):
- Simple chain-of-thought reasoning
- No memory or tools
- Fast to create and run
- Good for simple tasks

**Genies** (Advanced):
- Memory system for context
- Tool integration
- RAG capabilities
- Optimizable with GEPA
- Best for complex workflows

Use `super spec generate oracles <name>` for basic agents.
Use `super spec generate genies <name>` for advanced agents.

See also: docs/introduction.md""",
                "docs_link": "docs/introduction.md",
            },
            "compilation": {
                "topic": "compilation",
                "question": "How do I compile an agent?",
                "answer": """To compile an agent playbook to executable code:

```bash
super agent compile <agent_name>
```

This converts your YAML playbook into a DSPy pipeline.

You can also specify the framework:
```bash
super agent compile <agent_name> --framework langchain
super agent compile <agent_name> --framework crewai
```

The compiled pipeline is saved in: `agents/<name>/pipelines/`

See also: docs/guides/compilation.md""",
                "docs_link": "docs/guides/compilation.md",
            },
            "evaluation": {
                "topic": "evaluation",
                "question": "How do I evaluate my agent?",
                "answer": """To evaluate agent performance:

1. Create evaluation scenarios in your playbook's feature_specifications

2. Run evaluation:
```bash
super agent evaluate <agent_name>
```

Evaluation runs your agent on test scenarios and measures:
- Accuracy
- Response quality
- Tool usage
- Memory retention

Results are saved in: `agents/<name>/evaluation_results.json`

See also: docs/guides/evaluation.md""",
                "docs_link": "docs/guides/evaluation.md",
            },
            "optimization_levels": {
                "topic": "optimization_levels",
                "question": "What do the optimization levels mean?",
                "answer": """GEPA optimization levels:

**--auto low**:
- 3 generations
- Fast (5-10 min)
- 20-30% improvement
- Good for quick iterations

**--auto medium** (default):
- 5 generations
- Moderate (15-30 min)
- 30-40% improvement
- Balanced quality/speed

**--auto high**:
- 10+ generations
- Slow (30-60 min)
- 40-50% improvement
- Best quality

Add `--fresh` to clear cache and optimize from scratch.

See also: docs/guides/gepa-optimization.md""",
                "docs_link": "docs/guides/gepa-optimization.md",
            },
            "cli_commands": {
                "topic": "cli_commands",
                "question": "What CLI commands are available?",
                "answer": """Main SuperOptiX CLI commands:

**Agent Lifecycle:**
- `super spec generate {oracles|genies} <name>` - Create playbook
- `super agent compile <name>` - Compile to code
- `super agent optimize <name>` - Optimize with GEPA
- `super agent evaluate <name>` - Test performance
- `super agent run <name> --goal "..."` - Execute agent

**Management:**
- `super agent list` - Show all agents
- `super agent pull <name>` - Download pre-built agent

**Project:**
- `super init <name>` - Initialize new project

**Models:**
- `super model list` - Show available models
- `super model install <model>` - Install via Ollama

See also: docs/reference/cli.md""",
                "docs_link": "docs/reference/cli.md",
            },
            "fresh_flag": {
                "topic": "fresh_flag",
                "question": "What does the --fresh flag do?",
                "answer": """The `--fresh` flag clears DSPy's optimization cache:

```bash
super agent optimize <name> --fresh
```

**Use when:**
- Agent behavior changed
- Playbook was modified
- Want to re-optimize from scratch
- Previous optimization had issues

**Without --fresh:**
- Uses cached results
- Faster optimization
- Incremental improvements

**With --fresh:**
- Clears all caches
- Full re-optimization
- May find better solutions
- Takes longer

See also: docs/guides/gepa-optimization.md""",
                "docs_link": "docs/guides/gepa-optimization.md",
            },
            "multi_agent": {
                "topic": "multi_agent",
                "question": "How do I create multi-agent workflows?",
                "answer": """Use orchestras for multi-agent workflows:

1. Create orchestra:
```bash
super orchestra create <orchestra_name>
```

2. Define agents in orchestra playbook:
```yaml
name: development_team

agents:
  - name: developer
    role: "Code implementation"
  - name: reviewer
    role: "Code review"
  - name: tester
    role: "Test creation"
```

3. Run orchestra:
```bash
super orchestra run <orchestra_name> --goal "Build API"
```

See also: docs/guides/orchestra.md""",
                "docs_link": "docs/guides/orchestra.md",
            },
        }

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search knowledge base for relevant information.

        Hybrid search:
        1. Search curated hardcoded knowledge
        2. Search documentation files
        3. Return top results
        """
        query_lower = query.lower()
        results = []

        # 1. Search curated knowledge
        for topic_id, data in self.knowledge.items():
            score = 0

            # Match question
            if query_lower in data["question"].lower():
                score += 10

            # Match topic
            if query_lower in data["topic"].lower():
                score += 5

            # Match answer (keywords)
            if query_lower in data["answer"].lower():
                score += 2

            if score > 0:
                results.append({**data, "score": score, "source": "curated"})

        # 2. Search documentation files
        doc_results = self._search_docs(query_lower)
        results.extend(doc_results)

        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:top_k]

    def _search_docs(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search documentation markdown files."""
        results = []
        docs_dir = self.project_root / "docs"

        if not docs_dir.exists():
            return results

        # Search relevant doc files based on query keywords
        relevant_files = self._find_relevant_docs(query, docs_dir)

        for file_path in relevant_files[:max_results]:
            try:
                content = self._read_doc_file(file_path)
                if content:
                    # Simple keyword matching in content
                    score = self._score_content(query, content)
                    if score > 0:
                        results.append(
                            {
                                "topic": file_path.stem,
                                "question": f"Documentation: {file_path.name}",
                                "answer": self._extract_relevant_section(
                                    content, query
                                ),
                                "docs_link": str(
                                    file_path.relative_to(self.project_root)
                                ),
                                "score": score,
                                "source": "docs",
                            }
                        )
            except Exception as e:
                continue

        return results

    def _find_relevant_docs(self, query: str, docs_dir: Path) -> List[Path]:
        """Find relevant documentation files based on query."""
        keywords = {
            "memory": ["memory-optimization.md", "memory.md"],
            "rag": ["rag.md", "retrieval.md"],
            "tool": ["tools.md", "mcp-tools.md"],
            "optimize": ["gepa-optimization.md", "prompt-optimization.md"],
            "compile": ["compilation.md"],
            "agent": ["agent-optimization"],
            "spec": ["superspec.md", "bdd.md"],
            "evaluate": ["evaluation.md"],
        }

        relevant_files = []

        # Find files based on keywords
        for keyword, filenames in keywords.items():
            if keyword in query:
                for filename in filenames:
                    # Search in docs/guides/
                    guides = docs_dir / "guides"
                    if guides.exists():
                        for md_file in guides.rglob(f"*{filename}*"):
                            if md_file.is_file():
                                relevant_files.append(md_file)

        # Also search all guides if no specific matches
        if not relevant_files:
            guides = docs_dir / "guides"
            if guides.exists():
                for md_file in guides.glob("*.md"):
                    relevant_files.append(md_file)

        return list(set(relevant_files))[:10]  # Deduplicate and limit

    def _read_doc_file(self, file_path: Path) -> Optional[str]:
        """Read and cache documentation file."""
        if file_path in self.docs_cache:
            return self.docs_cache[file_path]

        try:
            content = file_path.read_text(encoding="utf-8")
            self.docs_cache[file_path] = content
            return content
        except:
            return None

    def _score_content(self, query: str, content: str) -> int:
        """Score content relevance to query."""
        content_lower = content.lower()
        query_words = query.split()

        score = 0
        for word in query_words:
            if len(word) > 2:  # Skip short words
                count = content_lower.count(word.lower())
                score += count * 2

        return min(score, 50)  # Cap at 50

    def _extract_relevant_section(
        self, content: str, query: str, max_length: int = 500
    ) -> str:
        """Extract the most relevant section from content."""
        lines = content.split("\n")
        query_words = set(query.lower().split())

        # Find paragraph with most query word matches
        best_section = []
        best_score = 0
        current_section = []

        for line in lines:
            if line.strip():
                current_section.append(line)
                if len(current_section) > 10:  # Max 10 lines per section
                    current_section.pop(0)
            else:
                # End of paragraph
                if current_section:
                    section_text = " ".join(current_section).lower()
                    score = sum(1 for word in query_words if word in section_text)
                    if score > best_score:
                        best_score = score
                        best_section = current_section[:]
                current_section = []

        if best_section:
            result = "\n".join(best_section)
            if len(result) > max_length:
                result = result[:max_length] + "..."
            return result

        # Fallback: return first few lines
        return "\n".join(lines[:10])

    def get_by_topic(self, topic: str) -> Optional[Dict]:
        """Get knowledge by topic."""
        return self.knowledge.get(topic)

    def list_topics(self) -> List[str]:
        """List all available topics."""
        return list(self.knowledge.keys())
