"""Intent parser for natural language understanding.

Uses DSPy to parse user's natural language input into structured intents.
"""

import warnings
from typing import Dict, Any, Optional
from dataclasses import dataclass

warnings.filterwarnings("ignore")

import dspy


@dataclass
class Intent:
    """Parsed user intent."""

    action: str  # build, compile, optimize, evaluate, run, help, info, etc.
    target: Optional[str]  # agent name, resource name
    parameters: Dict[str, Any]  # additional parameters
    confidence: float  # confidence score 0-1
    original_input: str  # original user input


class IntentRecognition(dspy.Signature):
    """You are an expert AI assistant for SuperOptiX, a full-stack AI agent optimization framework.

    Your job is to understand what the user wants to do and map it to the correct SuperOptiX action.

    ## SuperOptiX Overview:
    SuperOptiX helps developers build, compile, optimize, and deploy AI agents using:
    - **Agent Playbooks**: YAML specifications (called "specs") defining agent behavior
    - **GEPA Optimization**: Genetic Evolution of Prompting Algorithms for agent improvement
    - **DSPy Compilation**: Converts playbooks into executable Python pipelines
    - **Evaluation**: Tests agent performance on datasets
    - **Memory Systems**: Adds context retention to agents
    - **Tools & RAG**: Integrates external actions and knowledge retrieval

    ## Core Actions You Must Recognize:

    1. **build/create** - User wants to create a new agent
       Examples: "build an agent", "create a chatbot", "make a code reviewer"

    2. **compile** - User wants to convert playbook to executable code
       Examples: "compile my agent", "generate code for it", "turn playbook into pipeline"

    3. **optimize** - User wants to improve agent performance using GEPA
       Examples: "optimize the agent", "make it better", "improve performance", "tune prompts"

    4. **evaluate** - User wants to test agent performance
       Examples: "test the agent", "evaluate it", "run benchmarks", "check quality"

    5. **run** - User wants to execute the agent on a task
       Examples: "run the agent", "execute it", "try it out", "use the agent for..."

    6. **list** - User wants to see available resources
       Examples: "show agents", "list all agents", "what agents exist", "show playbooks"

    7. **help** - User needs information or assistance
       Examples: "how do I...", "what is...", "help with...", "explain..."

    ## Target Extraction Rules:
    - If user says "build a code review agent" → target is "code_review"
    - If user says "optimize my chatbot" → target is "chatbot"
    - If user says "compile developer" → target is "developer"
    - Remove filler words: "a", "the", "my", "me", "an"
    - Join multi-word names with underscores: "code review" → "code_review"
    - If no specific name given, target is "none"

    ## Parameter Extraction:
    Extract these when mentioned:
    - tier: "oracles" (basic) or "genies" (advanced) - default to "genies"
    - namespace: software, healthcare, finance, etc.
    - goal: the task to run agent on (for "run" action)
    - auto: optimization level - low, medium, high
    - reflection_lm: model for GEPA reflection (gpt-4o, gpt-4o-mini, claude-3-5-sonnet) - default to "gpt-4o-mini"
    - framework: dspy, langchain, crewai (for compile)

    ## Examples:
    Input: "build me a developer agent"
    → action=build, target=developer, parameters={"tier": "genies", "namespace": "software"}

    Input: "optimize customer_support with high quality"
    → action=optimize, target=customer_support, parameters={"auto": "high"}

    Input: "compile it"
    → action=compile, target=none (will use context), parameters={}

    Input: "how do I add memory to an agent?"
    → action=help, target=none, parameters={"topic": "memory"}

    Now parse the user's input carefully, considering context from conversation history.
    """

    user_input: str = dspy.InputField(
        desc="The user's natural language request or question"
    )
    available_commands: str = dspy.InputField(
        desc="List of available SuperOptiX CLI commands"
    )
    conversation_history: str = dspy.InputField(
        desc="Recent conversation context showing previous actions and agents mentioned"
    )
    knowledge_context: str = dspy.InputField(
        desc="Relevant SuperOptiX documentation and examples retrieved for this query"
    )

    intent_action: str = dspy.OutputField(
        desc="Primary action: build, compile, optimize, evaluate, run, help, list, or show. Choose the MOST specific action that matches user intent."
    )
    intent_target: str = dspy.OutputField(
        desc="Target agent/resource name extracted from input. Use underscores for multi-word names. Return 'none' if no specific target."
    )
    intent_parameters: str = dspy.OutputField(
        desc='JSON object with extracted parameters like {"tier": "genies", "namespace": "software", "goal": "...", "auto": "medium"}'
    )
    confidence: float = dspy.OutputField(
        desc="Your confidence in this parse from 0.0 to 1.0. Be honest - if input is ambiguous, give lower confidence."
    )
    reasoning: str = dspy.OutputField(
        desc="Brief explanation: 'User wants to [action] because they said [key phrase]. Target is [target] extracted from [where]. Parameters: [why]'"
    )


