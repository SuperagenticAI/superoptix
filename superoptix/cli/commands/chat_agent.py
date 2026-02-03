"""Conversational agent for natural language interaction.

Orchestrates intent parsing, command generation, execution, and response formatting.
"""

import warnings
import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path

warnings.filterwarnings("ignore")

from rich.console import Console
from .intent_parser import IntentParser, Intent
from .command_generator import CommandGenerator
from .response_formatter import ResponseFormatter


class ConversationContext:
    """Manages conversation state and history."""

    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self.current_agent: Optional[str] = None
        self.project_path: str = str(Path.cwd())

    def add_interaction(
        self, user_input: str, intent: Intent, commands: List[str], results: List[Dict]
    ):
        """Add interaction to history."""
        self.history.append(
            {
                "user_input": user_input,
                "intent": {
                    "action": intent.action,
                    "target": intent.target,
                    "confidence": intent.confidence,
                },
                "commands": commands,
                "results": results,
            }
        )

        # Update current context
        if intent.action in ["build", "create", "compile", "optimize"]:
            self.current_agent = intent.target

    def get_history_summary(self, last_n: int = 5) -> str:
        """Get summary of recent conversation."""
        recent = self.history[-last_n:]
        summary = []

        for interaction in recent:
            summary.append(f"User: {interaction['user_input']}")
            summary.append(f"Action: {interaction['intent']['action']}")
            if interaction["intent"]["target"]:
                summary.append(f"Target: {interaction['intent']['target']}")

        return "\n".join(summary)

    def get_project_state(self) -> str:
        """Get current project state."""
        state = []
        state.append(f"Current directory: {self.project_path}")

        if self.current_agent:
            state.append(f"Working on agent: {self.current_agent}")

        # Check for agents in project
        agents_dir = Path.cwd() / "agents"
        if agents_dir.exists():
            agent_files = list(agents_dir.glob("*_playbook.yaml"))
            agent_names = [f.stem.replace("_playbook", "") for f in agent_files]
            state.append(f"Available agents: {', '.join(agent_names)}")

        return "\n".join(state)


