"""CLI commands for SuperOptiX observability and monitoring."""

import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()


def dashboard(args):
    """Launch the SuperOptiX observability dashboard."""
    agent_id = getattr(args, "agent_id", None)
    port = getattr(args, "port", 8501)
    host = getattr(args, "host", "localhost")
    auto_open = getattr(args, "auto_open", False)
    use_fastapi = getattr(args, "fastapi", False)  # NEW: Option for FastAPI dashboard

    # Check for available traces
    from superoptix.observability import SuperOptixTracer

    # Try enhanced dashboard first if requested
    if use_fastapi:
        try:
            from superoptix.observability.simple_dashboard import start_dashboard

            console.print("🚀 [green]Starting enhanced FastAPI dashboard...[/]")
            console.print(f"📊 Dashboard will be available at: http://{host}:{port}")
            start_dashboard(host=host, port=port)
            return
        except ImportError:
            console.print(
                "⚠️  [yellow]FastAPI dashboard not available, using Streamlit[/]"
            )

    available_agents = SuperOptixTracer.get_all_available_agents()

    if not available_agents:
        console.print("ℹ️  [yellow]No trace files found in the project[/]")
        console.print(
            "[dim]Run some agents first to generate traces, then launch the dashboard[/]"
        )
        return

    console.print(
        Panel(
            f"🔍 [bold blue]SuperOptiX Observability Dashboard[/]\n\n"
            f"[cyan]Host:[/] {host}\n"
            f"[cyan]Port:[/] {port}\n"
            f"[cyan]Agent ID:[/] {agent_id or 'Multi-Agent Mode'}\n"
            f"[cyan]Auto-open:[/] {'Yes' if auto_open else 'No'}\n"
            f"[cyan]Available Agents:[/] {', '.join(available_agents)}",
            title="Dashboard Configuration",
            border_style="blue",
        )
    )

    # Use multi-agent dashboard if no specific agent_id provided
    if agent_id:
        dashboard_script = _create_dashboard_script(agent_id)
    else:
        dashboard_script = _create_multi_agent_dashboard_script()

    script_path = Path("/tmp/superoptix_dashboard.py")
    script_path.write_text(dashboard_script)

    try:
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(script_path),
            "--server.port",
            str(port),
            "--server.address",
            host,
            "--server.headless",
            "true" if not auto_open else "false",
        ]

        console.print("🚀 [green]Starting dashboard...[/]")
        console.print(f"📊 Dashboard will be available at: http://{host}:{port}")

        if auto_open:
            console.print("🌐 Opening browser automatically...")

        if not agent_id:
            console.print(
                "🎭 [cyan]Multi-Agent Mode:[/] All agents will be discoverable in the dashboard"
            )

        subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError as e:
        console.print(f"❌ [red]Failed to start dashboard:[/] {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n🛑 [yellow]Dashboard stopped by user[/]")
    finally:
        if script_path.exists():
            script_path.unlink()


def debug(args):
    """Start interactive debugging session for an agent."""
    agent_id = getattr(args, "agent_id", None)
    enable_step_mode = getattr(args, "enable_step_mode", False)
    break_on_error = getattr(args, "break_on_error", False)
    break_on_memory = getattr(args, "break_on_memory", False)

    console.print(
        Panel(
            f"🐛 [bold red]Interactive Debug Mode[/]\n\n"
            f"[cyan]Agent ID:[/] {agent_id}\n"
            f"[cyan]Step Mode:[/] {'Enabled' if enable_step_mode else 'Disabled'}\n"
            f"[cyan]Break on Error:[/] {'Enabled' if break_on_error else 'Disabled'}\n"
            f"[cyan]Break on Memory:[/] {'Enabled' if break_on_memory else 'Disabled'}",
            title="Debug Configuration",
            border_style="red",
        )
    )

    try:
        from superoptix.memory import AgentMemory
        from superoptix.observability import InteractiveDebugger, SuperOptixTracer

        tracer = SuperOptixTracer(agent_id)
        memory = AgentMemory(agent_id=agent_id)
        debugger = InteractiveDebugger(tracer, memory)

        if enable_step_mode:
            debugger.enable_step_mode()

        debugger.break_on_error = break_on_error
        debugger.break_on_memory_ops = break_on_memory

        console.print(
            "🔍 [green]Debug session started. Use 'help' for available commands.[/]"
        )
        console.print(
            "💡 [dim]Tip: Set breakpoints with 'breakpoint <component>' before running your agent.[/]"
        )

        debugger.debug_breakpoint(
            "debug_session_start",
            {
                "session_type": "manual",
                "agent_id": agent_id,
                "configuration": {
                    "step_mode": enable_step_mode,
                    "break_on_error": break_on_error,
                    "break_on_memory": break_on_memory,
                },
            },
        )

    except KeyboardInterrupt:
        console.print("\n🛑 [yellow]Debug session ended[/]")
    except Exception as e:
        console.print(f"❌ [red]Debug session failed:[/] {e}")
        sys.exit(1)