class IntentParser:
    """Parse natural language into SuperOptiX intents using DSPy."""

    def __init__(self, lm=None, knowledge_base=None):
        """Initialize intent parser.

        Args:
            lm: DSPy language model. If None, will try to use configured model.
            knowledge_base: Embedded knowledge base for RAG context
        """
        # DON'T configure DSPy globally - store LM locally
        # if lm:
        #     dspy.configure(lm=lm)  # ← REMOVED

        self.recognizer = dspy.ChainOfThought(IntentRecognition)
        self.knowledge_base = knowledge_base
        self.lm = lm

    def parse(self, user_input: str, conversation_history: str = "") -> Intent:
        """Parse user input into intent.

        Args:
            user_input: User's natural language input
            conversation_history: Previous conversation context

        Returns:
            Intent object with parsed information
        """
        # Available SuperOptiX commands with detailed descriptions
        available_commands = """
SuperOptiX CLI Commands Reference:

🎯 AGENT LIFECYCLE:
- super spec generate {oracles|genies} <name> --namespace <domain>
  Create agent playbook. Oracles=basic, Genies=advanced with memory/tools/RAG
  Examples: 
    super spec generate genies developer --namespace software
    super spec generate oracles chatbot --namespace customer_support

- super agent compile <name> [--framework dspy|langchain|crewai]
  Compile agent playbook to executable pipeline code
  Example: super agent compile developer

- super agent optimize <name> --auto {low|medium|high} [--fresh]
  Optimize agent using GEPA (Genetic Evolution of Prompting Algorithms)
  --auto low: Fast, 3 generations
  --auto medium: Balanced, 5 generations  
  --auto high: Deep, 10+ generations
  --fresh: Clear cache and optimize from scratch
  Example: super agent optimize developer --auto high --fresh

- super agent evaluate <name>
  Test agent performance on evaluation dataset
  Example: super agent evaluate developer

- super agent run <name> --goal "task description"
  Execute agent on a specific task
  Example: super agent run developer --goal "Review this code for bugs"

📦 AGENT MANAGEMENT:
- super agent list
  Show all agents in current project

- super agent pull <name>
  Download pre-built agent from registry
  Example: super agent pull code-reviewer

🎼 MULTI-AGENT ORCHESTRATION:
- super orchestra create <name>
  Create multi-agent workflow
  Example: super orchestra create development_team

- super orchestra run <name> --goal "..."
  Execute multi-agent workflow
  Example: super orchestra run development_team --goal "Build a REST API"

🤖 MODEL MANAGEMENT:
- super model list
  Show available AI models

- super model install <model>
  Install new model via Ollama
  Example: super model install llama3.1:8b

📂 PROJECT:
- super init <name>
  Initialize new SuperOptiX project
  Example: super init my_agents
"""

        # Get relevant knowledge context from RAG if available
        knowledge_context = ""
        if self.knowledge_base:
            try:
                # Search knowledge base for relevant context
                search_results = self.knowledge_base.search(user_input, top_k=3)
                if search_results:
                    knowledge_context = "\n\n".join(
                        [f"📚 Relevant Info:\n{result}" for result in search_results]
                    )
            except:
                pass

        # If no RAG context, provide essential context based on keywords
        if not knowledge_context:
            knowledge_context = self._get_contextual_hints(user_input)

        # Run DSPy intent recognition with full context
        try:
            if self.lm is None:
                # No LM configured, use fallback
                return self._fallback_parse(user_input)

            # Use LM directly with recognizer (don't rely on global dspy.configure)
            if self.lm:
                # Temporarily configure for this call only
                import dspy

                with dspy.context(lm=self.lm):
                    result = self.recognizer(
                        user_input=user_input,
                        available_commands=available_commands,
                        conversation_history=conversation_history,
                        knowledge_context=knowledge_context,
                    )
            else:
                result = self.recognizer(
                    user_input=user_input,
                    available_commands=available_commands,
                    conversation_history=conversation_history,
                    knowledge_context=knowledge_context,
                )

            # Parse parameters
            import json

            try:
                parameters = (
                    json.loads(result.intent_parameters)
                    if result.intent_parameters
                    else {}
                )
            except Exception as e:
                parameters = {}

            # Extract action and target
            action = result.intent_action.lower().strip()
            target = result.intent_target.strip() if result.intent_target else None

            # Handle "none" or empty targets
            if target and target.lower() in ["none", "null", ""]:
                target = None

            return Intent(
                action=action,
                target=target,
                parameters=parameters,
                confidence=float(result.confidence) if result.confidence else 0.5,
                original_input=user_input,
            )

        except Exception as e:
            # Fallback to simple keyword matching
            return self._fallback_parse(user_input)

    def _get_contextual_hints(self, user_input: str) -> str:
        """Provide contextual hints based on keywords in input."""
        hints = []
        user_lower = user_input.lower()

        if any(word in user_lower for word in ["memory", "context", "remember"]):
            hints.append(
                "💾 Memory: Use 'genies' tier for agents with memory. Memory helps agents retain context across conversations."
            )

        if any(word in user_lower for word in ["tool", "action", "external"]):
            hints.append(
                "🔧 Tools: Genie agents support external tool integration for actions like API calls, file operations, etc."
            )

        if any(
            word in user_lower for word in ["rag", "knowledge", "retrieval", "search"]
        ):
            hints.append(
                "🔍 RAG: Genie agents can use retrieval-augmented generation for accessing knowledge bases."
            )

        if any(
            word in user_lower for word in ["optimize", "improve", "better", "tune"]
        ):
            hints.append(
                "🎯 Optimization: GEPA optimizes prompts using genetic algorithms. Use --auto high for best results."
            )

        if any(word in user_lower for word in ["compile", "code", "pipeline"]):
            hints.append(
                "⚡ Compilation: Converts YAML playbooks to executable DSPy/LangChain/CrewAI code."
            )

        if any(word in user_lower for word in ["evaluate", "test", "benchmark"]):
            hints.append(
                "📊 Evaluation: Tests agent on datasets. Create eval.yaml in your project with test cases."
            )

        return "\n".join(hints) if hints else "No specific hints for this query."

    def _fallback_parse(self, user_input: str) -> Intent:
        """Fallback parser using simple keyword matching."""
        user_lower = user_input.lower()

        # More specific keyword matching (order matters!)
        if (
            any(word in user_lower for word in ["build", "create"])
            and "agent" in user_lower
        ):
            action = "build"
        elif "compile" in user_lower:
            action = "compile"
        elif "optimize" in user_lower or "improve" in user_lower:
            action = "optimize"
        elif "evaluate" in user_lower or "test" in user_lower:
            action = "evaluate"
        elif "run" in user_lower or "execute" in user_lower:
            action = "run"
        elif "list" in user_lower or "show" in user_lower:
            action = "list"
        elif (
            user_lower.startswith("help")
            or user_lower.startswith("how")
            or user_lower.startswith("what")
        ):
            action = "help"
        else:
            # Default to unknown if we can't match
            action = "unknown"

        # Extract potential agent name (improved heuristic)
        stopwords = {
            "build",
            "create",
            "compile",
            "optimize",
            "run",
            "evaluate",
            "test",
            "a",
            "the",
            "my",
            "an",
            "with",
            "for",
            "me",
            "you",
            "can",
            "please",
        }
        words = user_input.lower().split()
        target = None

        # For build/create actions, extract agent type description
        if action in ["build", "create"]:
            # Find the action word index
            action_idx = -1
            for action_word in ["build", "create", "generate"]:
                if action_word in words:
                    action_idx = words.index(action_word)
                    break

            if action_idx >= 0 and action_idx + 1 < len(words):
                # Get descriptive words after action (skip articles, "me", and "agent")
                agent_type_words = []
                for word in words[action_idx + 1 :]:
                    cleaned = (
                        word.replace(",", "")
                        .replace(".", "")
                        .replace('"', "")
                        .replace("'", "")
                    )
                    if cleaned not in stopwords and cleaned not in ["agent", "agents"]:
                        agent_type_words.append(cleaned)

                if agent_type_words:
                    target = "_".join(agent_type_words)

        # For evaluate/test/run/optimize/compile actions, look for agent name after action word
        if action in ["evaluate", "test", "run", "optimize", "compile"] and not target:
            # Find action word
            action_words = {
                "evaluate": "evaluate",
                "test": "test",
                "run": "run",
                "optimize": "optimize",
                "compile": "compile",
            }
            action_word = action_words.get(action, action)

            if action_word in words:
                action_idx = words.index(action_word)
                # Get words after action
                for word in words[action_idx + 1 :]:
                    cleaned = (
                        word.replace(",", "")
                        .replace(".", "")
                        .replace('"', "")
                        .replace("'", "")
                    )
                    if (
                        cleaned not in stopwords
                        and cleaned not in ["agent", "agents"]
                        and len(cleaned) > 2
                    ):
                        target = cleaned
                        break

        # For other actions, find first non-stopword
        if not target:
            for word in words:
                cleaned = (
                    word.replace(",", "")
                    .replace(".", "")
                    .replace('"', "")
                    .replace("'", "")
                )
                if (
                    cleaned not in stopwords
                    and cleaned not in ["agent", "agents"]
                    and len(cleaned) > 2
                ):
                    target = cleaned
                    break

        return Intent(
            action=action,
            target=target,
            parameters={},
            confidence=0.6,
            original_input=user_input,
        )
