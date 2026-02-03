"""Interactive debugger for SuperOptiX agent execution."""

import json
import pprint
from datetime import datetime
from typing import Any, Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

from .tracer import SuperOptixTracer


class InteractiveDebugger:
    """Interactive debugger with breakpoints and step-by-step execution."""

    def __init__(self, tracer: SuperOptixTracer, memory_system=None):
        self.tracer = tracer
        self.memory = memory_system
        self.console = Console()

        # Debugging state
        self.breakpoints = set()
        self.step_mode = False
        self.break_on_error = True
        self.break_on_memory_ops = False

        # Execution context
        self.current_context = {}
        self.execution_stack = []

        # Command handlers
        self.commands = {
            "c": self._cmd_continue,
            "continue": self._cmd_continue,
            "s": self._cmd_step,
            "step": self._cmd_step,
            "n": self._cmd_next,
            "next": self._cmd_next,
            "b": self._cmd_breakpoint,
            "breakpoint": self._cmd_breakpoint,
            "l": self._cmd_list_breakpoints,
            "list": self._cmd_list_breakpoints,
            "i": self._cmd_inspect,
            "inspect": self._cmd_inspect,
            "m": self._cmd_memory,
            "memory": self._cmd_memory,
            "t": self._cmd_trace,
            "trace": self._cmd_trace,
            "bt": self._cmd_backtrace,
            "backtrace": self._cmd_backtrace,
            "p": self._cmd_print,
            "print": self._cmd_print,
            "h": self._cmd_help,
            "help": self._cmd_help,
            "q": self._cmd_quit,
            "quit": self._cmd_quit,
            "export": self._cmd_export,
            "stats": self._cmd_stats,
        }

    def enable_step_mode(self):
        """Enable step-by-step execution mode."""
        self.step_mode = True
        self.console.print(
            "🐛 [bold yellow]Step mode enabled[/] - execution will pause at each operation"
        )

    def disable_step_mode(self):
        """Disable step-by-step execution mode."""
        self.step_mode = False
        self.console.print(
            "✅ [bold green]Step mode disabled[/] - normal execution resumed"
        )

    def add_breakpoint(self, component: str, operation: str = None):
        """Add a breakpoint for a specific component or operation."""
        bp_key = f"{component}:{operation}" if operation else component
        self.breakpoints.add(bp_key)
        self.console.print(f"🔴 [bold red]Breakpoint added:[/] {bp_key}")

    def remove_breakpoint(self, component: str, operation: str = None):
        """Remove a breakpoint."""
        bp_key = f"{component}:{operation}" if operation else component
        if bp_key in self.breakpoints:
            self.breakpoints.remove(bp_key)
            self.console.print(f"✅ [bold green]Breakpoint removed:[/] {bp_key}")
        else:
            self.console.print(f"⚠️  [yellow]Breakpoint not found:[/] {bp_key}")

    def should_break(
        self, component: str, operation: str = None, event_type: str = None
    ) -> bool:
        """Check if execution should break at this point."""
        if self.step_mode:
            return True

        # Check component-specific breakpoints
        if component in self.breakpoints:
            return True

        # Check operation-specific breakpoints
        if operation and f"{component}:{operation}" in self.breakpoints:
            return True

        # Break on errors if enabled
        if self.break_on_error and event_type and "error" in event_type:
            return True

        # Break on memory operations if enabled
        if self.break_on_memory_ops and component == "memory_system":
            return True

        return False

    def debug_breakpoint(
        self,
        breakpoint_name: str,
        context: Dict[str, Any] = None,
        component: str = "unknown",
        operation: str = None,
    ):
        """Interactive debugging breakpoint with full inspection capabilities."""
        if not self.should_break(component, operation):
            return

        # Update current context
        self.current_context = context or {}
        self.execution_stack.append(
            {
                "breakpoint": breakpoint_name,
                "component": component,
                "operation": operation,
                "timestamp": datetime.now(),
                "context": context,
            }
        )

        # Display breakpoint information
        self._display_breakpoint_info(breakpoint_name, component, operation, context)

        # Interactive command loop
        while True:
            try:
                cmd_input = self.console.input("\n🐛 [bold blue]Debug>[/] ").strip()
                if not cmd_input:
                    continue

                # Parse command and arguments
                parts = cmd_input.split()
                cmd = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []

                if cmd in self.commands:
                    result = self.commands[cmd](args)
                    if result == "continue":
                        break
                    elif result == "quit":
                        raise KeyboardInterrupt("Debug session terminated")
                else:
                    self.console.print(f"❌ [red]Unknown command:[/] {cmd}")
                    self._cmd_help([])

            except KeyboardInterrupt:
                self.console.print("\n🛑 [bold red]Debug session interrupted[/]")
                raise
            except EOFError:
                break

        # Pop from execution stack
        if self.execution_stack:
            self.execution_stack.pop()

    def _display_breakpoint_info(
        self, name: str, component: str, operation: str, context: Dict
    ):
        """Display comprehensive breakpoint information."""
        # Main breakpoint panel
        info_text = f"[bold yellow]Component:[/] {component}\n"
        if operation:
            info_text += f"[bold yellow]Operation:[/] {operation}\n"
        info_text += f"[bold yellow]Time:[/] {datetime.now().strftime('%H:%M:%S')}"

        self.console.print(
            Panel(info_text, title=f"🔍 Breakpoint: {name}", border_style="red")
        )

        # Context information
        if context:
            self._display_context_summary(context)

        # Quick stats
        trace_summary = self.tracer.get_trace_summary()
        self.console.print(
            f"📊 [dim]Traces: {trace_summary['total_events']} | "
            f"Errors: {trace_summary['error_events']} | "
            f"Avg Duration: {trace_summary['average_duration_ms']:.1f}ms[/]"
        )

    def _display_context_summary(self, context: Dict):
        """Display a summary of the current context."""
        table = Table(title="Context Summary", show_header=True)
        table.add_column("Key", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Value", style="white")

        for key, value in context.items():
            value_str = str(value)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."
            table.add_row(key, type(value).__name__, value_str)

        self.console.print(table)

    # Command implementations
    def _cmd_continue(self, args: List[str]) -> str:
        """Continue execution."""
        self.console.print("▶️  [green]Continuing execution...[/]")
        return "continue"

    def _cmd_step(self, args: List[str]) -> str:
        """Enable step mode and continue."""
        self.enable_step_mode()
        return "continue"

    def _cmd_next(self, args: List[str]) -> str:
        """Continue to next operation (same as continue for now)."""
        return self._cmd_continue(args)

    def _cmd_breakpoint(self, args: List[str]) -> str:
        """Add or remove breakpoints."""
        if not args:
            self.console.print(
                "Usage: breakpoint <component> [operation] | breakpoint remove <component> [operation]"
            )
            return ""

        if args[0] == "remove" and len(args) > 1:
            component = args[1]
            operation = args[2] if len(args) > 2 else None
            self.remove_breakpoint(component, operation)
        else:
            component = args[0]
            operation = args[1] if len(args) > 1 else None
            self.add_breakpoint(component, operation)

        return ""

    def _cmd_list_breakpoints(self, args: List[str]) -> str:
        """List all active breakpoints."""
        if not self.breakpoints:
            self.console.print("No active breakpoints")
        else:
            self.console.print("🔴 [bold red]Active Breakpoints:[/]")
            for bp in sorted(self.breakpoints):
                self.console.print(f"  • {bp}")
        return ""

    def _cmd_inspect(self, args: List[str]) -> str:
        """Inspect current context or specific variables."""
        if not args:
            # Show full context
            if self.current_context:
                syntax = Syntax(
                    json.dumps(self.current_context, indent=2, default=str),
                    "json",
                    theme="monokai",
                    line_numbers=True,
                )
                self.console.print(Panel(syntax, title="Current Context"))
            else:
                self.console.print("No context available")
        else:
            # Show specific variable
            var_name = args[0]
            if var_name in self.current_context:
                value = self.current_context[var_name]
                self.console.print(f"[bold cyan]{var_name}:[/] {pprint.pformat(value)}")
            else:
                self.console.print(f"❌ Variable '{var_name}' not found in context")

        return ""

    def _cmd_memory(self, args: List[str]) -> str:
        """Inspect memory system state."""
        if not self.memory:
            self.console.print("❌ Memory system not available")
            return ""

        try:
            summary = self.memory.get_memory_summary()

            # Memory overview table
            table = Table(title="Memory System State", show_header=True)
            table.add_column("Component", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Details", style="white")

            table.add_row(
                "Short-term Memory",
                "Active",
                f"Size: {summary['short_term_memory']['size']}",
            )
            table.add_row(
                "Long-term Memory",
                "Active",
                f"Items: {summary['long_term_memory']['total_items']}",
            )
            table.add_row(
                "Episodic Memory",
                "Active",
                f"Episodes: {summary['episodic_memory']['active_episodes']}",
            )
            table.add_row(
                "Interactions", "Tracked", f"Count: {summary['interaction_count']}"
            )

            self.console.print(table)

            # Recent memories if requested
            if args and args[0] == "recent":
                recent_memories = self.memory.recall("", limit=5)
                if recent_memories:
                    self.console.print("\n[bold yellow]Recent Memories:[/]")
                    for i, mem in enumerate(recent_memories, 1):
                        content = (
                            mem["content"][:100] + "..."
                            if len(mem["content"]) > 100
                            else mem["content"]
                        )
                        self.console.print(f"  {i}. {content}")

        except Exception as e:
            self.console.print(f"❌ Error accessing memory: {e}")

        return ""

    def _cmd_trace(self, args: List[str]) -> str:
        """Show trace information."""
        if not args:
            # Show trace summary
            summary = self.tracer.get_trace_summary()

            table = Table(title="Trace Summary", show_header=True)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Total Events", str(summary["total_events"]))
            table.add_row("Error Events", str(summary["error_events"]))
            table.add_row("Error Rate", f"{summary['error_rate']:.2%}")
            table.add_row("Avg Duration", f"{summary['average_duration_ms']:.2f}ms")
            table.add_row("Components", ", ".join(summary["components_traced"]))

            self.console.print(table)

        elif args[0] == "errors":
            # Show error traces
            error_traces = self.tracer.get_error_traces()
            if error_traces:
                self.console.print(f"[bold red]Error Traces ({len(error_traces)}):[/]")
                for trace in error_traces[-5:]:  # Last 5 errors
                    self.console.print(
                        f"  🔴 {trace.timestamp.strftime('%H:%M:%S')} - "
                        f"{trace.component}: {trace.data.get('error', 'Unknown error')}"
                    )
            else:
                self.console.print("✅ No error traces found")

        elif args[0] == "tree":
            # Show trace tree
            self._display_trace_tree()

        return ""

    def _display_trace_tree(self):
        """Display traces as a hierarchical tree."""
        trace_tree = self.tracer.get_trace_tree()

        tree = Tree("🌳 Trace Tree")

        def add_to_tree(parent_node, traces):
            for trace_item in traces:
                event = trace_item["event"]
                label = f"{event['component']}: {event['event_type']}"
                if event.get("duration_ms"):
                    label += f" ({event['duration_ms']:.1f}ms)"

                node = parent_node.add(label)
                if trace_item["children"]:
                    add_to_tree(node, trace_item["children"])

        add_to_tree(tree, trace_tree["root_traces"])
        self.console.print(tree)

    def _cmd_backtrace(self, args: List[str]) -> str:
        """Show execution stack backtrace."""
        if not self.execution_stack:
            self.console.print("No execution stack available")
        else:
            self.console.print("[bold yellow]Execution Stack:[/]")
            for i, frame in enumerate(reversed(self.execution_stack)):
                self.console.print(
                    f"  {i}: {frame['component']} - {frame['breakpoint']} "
                    f"({frame['timestamp'].strftime('%H:%M:%S')})"
                )
        return ""

    def _cmd_print(self, args: List[str]) -> str:
        """Print variable or expression."""
        if not args:
            self.console.print("Usage: print <variable_name>")
            return ""

        var_name = args[0]
        if var_name in self.current_context:
            self.console.print(
                f"{var_name} = {pprint.pformat(self.current_context[var_name])}"
            )
        else:
            self.console.print(f"❌ Variable '{var_name}' not found")

        return ""

    def _cmd_help(self, args: List[str]) -> str:
        """Show available commands."""
        help_text = """
[bold yellow]Available Debug Commands:[/]

[cyan]Execution Control:[/]
  c, continue     - Continue execution
  s, step         - Enable step mode and continue
  n, next         - Continue to next operation
  q, quit         - Quit debug session

[cyan]Breakpoints:[/]
  b, breakpoint <component> [operation] - Add breakpoint
  breakpoint remove <component>         - Remove breakpoint
  l, list                              - List breakpoints

[cyan]Inspection:[/]
  i, inspect [var]  - Inspect context or specific variable
  m, memory [recent] - Show memory system state
  t, trace [errors|tree] - Show trace information
  bt, backtrace     - Show execution stack
  p, print <var>    - Print variable value

[cyan]Utilities:[/]
  export [format]   - Export traces
  stats            - Show performance statistics
  h, help          - Show this help
        """
        self.console.print(help_text)
        return ""

    def _cmd_quit(self, args: List[str]) -> str:
        """Quit the debug session."""
        self.console.print("👋 [bold yellow]Quitting debug session[/]")
        return "quit"

    def _cmd_export(self, args: List[str]) -> str:
        """Export traces or debug information."""
        format_type = args[0] if args else "json"
        filename = (
            f"debug_traces_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
        )

        try:
            self.tracer.export_traces(format_type, filename)
            self.console.print(f"✅ Traces exported to {filename}")
        except Exception as e:
            self.console.print(f"❌ Export failed: {e}")

        return ""

    def _cmd_stats(self, args: List[str]) -> str:
        """Show detailed performance statistics."""
        summary = self.tracer.get_trace_summary()
        perf_stats = summary["performance_stats"]

        # Overall stats
        table = Table(title="Performance Statistics", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Total Operations", str(perf_stats["total_operations"]))
        table.add_row("Total Errors", str(perf_stats["total_errors"]))
        table.add_row(
            "Error Rate",
            f"{perf_stats['total_errors'] / perf_stats['total_operations'] * 100:.2f}%"
            if perf_stats["total_operations"] > 0
            else "0%",
        )
        table.add_row("Average Duration", f"{perf_stats['average_duration']:.2f}ms")

        self.console.print(table)

        # Component-specific stats
        if perf_stats["component_stats"]:
            comp_table = Table(title="Component Statistics", show_header=True)
            comp_table.add_column("Component", style="cyan")
            comp_table.add_column("Operations", style="white")
            comp_table.add_column("Errors", style="red")
            comp_table.add_column("Avg Duration", style="green")

            for comp, stats in perf_stats["component_stats"].items():
                comp_table.add_row(
                    comp,
                    str(stats["operations"]),
                    str(stats["errors"]),
                    f"{stats['avg_duration']:.2f}ms",
                )

            self.console.print(comp_table)

        return ""