def traces(args):
    """View and export agent execution traces."""
    agent_id = getattr(args, "agent_id", None)
    component = getattr(args, "component", None)
    status = getattr(args, "status", None)
    limit = getattr(args, "limit", 100)
    export = getattr(args, "export", None)
    output = getattr(args, "output", None)
    detailed = getattr(args, "detailed", False)
    show_tools = getattr(args, "show_tools", False)
    show_llm = getattr(args, "show_llm", False)

    try:
        from superoptix.observability import SuperOptixTracer

        console.print(f"🔍 [blue]Loading traces for agent:[/] {agent_id}")
        tracer = SuperOptixTracer(agent_id, auto_load=True)
        loaded_count = len(tracer.traces)

        if loaded_count == 0:
            # Show available agents if no traces found
            available_agents = SuperOptixTracer.get_all_available_agents()
            if available_agents:
                console.print(f"ℹ️  [yellow]No traces found for agent '{agent_id}'[/]")
                console.print(
                    f"[cyan]Available agents:[/] {', '.join(available_agents)}"
                )
            else:
                console.print("ℹ️  [yellow]No trace files found in the project[/]")
            return

        console.print(f"✅ [green]Loaded {loaded_count} trace events[/]")

        all_traces = tracer.traces

        if component:
            all_traces = [t for t in all_traces if t.component == component]

        if status:
            all_traces = [t for t in all_traces if t.status == status]

        filtered_traces = all_traces[-limit:]

        if not filtered_traces:
            console.print("ℹ️  [yellow]No traces found matching the criteria[/]")
            console.print(
                f"[dim]Filters applied: component={component}, status={status}[/]"
            )
            return

        if export:
            if export == "json":
                import json

                trace_data = [t.to_dict() for t in filtered_traces]
                output_content = json.dumps(trace_data, indent=2, default=str)
            else:  # csv
                import pandas as pd

                df = pd.DataFrame([t.to_dict() for t in filtered_traces])
                output_content = df.to_csv(index=False)

            if output:
                Path(output).write_text(output_content)
                console.print(f"✅ [green]Traces exported to {output}[/]")
            else:
                console.print(output_content)
        elif detailed:
            # Show detailed trace analysis similar to trace_viewer.py
            _display_detailed_traces(filtered_traces, show_tools, show_llm)
        else:
            from rich.table import Table

            table = Table(title=f"Traces for Agent: {agent_id}")
            table.add_column("Time", style="cyan")
            table.add_column("Component", style="magenta")
            table.add_column("Event", style="blue")
            table.add_column("Status", style="green")
            table.add_column("Duration", style="yellow")

            for trace in filtered_traces[-20:]:
                status_color = {
                    "success": "green",
                    "error": "red",
                    "warning": "yellow",
                    "info": "blue",
                }.get(trace.status, "white")
                duration_str = (
                    f"{trace.duration_ms:.1f}ms"
                    if trace.duration_ms is not None
                    else "-"
                )

                table.add_row(
                    trace.timestamp.strftime("%H:%M:%S"),
                    trace.component,
                    trace.event_type,
                    f"[{status_color}]{trace.status}[/]",
                    duration_str,
                )

            console.print(table)

            summary = tracer.get_trace_summary()
            console.print(
                f"\n📊 [dim]Total: {summary['total_events']} | Errors: {summary['error_events']} | Avg: {summary.get('average_duration_ms', 0):.1f}ms[/]"
            )

    except Exception as e:
        console.print(f"❌ [red]Failed to retrieve traces:[/] {e}")
        sys.exit(1)


