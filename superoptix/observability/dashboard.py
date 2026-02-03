"""Observability Dashboard for SuperOptiX using Streamlit."""

import json
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd
import plotly.express as px
import streamlit as st

from .tracer import SuperOptixTracer, TraceEvent


class MultiAgentObservabilityDashboard:
    """Multi-agent dashboard for SuperOptiX observability and monitoring."""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.agent_tracers = {}
        self.agent_memories = {}
        self._discover_agents()

    def _discover_agents(self):
        """Discover available agents from trace files and project structure."""
        agents = set()

        # Look for trace files in .superoptix/traces directory
        traces_dir = self.project_root / ".superoptix" / "traces"
        if traces_dir.exists():
            trace_files = traces_dir.glob("*.jsonl")
            for trace_file in trace_files:
                agent_id = trace_file.stem
                agents.add(agent_id)

        # Look for agent directories in project structure
        # Try both swe/swe/agents and direct agents patterns
        for agents_pattern in [
            "swe/swe/agents/*/playbook/*.yaml",
            "agents/*/playbook/*.yaml",
            "*/agents/*/playbook/*.yaml",
        ]:
            playbook_files = list(self.project_root.glob(agents_pattern))
            for playbook_file in playbook_files:
                # Extract agent name from path: .../agents/agent_name/playbook/...
                parts = playbook_file.parts
                agents_idx = None
                for i, part in enumerate(parts):
                    if part == "agents" and i + 1 < len(parts):
                        agents_idx = i + 1
                        break
                if agents_idx:
                    agent_id = parts[agents_idx]
                    agents.add(agent_id)

        # Initialize tracers and memories for discovered agents
        for agent_id in agents:
            try:
                tracer = SuperOptixTracer(agent_id)
                # Try to load historical traces if method exists
                if hasattr(tracer, "_load_traces_from_file"):
                    tracer._load_traces_from_file()
                self.agent_tracers[agent_id] = tracer

                # Try to initialize memory (optional)
                try:
                    from superoptix.memory import AgentMemory

                    memory = AgentMemory(agent_id=agent_id)
                    self.agent_memories[agent_id] = memory
                except Exception:
                    self.agent_memories[agent_id] = None
            except Exception as e:
                st.warning(f"Could not initialize tracer for agent {agent_id}: {e}")

        if not self.agent_tracers:
            # If no agents discovered, add a demo agent for testing
            demo_tracer = SuperOptixTracer("demo_agent")
            self.agent_tracers["demo_agent"] = demo_tracer
            self.agent_memories["demo_agent"] = None

    def render_dashboard(self):
        """Render the multi-agent observability dashboard."""
        st.set_page_config(
            page_title="SuperOptiX Multi-Agent Observatory",
            page_icon="🎭",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        st.title("🎭 SuperOptiX Multi-Agent Observatory")

        # Agent selection sidebar
        selected_agent = self._render_agent_selection()

        if selected_agent and selected_agent in self.agent_tracers:
            tracer = self.agent_tracers[selected_agent]
            memory = self.agent_memories.get(selected_agent)

            # Create single-agent dashboard for selected agent
            single_dashboard = ObservabilityDashboard(tracer, memory)

            # Override the title to show multi-agent context
            st.markdown(f"**Selected Agent:** `{selected_agent}`")

            # Render the single agent dashboard
            self._render_single_agent_dashboard(single_dashboard, selected_agent)
        else:
            self._render_overview_dashboard()

    def _render_agent_selection(self):
        """Render agent selection sidebar."""
        st.sidebar.header("🤖 Agent Selection")

        if not self.agent_tracers:
            st.sidebar.warning("No agents found")
            return None

        # Agent list with metrics
        agent_options = []
        agent_stats = {}

        for agent_id, tracer in self.agent_tracers.items():
            summary = tracer.get_trace_summary()
            total_events = summary.get("total_events", 0)
            error_rate = summary.get("error_rate", 0)

            agent_stats[agent_id] = {
                "events": total_events,
                "error_rate": error_rate,
                "status": "🟢"
                if error_rate < 0.1
                else "🟡"
                if error_rate < 0.3
                else "🔴",
            }

            display_name = (
                f"{agent_stats[agent_id]['status']} {agent_id} ({total_events} events)"
            )
            agent_options.append(display_name)

        # Agent selection
        if agent_options:
            selected_display = st.sidebar.selectbox(
                "Select Agent to Monitor:", agent_options, key="agent_selector"
            )

            # Extract agent_id from display name
            selected_agent = (
                selected_display.split(" ")[1] if selected_display else None
            )

            # Show quick stats for selected agent
            if selected_agent and selected_agent in agent_stats:
                stats = agent_stats[selected_agent]
                st.sidebar.metric(
                    "Total Events",
                    stats["events"],
                    delta=f"{stats['error_rate']:.1%} error rate",
                )

            return selected_agent

        return None

    def _render_single_agent_dashboard(
        self, dashboard: "ObservabilityDashboard", agent_id: str
    ):
        """Render dashboard for a single selected agent."""
        # Main dashboard tabs (same as single-agent dashboard)
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["📊 Overview", "🔍 Traces", "🧠 Memory", "⚡ Performance", "🐛 Debug"]
        )

        with tab1:
            dashboard._render_overview()

        with tab2:
            dashboard._render_traces()

        with tab3:
            dashboard._render_memory()

        with tab4:
            dashboard._render_performance()

        with tab5:
            dashboard._render_debug()

    def _render_overview_dashboard(self):
        """Render overview dashboard showing all agents."""
        if not self.agent_tracers:
            st.info("No agents found. Run some agents first to see observability data.")
            return

        st.subheader("🎭 Multi-Agent Overview")

        # Overall metrics
        col1, col2, col3, col4 = st.columns(4)

        total_agents = len(self.agent_tracers)
        total_events = sum(
            tracer.get_trace_summary().get("total_events", 0)
            for tracer in self.agent_tracers.values()
        )
        total_errors = sum(
            tracer.get_trace_summary().get("error_events", 0)
            for tracer in self.agent_tracers.values()
        )
        avg_error_rate = (
            (total_errors / max(total_events, 1)) if total_events > 0 else 0
        )

        with col1:
            st.metric("Total Agents", total_agents)

        with col2:
            st.metric("Total Events", total_events)

        with col3:
            st.metric("Total Errors", total_errors)

        with col4:
            st.metric("Avg Error Rate", f"{avg_error_rate:.2%}")

        # Agent comparison table
        st.subheader("📈 Agent Comparison")

        agent_data = []
        for agent_id, tracer in self.agent_tracers.items():
            summary = tracer.get_trace_summary()
            agent_data.append(
                {
                    "Agent": agent_id,
                    "Events": summary.get("total_events", 0),
                    "Errors": summary.get("error_events", 0),
                    "Error Rate": f"{summary.get('error_rate', 0):.2%}",
                    "Avg Duration (ms)": f"{summary.get('average_duration_ms', 0):.1f}",
                    "Status": "🟢"
                    if summary.get("error_rate", 0) < 0.1
                    else "🟡"
                    if summary.get("error_rate", 0) < 0.3
                    else "🔴",
                }
            )

        if agent_data:
            df = pd.DataFrame(agent_data)
            st.dataframe(df, use_container_width=True)

        # Multi-agent charts
        col1, col2 = st.columns(2)

        with col1:
            # Events by agent
            if agent_data:
                fig = px.bar(
                    df, x="Agent", y="Events", title="Events by Agent", color="Events"
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Error rates by agent
            if agent_data:
                error_rates = [
                    float(row["Error Rate"].strip("%")) for row in agent_data
                ]
                fig = px.bar(
                    x=[row["Agent"] for row in agent_data],
                    y=error_rates,
                    title="Error Rate by Agent (%)",
                    labels={"x": "Agent", "y": "Error Rate (%)"},
                )
                fig.update_traces(marker_color="red")
                st.plotly_chart(fig, use_container_width=True)

        # Recent activity across all agents
        st.subheader("📅 Recent Activity (All Agents)")
        self._render_multi_agent_timeline()

    def _render_multi_agent_timeline(self):
        """Render timeline showing events from all agents."""
        all_traces = []

        for agent_id, tracer in self.agent_tracers.items():
            recent_traces = tracer.traces[-50:]  # Last 50 events per agent
            for trace in recent_traces:
                all_traces.append(
                    {
                        "timestamp": trace.timestamp,
                        "agent": agent_id,
                        "component": trace.component,
                        "event_type": trace.event_type,
                        "status": trace.status,
                        "duration_ms": trace.duration_ms or 0,
                    }
                )

        if not all_traces:
            st.info("No recent trace data available")
            return

        # Sort by timestamp
        all_traces.sort(key=lambda x: x["timestamp"], reverse=True)
        all_traces = all_traces[:100]  # Show last 100 events across all agents

        df = pd.DataFrame(all_traces)

        # Timeline chart
        fig = px.scatter(
            df,
            x="timestamp",
            y="agent",
            color="status",
            hover_data=["component", "event_type", "duration_ms"],
            title="Multi-Agent Activity Timeline",
            color_discrete_map={
                "success": "green",
                "error": "red",
                "warning": "orange",
                "info": "blue",
            },
        )

        fig.update_layout(xaxis_title="Time", yaxis_title="Agent", height=400)

        st.plotly_chart(fig, use_container_width=True)


class ObservabilityDashboard:
    """Interactive dashboard for SuperOptix observability and monitoring."""

    def __init__(self, tracer: SuperOptixTracer, memory_system=None):
        self.tracer = tracer
        self.memory = memory_system
        self._load_traces_from_file()  # Load existing traces on startup

    def _load_traces_from_file(self):
        """Load historical traces from the agent's .jsonl trace file."""
        try:
            project_root = Path.cwd()
            traces_dir = project_root / ".superoptix" / "traces"
            trace_file = traces_dir / f"{self.tracer.agent_id}.jsonl"

            if trace_file.exists():
                loaded_traces = []
                with open(trace_file, "r") as f:
                    for line in f:
                        if line.strip():
                            try:
                                data = json.loads(line)
                                # Re-create TraceEvent objects
                                data["timestamp"] = datetime.fromisoformat(
                                    data["timestamp"]
                                )
                                loaded_traces.append(TraceEvent(**data))
                            except (json.JSONDecodeError, TypeError, KeyError) as e:
                                print(
                                    f"Warning: Skipping corrupted trace line in {trace_file}: {e}"
                                )

                # Prepend loaded traces to the current session's traces
                self.tracer.traces = loaded_traces + self.tracer.traces
        except Exception as e:
            st.warning(f"Could not load historical traces: {e}")

    def render_dashboard(self):
        """Render the complete observability dashboard."""
        st.set_page_config(
            page_title="SuperOptix Observability Dashboard",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        st.title("🔍 SuperOptix Observability Dashboard")
        st.markdown(f"**Agent ID:** `{self.tracer.agent_id}`")

        # Sidebar controls
        self._render_sidebar()

        # Main dashboard tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["📊 Overview", "🔍 Traces", "🧠 Memory", "⚡ Performance", "🐛 Debug"]
        )

        with tab1:
            self._render_overview()

        with tab2:
            self._render_traces()

        with tab3:
            self._render_memory()

        with tab4:
            self._render_performance()

        with tab5:
            self._render_debug()

    def _render_sidebar(self):
        """Render sidebar controls."""
        st.sidebar.header("🎛️ Controls")

        # Auto-refresh toggle
        auto_refresh = st.sidebar.checkbox(
            "Auto Refresh", value=False, key=f"auto_refresh_{self.tracer.agent_id}"
        )
        if auto_refresh:
            st.sidebar.slider(
                "Refresh Interval (seconds)",
                1,
                30,
                5,
                key=f"refresh_interval_{self.tracer.agent_id}",
            )
            st.sidebar.empty()  # Placeholder for auto-refresh logic

        # Manual refresh button
        if st.sidebar.button(
            "🔄 Refresh Data", key=f"refresh_data_{self.tracer.agent_id}"
        ):
            st.rerun()

        # Export options
        st.sidebar.header("📤 Export")
        if st.sidebar.button(
            "Export Traces", key=f"export_traces_{self.tracer.agent_id}"
        ):
            trace_data = self.tracer.export_traces("json")
            st.sidebar.download_button(
                label="📥 Download JSON",
                data=trace_data,
                file_name=f"traces_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key=f"download_json_{self.tracer.agent_id}",
            )

        # Clear data
        st.sidebar.header("🗑️ Maintenance")
        if st.sidebar.button(
            "Clear Traces",
            type="secondary",
            key=f"clear_traces_sidebar_{self.tracer.agent_id}",
        ):
            if st.sidebar.confirmation_dialog(
                "Are you sure you want to clear all traces?"
            ):
                self.tracer.clear_traces()
                st.sidebar.success("Traces cleared!")
                st.rerun()

    def _render_overview(self):
        """Render the overview tab with key metrics."""
        # Get trace summary
        summary = self.tracer.get_trace_summary()

        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Total Events",
                value=summary["total_events"],
                delta=f"+{summary.get('recent_events', 0)} recent",
            )

        with col2:
            st.metric(
                label="Error Rate",
                value=f"{summary['error_rate']:.2%}",
                delta=f"{summary['error_events']} errors",
                delta_color="inverse",
            )

        with col3:
            st.metric(
                label="Avg Duration",
                value=f"{summary['average_duration_ms']:.1f}ms",
                delta=f"Max: {summary['max_duration_ms']:.1f}ms",
            )

        with col4:
            st.metric(
                label="Components",
                value=len(summary["components_traced"]),
                delta=", ".join(summary["components_traced"][:3]),
            )

        # Charts row
        col1, col2 = st.columns(2)

        with col1:
            self._render_events_timeline()

        with col2:
            self._render_component_distribution()

        # Recent activity
        st.subheader("📈 Recent Activity")
        self._render_recent_events()

        # System health indicators
        st.subheader("🏥 System Health")
        self._render_health_indicators()

    def _render_events_timeline(self):
        """Render events timeline chart."""
        st.subheader("📅 Events Timeline")

        traces = self.tracer.traces
        if not traces:
            st.info("No trace data available")
            return

        # Convert to DataFrame
        df_data = []
        for trace in traces[-100:]:  # Last 100 events
            df_data.append(
                {
                    "timestamp": trace.timestamp,
                    "component": trace.component,
                    "event_type": trace.event_type,
                    "status": trace.status,
                    "duration_ms": trace.duration_ms or 0,
                }
            )

        df = pd.DataFrame(df_data)

        if not df.empty:
            # Timeline chart
            fig = px.scatter(
                df,
                x="timestamp",
                y="component",
                color="status",
                size="duration_ms",
                hover_data=["event_type", "duration_ms"],
                title="Event Timeline",
                color_discrete_map={
                    "success": "green",
                    "error": "red",
                    "warning": "orange",
                    "info": "blue",
                },
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No timeline data available")

    def _render_component_distribution(self):
        """Render component distribution pie chart."""
        st.subheader("🔧 Component Distribution")

        summary = self.tracer.get_trace_summary()
        perf_stats = summary.get("performance_stats", {})
        comp_stats = perf_stats.get("component_stats", {})

        if comp_stats:
            components = list(comp_stats.keys())
            operations = [comp_stats[comp]["operations"] for comp in components]

            fig = px.pie(
                values=operations, names=components, title="Operations by Component"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No component data available")

    def _render_recent_events(self):
        """Render recent events table."""
        recent_traces = self.tracer.traces[-20:]  # Last 20 events

        if not recent_traces:
            st.info("No recent events")
            return

        # Convert to DataFrame for display
        df_data = []
        for trace in reversed(recent_traces):
            df_data.append(
                {
                    "Time": trace.timestamp.strftime("%H:%M:%S"),
                    "Component": trace.component,
                    "Event": trace.event_type,
                    "Status": trace.status,
                    "Duration (ms)": f"{trace.duration_ms:.1f}"
                    if trace.duration_ms
                    else "-",
                    "Data": str(trace.data)[:50] + "..."
                    if len(str(trace.data)) > 50
                    else str(trace.data),
                }
            )

        df = pd.DataFrame(df_data)

        # Style the dataframe
        def style_status(val):
            color = {
                "success": "background-color: #d4edda",
                "error": "background-color: #f8d7da",
                "warning": "background-color: #fff3cd",
                "info": "background-color: #d1ecf1",
            }.get(val, "")
            return color

        styled_df = df.style.applymap(style_status, subset=["Status"])
        st.dataframe(styled_df, use_container_width=True)

    def _render_health_indicators(self):
        """Render system health indicators."""
        summary = self.tracer.get_trace_summary()

        col1, col2, col3 = st.columns(3)

        with col1:
            # Error rate health
            error_rate = summary["error_rate"]
            if error_rate < 0.01:
                health_color = "🟢"
                health_status = "Healthy"
            elif error_rate < 0.05:
                health_color = "🟡"
                health_status = "Warning"
            else:
                health_color = "🔴"
                health_status = "Critical"

            st.metric(
                label=f"{health_color} Error Rate Health",
                value=health_status,
                delta=f"{error_rate:.2%}",
            )

        with col2:
            # Performance health
            avg_duration = summary["average_duration_ms"]
            if avg_duration < 1000:
                perf_color = "🟢"
                perf_status = "Fast"
            elif avg_duration < 5000:
                perf_color = "🟡"
                perf_status = "Moderate"
            else:
                perf_color = "🔴"
                perf_status = "Slow"

            st.metric(
                label=f"{perf_color} Performance Health",
                value=perf_status,
                delta=f"{avg_duration:.1f}ms avg",
            )

        with col3:
            # Memory health (if available)
            if self.memory:
                try:
                    mem_summary = self.memory.get_memory_summary()
                    total_items = (
                        mem_summary["short_term_memory"]["size"]
                        + mem_summary["long_term_memory"]["total_items"]
                    )

                    if total_items < 1000:
                        mem_color = "🟢"
                        mem_status = "Healthy"
                    elif total_items < 5000:
                        mem_color = "🟡"
                        mem_status = "Growing"
                    else:
                        mem_color = "🔴"
                        mem_status = "High Usage"

                    st.metric(
                        label=f"{mem_color} Memory Health",
                        value=mem_status,
                        delta=f"{total_items} items",
                    )
                except Exception:
                    st.metric(
                        label="🔴 Memory Health", value="Error", delta="Unable to check"
                    )
            else:
                st.metric(label="⚪ Memory Health", value="N/A", delta="Not configured")

    def _render_traces(self):
        """Render the traces tab with detailed trace analysis."""
        st.subheader("🔍 Trace Analysis")

        # Trace filters
        col1, col2, col3 = st.columns(3)

        with col1:
            component_filter = st.selectbox(
                "Filter by Component",
                ["All"] + list(self.tracer.get_trace_summary()["components_traced"]),
                key=f"component_filter_{self.tracer.agent_id}",
            )

        with col2:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "success", "error", "warning", "info"],
                key=f"status_filter_{self.tracer.agent_id}",
            )

        with col3:
            limit = st.number_input(
                "Number of traces",
                min_value=10,
                max_value=1000,
                value=100,
                key=f"trace_limit_{self.tracer.agent_id}",
            )

        # Apply filters
        filtered_traces = self.tracer.traces[-limit:]

        if component_filter != "All":
            filtered_traces = [
                t for t in filtered_traces if t.component == component_filter
            ]

        if status_filter != "All":
            filtered_traces = [t for t in filtered_traces if t.status == status_filter]

        # Trace tree visualization
        st.subheader("🌳 Trace Tree")
        if st.button(
            "Generate Trace Tree", key=f"generate_trace_tree_{self.tracer.agent_id}"
        ):
            self._render_trace_tree()

        # Detailed trace table
        st.subheader("📋 Detailed Traces")
        self._render_detailed_traces(filtered_traces)

        # Error analysis
        if st.checkbox(
            "Show Error Analysis", key=f"show_error_analysis_{self.tracer.agent_id}"
        ):
            self._render_error_analysis()

    def _render_trace_tree(self):
        """Render hierarchical trace tree."""
        trace_tree = self.tracer.get_trace_tree()

        def render_tree_node(traces, level=0):
            for trace_item in traces:
                event = trace_item["event"]
                indent = "  " * level
                duration = (
                    f" ({event.get('duration_ms', 0):.1f}ms)"
                    if event.get("duration_ms")
                    else ""
                )

                st.text(
                    f"{indent}├─ {event['component']}: {event['event_type']}{duration}"
                )

                if trace_item["children"]:
                    render_tree_node(trace_item["children"], level + 1)

        if trace_tree["root_traces"]:
            st.code("Trace Execution Tree:")
            render_tree_node(trace_tree["root_traces"])
        else:
            st.info("No trace tree data available")

    def _render_detailed_traces(self, traces: List[TraceEvent]):
        """Render detailed traces table."""
        if not traces:
            st.info("No traces match the current filters")
            return

        # Convert to DataFrame
        df_data = []
        for trace in traces:
            df_data.append(
                {
                    "Timestamp": trace.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                    "Component": trace.component,
                    "Event Type": trace.event_type,
                    "Status": trace.status,
                    "Duration (ms)": f"{trace.duration_ms:.2f}"
                    if trace.duration_ms
                    else "-",
                    "Parent ID": trace.parent_id[:8] if trace.parent_id else "-",
                    "Event ID": trace.event_id[:8],
                    "Data": json.dumps(trace.data) if trace.data else "{}",
                }
            )

        df = pd.DataFrame(df_data)

        # Interactive table with selection
        selected_rows = st.dataframe(
            df,
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row",
            key=f"detailed_traces_table_{self.tracer.agent_id}",
        )

        # Show detailed view of selected trace
        if selected_rows and len(selected_rows["selection"]["rows"]) > 0:
            selected_idx = selected_rows["selection"]["rows"][0]
            selected_trace = traces[selected_idx]

            st.subheader("🔍 Trace Details")

            col1, col2 = st.columns(2)

            with col1:
                st.json(
                    {
                        "event_id": selected_trace.event_id,
                        "timestamp": selected_trace.timestamp.isoformat(),
                        "component": selected_trace.component,
                        "event_type": selected_trace.event_type,
                        "status": selected_trace.status,
                        "duration_ms": selected_trace.duration_ms,
                        "parent_id": selected_trace.parent_id,
                    }
                )

            with col2:
                st.subheader("Event Data")
                st.json(selected_trace.data)

                if selected_trace.metadata:
                    st.subheader("Metadata")
                    st.json(selected_trace.metadata)

    def _render_error_analysis(self):
        """Render error analysis section."""
        error_traces = self.tracer.get_error_traces()

        if not error_traces:
            st.success("No errors found! 🎉")
            return

        st.subheader("🚨 Error Analysis")

        # Error summary
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Errors", len(error_traces))

            # Error by component
            error_by_component = {}
            for trace in error_traces:
                comp = trace.component
                error_by_component[comp] = error_by_component.get(comp, 0) + 1

            if error_by_component:
                fig = px.bar(
                    x=list(error_by_component.keys()),
                    y=list(error_by_component.values()),
                    title="Errors by Component",
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Recent errors timeline
            if len(error_traces) > 1:
                error_df = pd.DataFrame(
                    [
                        {
                            "timestamp": trace.timestamp,
                            "component": trace.component,
                            "error": trace.data.get("error", "Unknown error")[:50],
                        }
                        for trace in error_traces[-20:]
                    ]
                )

                fig = px.scatter(
                    error_df,
                    x="timestamp",
                    y="component",
                    hover_data=["error"],
                    title="Error Timeline",
                    color_discrete_sequence=["red"],
                )
                st.plotly_chart(fig, use_container_width=True)

        # Error details
        st.subheader("Error Details")
        for i, trace in enumerate(error_traces[-10:], 1):
            with st.expander(
                f"Error {i}: {trace.component} - {trace.timestamp.strftime('%H:%M:%S')}"
            ):
                st.code(trace.data.get("error", "Unknown error"))
                st.json(trace.data)

    def _render_memory(self):
        """Render the memory tab with memory system analysis."""
        if not self.memory:
            st.warning("Memory system not available")
            return

        st.subheader("🧠 Memory System Analysis")

        try:
            memory_summary = self.memory.get_memory_summary()

            # Memory overview metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Short-term Items", memory_summary["short_term_memory"]["size"]
                )

            with col2:
                st.metric(
                    "Long-term Items", memory_summary["long_term_memory"]["total_items"]
                )

            with col3:
                st.metric(
                    "Active Episodes",
                    memory_summary["episodic_memory"]["active_episodes"],
                )

            with col4:
                st.metric("Total Interactions", memory_summary["interaction_count"])

            # Memory usage over time
            st.subheader("📈 Memory Usage Trends")
            # This would require historical data tracking
            st.info(
                "Memory usage trends will be available with historical data collection"
            )

            # Recent memories
            st.subheader("💭 Recent Memories")
            recent_memories = self.memory.recall("", limit=10)

            if recent_memories:
                for i, memory in enumerate(recent_memories, 1):
                    with st.expander(
                        f"Memory {i} (Similarity: {memory.get('similarity', 0):.2f})"
                    ):
                        st.write(memory["content"])
                        if memory.get("metadata"):
                            st.json(memory["metadata"])
            else:
                st.info("No memories found")

            # Memory insights
            if hasattr(self.memory, "get_memory_insights"):
                st.subheader("🔍 Memory Insights")
                try:
                    insights = self.memory.get_memory_insights()
                    st.json(insights)
                except Exception as e:
                    st.error(f"Error getting memory insights: {e}")

        except Exception as e:
            st.error(f"Error accessing memory system: {e}")

    def _render_performance(self):
        """Render the performance tab with performance metrics."""
        st.subheader("⚡ Performance Analysis")

        summary = self.tracer.get_trace_summary()
        perf_stats = summary.get("performance_stats", {})

        # Performance overview
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Operations", perf_stats.get("total_operations", 0))

        with col2:
            st.metric(
                "Average Duration", f"{perf_stats.get('average_duration', 0):.2f}ms"
            )

        with col3:
            error_rate = perf_stats.get("total_errors", 0) / max(
                perf_stats.get("total_operations", 1), 1
            )
            st.metric("Error Rate", f"{error_rate:.2%}")

        # Performance by component
        comp_stats = perf_stats.get("component_stats", {})
        if comp_stats:
            st.subheader("📊 Performance by Component")

            # Create DataFrame for component stats
            comp_df_data = []
            for comp, stats in comp_stats.items():
                comp_df_data.append(
                    {
                        "Component": comp,
                        "Operations": stats["operations"],
                        "Errors": stats["errors"],
                        "Error Rate": f"{stats['errors'] / stats['operations'] * 100:.1f}%"
                        if stats["operations"] > 0
                        else "0%",
                        "Avg Duration (ms)": f"{stats['avg_duration']:.2f}",
                    }
                )

            comp_df = pd.DataFrame(comp_df_data)
            st.dataframe(comp_df, use_container_width=True)

            # Performance charts
            col1, col2 = st.columns(2)

            with col1:
                # Operations by component
                fig = px.bar(
                    comp_df,
                    x="Component",
                    y="Operations",
                    title="Operations by Component",
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Average duration by component
                fig = px.bar(
                    comp_df,
                    x="Component",
                    y="Avg Duration (ms)",
                    title="Average Duration by Component",
                )
                st.plotly_chart(fig, use_container_width=True)

        # Duration distribution
        st.subheader("⏱️ Duration Distribution")
        traces_with_duration = [
            t for t in self.tracer.traces if t.duration_ms is not None
        ]

        if traces_with_duration:
            durations = [t.duration_ms for t in traces_with_duration]

            fig = px.histogram(
                x=durations,
                nbins=30,
                title="Response Time Distribution",
                labels={"x": "Duration (ms)", "y": "Count"},
            )
            st.plotly_chart(fig, use_container_width=True)

            # Duration percentiles
            percentiles_df = pd.DataFrame(
                {
                    "Percentile": ["P50", "P75", "P90", "P95", "P99"],
                    "Duration (ms)": [
                        pd.Series(durations).quantile(0.5),
                        pd.Series(durations).quantile(0.75),
                        pd.Series(durations).quantile(0.9),
                        pd.Series(durations).quantile(0.95),
                        pd.Series(durations).quantile(0.99),
                    ],
                }
            )

            st.subheader("📈 Duration Percentiles")
            st.dataframe(percentiles_df, use_container_width=True)
        else:
            st.info("No duration data available")

    def _render_debug(self):
        """Render the debug tab with debugging tools."""
        st.subheader("🐛 Debug Tools")

        # Debug controls
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🎛️ Debug Controls")

            if st.button(
                "Clear All Traces", key=f"clear_all_traces_{self.tracer.agent_id}"
            ):
                self.tracer.clear_traces()
                st.success("All traces cleared!")
                st.rerun()

            if st.button(
                "Generate Test Traces",
                key=f"generate_test_traces_{self.tracer.agent_id}",
            ):
                # Generate some test traces for demonstration
                self._generate_test_traces()
                st.success("Test traces generated!")
                st.rerun()

        with col2:
            st.subheader("📤 Export Options")

            export_format = st.selectbox(
                "Export Format",
                ["json", "csv"],
                key=f"export_format_{self.tracer.agent_id}",
            )

            if st.button(
                "Export Traces", key=f"export_traces_debug_{self.tracer.agent_id}"
            ):
                if export_format == "json":
                    data = self.tracer.export_traces("json")
                    st.download_button(
                        "Download JSON",
                        data,
                        f"traces_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        "application/json",
                        key=f"download_json_debug_{self.tracer.agent_id}",
                    )
                else:
                    # Convert to CSV
                    traces_data = []
                    for trace in self.tracer.traces:
                        traces_data.append(
                            {
                                "timestamp": trace.timestamp.isoformat(),
                                "component": trace.component,
                                "event_type": trace.event_type,
                                "status": trace.status,
                                "duration_ms": trace.duration_ms,
                                "data": json.dumps(trace.data),
                            }
                        )

                    df = pd.DataFrame(traces_data)
                    csv_data = df.to_csv(index=False)

                    st.download_button(
                        "Download CSV",
                        csv_data,
                        f"traces_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv",
                        key=f"download_csv_debug_{self.tracer.agent_id}",
                    )

        # Raw trace data viewer
        st.subheader("🔍 Raw Trace Data")
        if st.checkbox(
            "Show Raw Traces", key=f"show_raw_traces_{self.tracer.agent_id}"
        ):
            selected_trace_count = st.slider(
                "Number of traces to show",
                1,
                100,
                10,
                key=f"trace_count_slider_{self.tracer.agent_id}",
            )

            for i, trace in enumerate(self.tracer.traces[-selected_trace_count:]):
                with st.expander(
                    f"Trace {i + 1}: {trace.component} - {trace.event_type}"
                ):
                    st.json(trace.to_dict())

        # System information
        st.subheader("ℹ️ System Information")
        system_info = {
            "Agent ID": self.tracer.agent_id,
            "External Tracers": list(self.tracer.external_tracers.keys()),
            "Total Traces": len(self.tracer.traces),
            "Memory System": "Available" if self.memory else "Not Available",
            "Dashboard Version": "1.0.0",
        }
        st.json(system_info)

    def _generate_test_traces(self):
        """Generate test traces for demonstration purposes."""
        import random
        import time

        components = ["dspy_adapter", "memory_system", "agent_module", "llm_call"]
        operations = ["setup", "execute", "cleanup", "recall", "store"]
        statuses = [
            "success",
            "success",
            "success",
            "error",
            "warning",
        ]  # Weighted towards success

        for _ in range(20):
            component = random.choice(components)
            operation = random.choice(operations)
            status = random.choice(statuses)
            duration = random.uniform(10, 1000)

            self.tracer.add_event(
                event_type=f"{operation}_test",
                component=component,
                data={
                    "operation": operation,
                    "test_data": f"Test data for {component}",
                    "random_value": random.randint(1, 100),
                },
                status=status,
            )

            # Add corresponding end event for operations with duration
            if random.choice([True, False]):
                time.sleep(0.001)  # Small delay
                self.tracer.add_event(
                    event_type=f"{operation}_test_end",
                    component=component,
                    data={
                        "operation": operation,
                        "duration_ms": duration,
                        "completed": True,
                    },
                    status=status,
                )
