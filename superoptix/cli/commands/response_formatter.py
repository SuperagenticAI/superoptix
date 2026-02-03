"""Response formatter for conversational responses.

Formats CLI command results into natural, conversational responses.
"""

import warnings
from typing import List, Dict, Any

warnings.filterwarnings("ignore")

import dspy
from rich.panel import Panel
from rich.text import Text
from rich.console import Console


class ResponseGeneration(dspy.Signature):
    """Generate conversational response from command results.

    Transform technical CLI output into friendly, helpful responses.
    """

    user_input: str = dspy.InputField(desc="Original user query")
    command_executed: str = dspy.InputField(desc="CLI command that was executed")
    command_output: str = dspy.InputField(desc="Output from the CLI command")
    command_success: bool = dspy.InputField(desc="Whether command succeeded")

    response: str = dspy.OutputField(desc="Friendly conversational response")
    next_suggestions: str = dspy.OutputField(desc="Suggested next steps for the user")


class ResponseFormatter:
    """Format command results into conversational responses."""

    def __init__(self, console: Console, lm=None):
        """Initialize response formatter.

        Args:
                console: Rich console for output
                lm: DSPy language model (optional)
        """
        self.console = console

        # Don't configure globally - store LM locally
        self.lm = lm
        if lm:
            self.formatter = dspy.ChainOfThought(ResponseGeneration)
        else:
            self.formatter = None

    def format(
        self, intent, commands: List[str], results: List[Dict[str, Any]]
    ) -> None:
        """Format and display results.

        Args:
                intent: Original intent
                commands: Commands that were executed
                results: Results from command execution
        """
        # Use rule-based formatting (DSPy optional for complex cases)
        self._rule_based_format(intent, commands, results)

    def _rule_based_format(
        self, intent, commands: List[str], results: List[Dict[str, Any]]
    ):
        """Format results using rule-based approach."""

        if not results:
            self.console.print()
            self.console.print(
                Panel(
                    "[yellow]❓ I'm not sure how to do that yet.[/yellow]\n\n"
                    "[dim]Try:[/dim]\n"
                    "• [cyan]/help[/cyan] - Show all commands\n"
                    "• [cyan]/ask <question>[/cyan] - Ask about SuperOptiX\n"
                    "• Or use traditional CLI: [cyan]super agent compile <name>[/cyan]",
                    border_style="yellow",
                    title="[bold yellow]⚠️  Not Understood[/bold yellow]",
                )
            )
            self.console.print()
            return

        # Process each result
        for i, result in enumerate(results):
            cmd = result.get("command", "")
            stdout = result.get("stdout", "")
            stderr = result.get("stderr", "")
            returncode = result.get("returncode", 1)

            if returncode == 0:
                # Success
                self._format_success(intent, cmd, stdout)
            else:
                # Error
                self._format_error(intent, cmd, stderr)

    def _format_success(self, intent, command: str, output: str):
        """Format successful command result."""
        action = intent.action
        target = intent.target or "agent"

        # Show command output if it has useful info
        if output and len(output.strip()) > 10:
            self.console.print()
            self.console.print("[dim]" + "─" * 60 + "[/dim]")
            self.console.print(output.strip())
            self.console.print("[dim]" + "─" * 60 + "[/dim]")

        self.console.print()

        # Action-specific messages
        if action == "build" or action == "create":
            message = Text.assemble(
                ("✅ ", "green"),
                ("Created agent: ", "cyan"),
                (f"{target}", "bold yellow"),
                ("\n\n", ""),
                ("Your agent playbook is ready!\n\n", "green"),
                ("Next steps:\n", "bold cyan"),
                ("• ", "dim"),
                ("Compile the agent to create executable pipeline\n", "cyan"),
                ("• ", "dim"),
                ("Evaluate to test performance\n", "cyan"),
                ("• ", "dim"),
                ("Optimize with GEPA for better results", "cyan"),
            )

            panel = Panel(
                message,
                border_style="green",
                title="[bold green]🎉 Agent Created![/bold green]",
                padding=(1, 2),
            )
            self.console.print(panel)

        elif action == "compile":
            message = Text.assemble(
                ("✅ ", "green"),
                ("Compiled: ", "cyan"),
                (f"{target}", "bold yellow"),
                ("\n\n", ""),
                ("Pipeline generated successfully!\n\n", "green"),
                ("Next steps:\n", "bold cyan"),
                ("• ", "dim"),
                ("Evaluate to test the agent's performance\n", "cyan"),
                ("• ", "dim"),
                ("Optimize with GEPA for better results\n", "cyan"),
                ("• ", "dim"),
                ("Run the agent with your specific goals", "cyan"),
            )

            panel = Panel(
                message,
                border_style="green",
                title="[bold green]⚡ Compilation Complete![/bold green]",
                padding=(1, 2),
            )
            self.console.print(panel)

        elif action == "optimize":
            message = Text.assemble(
                ("✅ ", "green"),
                ("Optimized: ", "cyan"),
                (f"{target}", "bold yellow"),
                ("\n\n", ""),
                ("GEPA optimization complete!\n\n", "green"),
                ("Next: ", "bold cyan"),
                ("Evaluate the agent to see improvements", "cyan"),
            )

            panel = Panel(
                message,
                border_style="green",
                title="[bold green]🎯 Optimization Complete![/bold green]",
                padding=(1, 2),
            )
            self.console.print(panel)

        elif action == "evaluate" or action == "test":
            message = Text.assemble(
                ("✅ ", "green"),
                ("Evaluation complete: ", "cyan"),
                (f"{target}", "bold yellow"),
                ("\n\n", ""),
                (output[:200] if output else "Check the results above!", "dim"),
            )

            panel = Panel(
                message,
                border_style="green",
                title="[bold green]📊 Evaluation Results[/bold green]",
                padding=(1, 2),
            )
            self.console.print(panel)

        elif action == "run":
            message = Text.assemble(
                ("✅ ", "green"),
                ("Executed: ", "cyan"),
                (f"{target}", "bold yellow"),
                ("\n\n", ""),
                ("Agent run complete!\n", "green"),
                ("Check the output above for results.", "dim"),
            )

            panel = Panel(
                message,
                border_style="green",
                title="[bold green]🚀 Execution Complete![/bold green]",
                padding=(1, 2),
            )
            self.console.print(panel)

        else:
            # Generic success
            self.console.print(
                Panel(
                    f"[green]✅ Command executed successfully![/green]\n\n"
                    f"[dim]Command:[/dim] [cyan]{command}[/cyan]",
                    border_style="green",
                    title="[bold green]✅ Success[/bold green]",
                )
            )

        self.console.print()

    def _format_error(self, intent, command: str, error: str):
        """Format error result."""
        self.console.print()

        # Check for common errors and provide better messages
        if "not in a SuperOptiX project" in error or "No .super file found" in error:
            error_panel = Panel(
                f"[yellow]⚠️  Not in a SuperOptiX project[/yellow]\n\n"
                f"[dim]You need to be in a SuperOptiX project directory.[/dim]\n\n"
                f"[bold cyan]Quick fix:[/bold cyan]\n"
                f"1. Exit: [cyan]/exit[/cyan]\n"
                f"2. Initialize project: [cyan]super init my_project[/cyan]\n"
                f"3. Enter project: [cyan]cd my_project[/cyan]\n"
                f"4. Run [cyan]super[/cyan] again\n\n"
                f"[dim]Or continue using slash commands for help:[/dim]\n"
                f"• [cyan]/ask <question>[/cyan] - Ask about SuperOptiX\n"
                f"• [cyan]/help[/cyan] - Show commands",
                border_style="yellow",
                title="[bold yellow]📁 Project Required[/bold yellow]",
                padding=(1, 2),
            )

        elif (
            "Model configuration missing" in error
            or "Specification execution failed" in error
        ):
            # Model config mismatch - need to recompile
            target = intent.target or "agent"
            error_panel = Panel(
                f"[yellow]⚠️  Agent needs to be recompiled[/yellow]\n\n"
                f"[dim]The agent was compiled with a different model configuration.[/dim]\n\n"
                f"[bold cyan]Quick fix:[/bold cyan]\n"
                f"1. Recompile: [cyan]super agent compile {target}[/cyan]\n"
                f"2. Then evaluate: [cyan]super agent evaluate {target}[/cyan]\n\n"
                f"[dim]Or in natural language:[/dim]\n"
                f"• Type: [cyan]compile {target}[/cyan]\n"
                f"• Then: [cyan]evaluate {target}[/cyan]",
                border_style="yellow",
                title="[bold yellow]🔧 Recompilation Needed[/bold yellow]",
                padding=(1, 2),
            )

        elif not error or len(error.strip()) == 0:
            # Command succeeded despite returncode (probably just warnings)
            self._format_success(intent, command, "")
            return

        else:
            # Generic error
            error_panel = Panel(
                f"[red]❌ Command failed[/red]\n\n"
                f"[dim]Command:[/dim] [cyan]{command}[/cyan]\n\n"
                f"[dim]Error:[/dim]\n[red]{error[:300] if error else 'Unknown error'}[/red]\n\n"
                f"[dim]Try:[/dim]\n"
                f"• [cyan]/help[/cyan] - Get help\n"
                f"• [cyan]/ask <question>[/cyan] - Ask about SuperOptiX\n"
                f"• [cyan]/status[/cyan] - Check project status",
                border_style="red",
                title="[bold red]❌ Error[/bold red]",
                padding=(1, 2),
            )

        self.console.print(error_panel)
        self.console.print()