def analyze(args):
    """Analyze agent performance and generate insights."""
    agent_id = getattr(args, "agent_id", None)
    days = getattr(args, "days", 7)

    console.print(
        Panel(
            f"📈 [bold blue]Performance Analysis[/]\n\n"
            f"[cyan]Agent ID:[/] {agent_id or 'All agents'}\n"
            f"[cyan]Time Period:[/] Last {days} days",
            title="Analysis Configuration",
            border_style="blue",
        )
    )

    try:
        from superoptix.observability import SuperOptixTracer

        if not agent_id:
            console.print("❌ [red]Agent ID is required for analysis[/]")
            available_agents = SuperOptixTracer.get_all_available_agents()
            if available_agents:
                console.print(
                    f"[cyan]Available agents:[/] {', '.join(available_agents)}"
                )
            sys.exit(1)

        console.print(f"🔍 [blue]Loading traces for agent:[/] {agent_id}")
        tracer = SuperOptixTracer(agent_id, auto_load=True)

        if len(tracer.traces) == 0:
            available_agents = SuperOptixTracer.get_all_available_agents()
            if available_agents:
                console.print(f"ℹ️  [yellow]No traces found for agent '{agent_id}'[/]")
                console.print(
                    f"[cyan]Available agents:[/] {', '.join(available_agents)}"
                )
            else:
                console.print("ℹ️  [yellow]No trace files found in the project[/]")
            return

        console.print(f"✅ [green]Loaded {len(tracer.traces)} trace events[/]")
        summary = tracer.get_trace_summary(days=days)

        console.print(f"\n📊 [bold]Performance Summary for Agent: {agent_id}[/]")

        from rich.table import Table

        summary_table = Table(show_header=False, box=None)
        summary_table.add_column(style="cyan")
        summary_table.add_column(style="white")

        summary_table.add_row("Total Events", str(summary["total_events"]))
        summary_table.add_row("Successful Events", str(summary["success_events"]))
        summary_table.add_row("Error Events", f"[red]{summary['error_events']}[/red]")
        summary_table.add_row(
            "Warning Events", f"[yellow]{summary['warning_events']}[/yellow]"
        )
        summary_table.add_row(
            "Average Duration", f"{summary.get('average_duration_ms', 0):.1f} ms"
        )
        summary_table.add_row(
            "Median Duration", f"{summary.get('median_duration_ms', 0):.1f} ms"
        )
        summary_table.add_row(
            "95th Percentile Duration", f"{summary.get('p95_duration_ms', 0):.1f} ms"
        )

        console.print(summary_table)

        if summary.get("most_common_errors"):
            error_table = Table(
                title="Top 5 Most Common Errors", title_style="bold red"
            )
            error_table.add_column("Error Type", style="red")
            error_table.add_column("Count", style="magenta")
            for error, count in summary["most_common_errors"]:
                error_table.add_row(error, str(count))
            console.print(error_table)

    except Exception as e:
        console.print(f"❌ [red]Failed to analyze performance:[/] {e}")
        import traceback

        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


