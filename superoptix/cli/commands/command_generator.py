"""Command generator for converting intents to CLI commands.

Maps parsed intents to actual SuperOptiX CLI commands.
"""

import warnings
from typing import List

warnings.filterwarnings("ignore")

import dspy
from .intent_parser import Intent


class CommandGeneration(dspy.Signature):
    """Generate CLI commands from parsed intent.

    SuperOptiX command format examples:
    - super spec generate genie agent_name
    - super agent compile agent_name
    - super agent optimize agent_name --auto medium
    - super agent evaluate agent_name
    - super agent run agent_name --goal "task description"
    """

    intent_action: str = dspy.InputField(
        desc="Parsed action (build, compile, optimize, etc.)"
    )
    intent_target: str = dspy.InputField(desc="Target agent or resource name")
    intent_parameters: str = dspy.InputField(desc="Additional parameters as JSON")
    project_context: str = dspy.InputField(
        desc="Current project state and available agents"
    )

    cli_commands: str = dspy.OutputField(desc="CLI commands to execute (one per line)")
    explanation: str = dspy.OutputField(
        desc="Brief explanation of what these commands will do"
    )


class CommandGenerator:
    """Generate CLI commands from intents using DSPy."""

    # Valid SuperOptiX namespaces
    VALID_NAMESPACES = {
        "software",
        "healthcare",
        "finance",
        "education",
        "legal",
        "marketing",
        "manufacturing",
        "retail",
        "transportation",
        "energy",
        "agriculture",
        "consulting",
        "government",
        "human_resources",
        "hospitality",
        "real_estate",
        "media",
        "gaming",
    }

    # Keyword to namespace mapping
    NAMESPACE_KEYWORDS = {
        "code": "software",
        "developer": "software",
        "programming": "software",
        "api": "software",
        "app": "software",
        "software": "software",
        "tech": "software",
        "customer": "marketing",
        "support": "marketing",
        "sales": "marketing",
        "marketing": "marketing",
        "patient": "healthcare",
        "medical": "healthcare",
        "health": "healthcare",
        "healthcare": "healthcare",
        "doctor": "healthcare",
        "finance": "finance",
        "accounting": "finance",
        "banking": "finance",
        "trading": "finance",
        "legal": "legal",
        "law": "legal",
        "contract": "legal",
        "education": "education",
        "teaching": "education",
        "learning": "education",
        "student": "education",
        "game": "gaming",
        "gaming": "gaming",
        "media": "media",
        "content": "media",
        "hr": "human_resources",
        "recruiting": "human_resources",
        "hotel": "hospitality",
        "restaurant": "hospitality",
        "real_estate": "real_estate",
        "property": "real_estate",
    }

    def __init__(self, lm=None):
        """Initialize command generator.

        Args:
                lm: DSPy language model. If None, will try to use configured model.
        """
        # Don't configure globally - store LM locally
        self.lm = lm
        self.generator = dspy.ChainOfThought(CommandGeneration)

    def _infer_namespace(self, agent_name: str, intent_params: dict) -> str:
        """Infer namespace from agent name and parameters.

        Args:
                agent_name: Agent name/target
                intent_params: Intent parameters

        Returns:
                Valid namespace
        """
        # Check if namespace explicitly provided
        if "namespace" in intent_params:
            ns = intent_params["namespace"].lower()
            if ns in self.VALID_NAMESPACES:
                return ns

        # Infer from agent name
        if agent_name:
            agent_lower = agent_name.lower()
            for keyword, namespace in self.NAMESPACE_KEYWORDS.items():
                if keyword in agent_lower:
                    return namespace

        # Default to software
        return "software"

    def generate(self, intent: Intent, project_context: str = "") -> List[str]:
        """Generate CLI commands from intent.

        Args:
                intent: Parsed intent
                project_context: Current project state

        Returns:
                List of CLI command strings to execute
        """
        # Use simple rule-based generation (DSPy optional for complex cases)
        return self._rule_based_generation(intent, project_context)

    def _rule_based_generation(self, intent: Intent, project_context: str) -> List[str]:
        """Generate commands using rule-based approach."""
        commands = []

        action = intent.action
        target = intent.target or "my_agent"
        params = intent.parameters

        if action == "build" or action == "create":
            # Build agent
            tier = params.get("tier", "genies")  # Default to 'genies' (advanced)
            namespace = self._infer_namespace(
                target, params
            )  # Intelligent namespace inference
            commands.append(
                f"super spec generate {tier} {target} --namespace {namespace}"
            )

        elif action == "compile":
            # Compile agent
            framework = params.get("framework", "dspy")
            if framework != "dspy":
                commands.append(f"super agent compile {target} --framework {framework}")
            else:
                commands.append(f"super agent compile {target}")

        elif action == "optimize":
            # Optimize agent
            auto_level = params.get("auto", "medium")
            fresh = params.get("fresh", False)
            reflection_lm = params.get(
                "reflection_lm", "gpt-4o-mini"
            )  # Default reflection model

            cmd = f"super agent optimize {target} --auto {auto_level} --reflection-lm {reflection_lm}"
            if fresh:
                cmd += " --fresh"
            commands.append(cmd)

        elif action == "evaluate" or action == "test":
            # Evaluate agent
            commands.append(f"super agent evaluate {target}")

        elif action == "run" or action == "execute":
            # Run agent
            goal = params.get("goal", "Complete the task")
            commands.append(f'super agent run {target} --goal "{goal}"')

        elif action == "list" or action == "show":
            # List resources
            if "agent" in intent.original_input.lower():
                commands.append("super agent list")
            elif "playbook" in intent.original_input.lower():
                # Use slash command instead
                return ["/playbooks"]
            elif "model" in intent.original_input.lower():
                return ["/model list"]
            else:
                commands.append("super agent list")

        elif action == "pull" or action == "add":
            # Pull pre-built agent
            commands.append(f"super agent pull {target}")

        elif action == "init" or action == "initialize":
            # Initialize project
            commands.append(f"super init {target}")

        elif action == "help" or action == "info":
            # Show help
            return ["/help"]

        else:
            # Unknown action
            return []

        return commands

    def _dspy_generation(self, intent: Intent, project_context: str) -> List[str]:
        """Generate commands using DSPy (for complex cases)."""
        import json

        try:
            result = self.generator(
                intent_action=intent.action,
                intent_target=intent.target or "unknown",
                intent_parameters=json.dumps(intent.parameters),
                project_context=project_context,
            )

            # Parse commands from result
            commands = [
                cmd.strip() for cmd in result.cli_commands.split("\n") if cmd.strip()
            ]

            return commands

        except Exception as e:
            # Fallback to rule-based
            return self._rule_based_generation(intent, project_context)