class ConversationalAgent:
    """Main conversational agent for natural language interaction."""

    def __init__(self, console: Console, config: dict):
        """Initialize conversational agent.

        Args:
                console: Rich console for output
                config: Configuration dict with model settings
        """
        self.console = console
        self.config = config
        self.context = ConversationContext()

        # Initialize DSPy LM if available
        self.lm = self._initialize_lm(config)

        # Initialize embedded knowledge base for RAG
        try:
            from superoptix.cli.commands.embedded_knowledge_access import (
                EmbeddedKnowledgeAccess,
            )

            self.knowledge_base = EmbeddedKnowledgeAccess()
        except:
            self.knowledge_base = None

        # Initialize components with knowledge base
        self.intent_parser = IntentParser(
            lm=self.lm, knowledge_base=self.knowledge_base
        )
        self.command_generator = CommandGenerator(lm=self.lm)
        self.response_formatter = ResponseFormatter(console=console, lm=self.lm)

    def _initialize_lm(self, config: dict) -> Optional[Any]:
        """Initialize DSPy language model from config."""
        try:
            import dspy

            provider = config.get("provider", "mock")
            model = config.get("model", "mock")

            if provider == "ollama":
                api_base = config.get("api_base", "http://localhost:11434")

                # Create LM instance
                lm = dspy.LM(f"ollama/{model}", api_base=api_base)

                # DON'T configure DSPy globally - it interferes with agent execution!
                # Each module should configure its own LM locally
                # dspy.configure(lm=lm)  # ← REMOVED

                return lm

            elif provider == "openai":
                api_key = config.get("api_key")
                if api_key:
                    lm = dspy.LM(model, api_key=api_key)
                    return lm

            elif provider == "anthropic":
                api_key = config.get("api_key")
                if api_key:
                    lm = dspy.LM(model, api_key=api_key)
                    return lm

            return None

        except Exception as e:
            return None

    def reload_config(self):
        """Reload configuration and reinitialize LM.

        Called after model changes to pick up new settings.
        """
        from superoptix.cli.commands.conversational import load_config

        self.config = load_config()

        # Reinitialize LM
        old_lm = self.lm
        self.lm = self._initialize_lm(self.config)

        # Update intent parser with new LM
        self.intent_parser.lm = self.lm
        # Don't configure DSPy globally - let agents use their own models

        return self.lm is not None

    def process(self, user_input: str):
        """Process user's natural language input.

        Args:
                user_input: User's natural language command
        """
        from rich.text import Text
        from superoptix.cli.commands.thinking_animation import ThinkingAnimation

        # Create animation helper
        animator = ThinkingAnimation(self.console)

        # Show progressive status
        self.console.print()

        # Step 1: Parse intent with thinking animation
        animator.thinking()
        conversation_history = self.context.get_history_summary()
        intent = self.intent_parser.parse(user_input, conversation_history)
        animator.stop()

        # Show what we understood
        self.console.print(
            Text.assemble(
                ("  ✓ ", "green"),
                ("Understood: ", "dim"),
                (f"{intent.action}", "cyan"),
                (" ", ""),
                (f"({intent.target or 'context-aware'})", "dim yellow"),
            )
        )

        # Step 2: Generate commands with preparing animation
        animator.preparing()
        project_context = self.context.get_project_state()
        commands = self.command_generator.generate(intent, project_context)
        animator.stop()

        # Show generated commands
        if commands:
            self.console.print(
                Text.assemble(
                    ("  ✓ ", "green"),
                    ("Generated ", "dim"),
                    (f"{len(commands)} command(s)", "cyan"),
                )
            )

        self.console.print()

        # Step 3: Execute commands with progress
        results = self._execute_commands(commands)

        # Step 4: Format response with typing effect
        self.response_formatter.format(intent, commands, results)

        # Step 5: Update context
        self.context.add_interaction(user_input, intent, commands, results)

    def _execute_commands(self, commands: List[str]) -> List[Dict[str, Any]]:
        """Execute CLI commands with loading animation.

        Args:
                commands: List of command strings to execute

        Returns:
                List of result dictionaries
        """

        results = []

        for cmd in commands:
            # Handle slash commands (don't execute as shell)
            if cmd.startswith("/"):
                results.append(
                    {
                        "command": cmd,
                        "stdout": "",
                        "stderr": "",
                        "returncode": 0,
                        "is_slash_command": True,
                    }
                )
                continue

            try:
                from superoptix.cli.commands.thinking_animation import ThinkingAnimation
                import os

                # Show what we're executing with animation
                animator = ThinkingAnimation(self.console)
                animator.executing(cmd)

                # Execute via subprocess with warning suppression
                env = os.environ.copy()
                env["PYTHONWARNINGS"] = "ignore"

                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=str(Path.cwd()),
                    env=env,
                )

                # Filter out warning messages from stderr
                stderr_lines = result.stderr.split("\n") if result.stderr else []
                filtered_stderr = []

                for line in stderr_lines:
                    # Skip pydantic and litellm warnings
                    if any(
                        skip in line
                        for skip in [
                            "PydanticDeprecatedSince20",
                            "DeprecationWarning",
                            "ResourceWarning",
                            "pydantic/_internal/",
                            "litellm/llms/",
                            "@validator",
                            "@field_validator",
                        ]
                    ):
                        continue

                    # Keep actual errors
                    if line.strip():
                        filtered_stderr.append(line)

                final_stderr = "\n".join(filtered_stderr).strip()

                # Respect the actual return code from the command
                results.append(
                    {
                        "command": cmd,
                        "stdout": result.stdout,
                        "stderr": final_stderr,
                        "returncode": result.returncode,
                    }
                )

            except Exception as e:
                results.append(
                    {"command": cmd, "stdout": "", "stderr": str(e), "returncode": 1}
                )

        return results