def list_agents_with_traces(args):
    """List all agents that have trace files."""
    try:
        from superoptix.observability import SuperOptixTracer

        available_agents = SuperOptixTracer.get_all_available_agents()

        if not available_agents:
            console.print("ℹ️  [yellow]No trace files found in the project[/]")
            console.print("[dim]Run some agents first to generate traces[/dim]")
            return

        console.print("📋 [bold blue]Available Agents with Traces[/]\n")

        from rich.table import Table

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Agent ID", style="cyan")
        table.add_column("Trace Count", style="magenta")
        table.add_column("Last Activity", style="green")

        for agent_id in available_agents:
            tracer = SuperOptixTracer(agent_id, auto_load=True)
            trace_count = len(tracer.traces)

            # Get last activity
            if tracer.traces:
                last_trace = max(tracer.traces, key=lambda t: t.timestamp)
                last_activity = last_trace.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            else:
                last_activity = "Unknown"

            table.add_row(agent_id, str(trace_count), last_activity)

        console.print(table)
        console.print(
            "\n[dim]Use 'super observability traces <agent_id>' to view traces for a specific agent[/dim]"
        )

    except Exception as e:
        console.print(f"❌ [red]Failed to list agents:[/] {e}")
        sys.exit(1)


def check_traces(args):
    """Check pipeline tracing configuration and output (similar to check_pipeline_traces.py)."""
    agent_id = getattr(args, "agent_id", None)
    run_test = getattr(args, "run_test", False)
    check_dspy = getattr(args, "check_dspy", False)

    console.print(
        Panel(
            f"🔍 [bold blue]Pipeline Trace Analysis[/]\n\n"
            f"[cyan]Agent ID:[/] {agent_id or 'All agents'}\n"
            f"[cyan]Run Test:[/] {'Yes' if run_test else 'No'}\n"
            f"[cyan]Check DSPy:[/] {'Yes' if check_dspy else 'No'}",
            title="Trace Check Configuration",
            border_style="blue",
        )
    )

    try:
        # Check current directory structure for trace files
        console.print("📁 [blue]Checking for trace files...[/]")
        current_dir = Path(".")
        trace_files = []

        for pattern in ["*trace*", "*.jsonl", "*.log"]:
            trace_files.extend(list(current_dir.rglob(pattern)))

        if trace_files:
            console.print(
                f"✅ [green]Found {len(trace_files)} potential trace files:[/]"
            )
            for trace_file in trace_files:
                stat = trace_file.stat()
                console.print(f"   📄 {trace_file} ({stat.st_size} bytes)")
        else:
            console.print("ℹ️  [yellow]No trace files found in current directory[/]")

        # Check SuperOptiX trace directory
        superoptix_trace_dir = Path(".superoptix/traces")
        if superoptix_trace_dir.exists():
            console.print(
                f"✅ [green]SuperOptiX trace directory found: {superoptix_trace_dir}[/]"
            )
            trace_files = list(superoptix_trace_dir.glob("*.jsonl"))
            console.print(f"   📊 Found {len(trace_files)} trace files")
            for trace_file in trace_files:
                stat = trace_file.stat()
                console.print(f"   📄 {trace_file.name} ({stat.st_size} bytes)")
        else:
            console.print("ℹ️  [yellow]SuperOptiX trace directory not found[/]")

        # Run test if requested
        if run_test and agent_id:
            console.print(f"\n🏃 [blue]Running test with agent: {agent_id}[/]")
            try:
                result = subprocess.run(
                    ["super", "agent", "run", agent_id, "-i", "Test trace: 5*5"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.returncode == 0:
                    console.print("✅ [green]Test run completed successfully[/]")
                    # Check if new traces were generated
                    if superoptix_trace_dir.exists():
                        new_traces = list(
                            superoptix_trace_dir.glob(f"{agent_id}*.jsonl")
                        )
                        if new_traces:
                            console.print(
                                f"✅ [green]New traces generated: {len(new_traces)} files[/]"
                            )
                        else:
                            console.print("ℹ️  [yellow]No new traces detected[/]")
                else:
                    console.print(f"❌ [red]Test run failed: {result.stderr}[/]")

            except subprocess.TimeoutExpired:
                console.print("❌ [red]Test run timed out[/]")
            except Exception as e:
                console.print(f"❌ [red]Test run error: {e}[/]")

        # Check DSPy configuration if requested
        if check_dspy:
            console.print("\n🔬 [blue]Checking DSPy configuration...[/]")
            try:
                import dspy

                console.print("✅ [green]DSPy imported successfully[/]")
                console.print(f"📝 DSPy settings: {hasattr(dspy, 'settings')}")

                if hasattr(dspy, "settings") and hasattr(dspy.settings, "lm"):
                    console.print(f"🤖 LM configured: {dspy.settings.lm is not None}")

                # Check logging configuration
                import logging

                logger = logging.getLogger("dspy")
                console.print(f"📊 DSPy logger level: {logger.level}")
                console.print(f"📊 DSPy logger handlers: {len(logger.handlers)}")

            except Exception as e:
                console.print(f"❌ [red]Error checking DSPy: {e}[/]")

        # Show recommendations
        console.print("\n💡 [bold]RECOMMENDATIONS:[/]")
        console.print(
            "1. Run agents to generate traces: [cyan]super agent run <agent_id>[/]"
        )
        console.print("2. View traces: [cyan]super observability traces <agent_id>[/]")
        console.print("3. Launch dashboard: [cyan]super observability dashboard[/]")
        console.print("4. Debug issues: [cyan]super observability debug <agent_id>[/]")

    except Exception as e:
        console.print(f"❌ [red]Failed to check traces:[/] {e}")
        sys.exit(1)


def _display_detailed_traces(traces, show_tools=False, show_llm=False):
    """Display detailed trace analysis similar to trace_viewer.py functionality."""
    from rich.table import Table
    from rich.panel import Panel

    # Analyze traces
    stats = _analyze_traces(traces)

    # Display summary
    summary_panel = Panel(
        f"📊 [bold]TRACE ANALYSIS SUMMARY[/]\n\n"
        f"🔢 Total Events: {stats['total_events']}\n"
        f"⏱️  Average Duration: {stats.get('avg_duration', 0):.2f}ms\n"
        f"⚡ Max Duration: {stats.get('max_duration', 0):.2f}ms\n"
        f"🏃 Min Duration: {stats.get('min_duration', 0):.2f}ms\n"
        f"🔧 Tools Used: {len(stats['tools_used'])}\n"
        f"🤖 LLM Calls: {len(stats['llm_calls'])}\n"
        f"❌ Errors: {len(stats['errors'])}",
        title="📊 Trace Statistics",
        border_style="blue",
    )
    console.print(summary_panel)

    # Display recent events
    if traces:
        recent_table = Table(title=f"📋 Recent Events (Last {min(10, len(traces))})")
        recent_table.add_column("Time", style="cyan")
        recent_table.add_column("Component", style="magenta")
        recent_table.add_column("Event", style="blue")
        recent_table.add_column("Status", style="green")
        recent_table.add_column("Duration", style="yellow")

        for trace in traces[-10:]:
            status_color = {
                "success": "green",
                "error": "red",
                "warning": "yellow",
                "info": "blue",
            }.get(trace.status, "white")

            duration_str = f"{trace.duration_ms:.1f}ms" if trace.duration_ms else "-"

            recent_table.add_row(
                trace.timestamp.strftime("%H:%M:%S"),
                trace.component,
                trace.event_type,
                f"[{status_color}]{trace.status}[/]",
                duration_str,
            )

        console.print(recent_table)

    # Display tool executions if requested
    if show_tools and stats["tools_used"]:
        tools_table = Table(title="🔧 Tool Executions")
        tools_table.add_column("Time", style="cyan")
        tools_table.add_column("Tool", style="magenta")
        tools_table.add_column("Event", style="blue")
        tools_table.add_column("Status", style="green")
        tools_table.add_column("Duration", style="yellow")

        for trace in stats["tools_used"][-10:]:
            duration_str = f"{trace.duration_ms:.1f}ms" if trace.duration_ms else "-"
            tools_table.add_row(
                trace.timestamp.strftime("%H:%M:%S"),
                trace.component,
                trace.event_type,
                f"[green]{trace.status}[/]",
                duration_str,
            )

        console.print(tools_table)

    # Display LLM calls if requested
    if show_llm and stats["llm_calls"]:
        llm_table = Table(title="🤖 LLM Calls")
        llm_table.add_column("Time", style="cyan")
        llm_table.add_column("Component", style="magenta")
        llm_table.add_column("Event", style="blue")
        llm_table.add_column("Status", style="green")
        llm_table.add_column("Duration", style="yellow")

        for trace in stats["llm_calls"][-10:]:
            duration_str = f"{trace.duration_ms:.1f}ms" if trace.duration_ms else "-"
            llm_table.add_row(
                trace.timestamp.strftime("%H:%M:%S"),
                trace.component,
                trace.event_type,
                f"[green]{trace.status}[/]",
                duration_str,
            )

        console.print(llm_table)


def _analyze_traces(traces):
    """Analyze trace data for insights."""
    stats = {
        "total_events": len(traces),
        "event_types": {},
        "components": {},
        "durations": [],
        "errors": [],
        "tools_used": [],
        "llm_calls": [],
    }

    for trace in traces:
        # Count event types
        event_type = trace.event_type
        stats["event_types"][event_type] = stats["event_types"].get(event_type, 0) + 1

        # Count components
        component = trace.component
        stats["components"][component] = stats["components"].get(component, 0) + 1

        # Collect durations
        if trace.duration_ms:
            stats["durations"].append(trace.duration_ms)

        # Collect errors
        if trace.status == "error":
            stats["errors"].append(trace)

        # Identify tool calls
        if "tool" in component.lower() or any(
            keyword in event_type
            for keyword in ["calculate", "datetime", "analyze", "read_file"]
        ):
            stats["tools_used"].append(trace)

        # Identify potential LLM calls
        if (
            "llm" in component.lower()
            or "model" in event_type
            or "generation" in event_type
        ):
            stats["llm_calls"].append(trace)

    # Calculate duration statistics
    if stats["durations"]:
        stats["avg_duration"] = sum(stats["durations"]) / len(stats["durations"])
        stats["max_duration"] = max(stats["durations"])
        stats["min_duration"] = min(stats["durations"])

    return stats


def _create_dashboard_script(agent_id: str = None) -> str:
    """Create the Streamlit dashboard script."""
    return f"""
import streamlit as st
import sys
import os

# Add SuperOptiX to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
            from superoptix.observability import SuperOptixTracer, ObservabilityDashboard
        from superoptix.memory import AgentMemory

    # Initialize components
    agent_id = "{agent_id}" if "{agent_id}" else "demo_agent"

    # Create tracer and memory
            tracer = SuperOptixTracer(agent_id)

    try:
        memory = AgentMemory(agent_id=agent_id)
    except Exception:
        memory = None

    # Create and render dashboard
    dashboard = ObservabilityDashboard(tracer, memory)
    dashboard.render_dashboard()

except ImportError as e:
    st.error(f"Failed to import SuperOptiX components: {{e}}")
    st.info("Please ensure SuperOptiX is properly installed and configured.")
except Exception as e:
    st.error(f"Dashboard error: {{e}}")
    st.info("Check the console for detailed error information.")
"""


def _create_multi_agent_dashboard_script() -> str:
    """Create the Streamlit multi-agent dashboard script."""
    return """
import streamlit as st
import sys
import os
from pathlib import Path

# Add SuperOptiX to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from superoptix.observability.dashboard import MultiAgentObservabilityDashboard

    # Create and render multi-agent dashboard
    dashboard = MultiAgentObservabilityDashboard(project_root=Path.cwd())
    dashboard.render_dashboard()

except ImportError as e:
    st.error(f"Failed to import SuperOptiX components: {e}")
    st.info("Please ensure SuperOptiX is properly installed and configured.")
except Exception as e:
    st.error(f"Dashboard error: {e}")
    st.info("Check the console for detailed error information.")
    import traceback
    st.code(traceback.format_exc())
"""
