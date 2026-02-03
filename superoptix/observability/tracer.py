"""Core tracing system for SuperOptix observability."""

import json
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class TraceEvent:
    """Represents a single trace event with comprehensive metadata."""

    event_id: str
    timestamp: datetime
    event_type: str
    component: str
    data: Dict[str, Any]
    parent_id: Optional[str] = None
    duration_ms: Optional[float] = None
    status: str = "success"  # success, error, warning, info
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        return result


class SuperOptixTracer:
    """Comprehensive tracer for SuperOptix agent execution with external integrations."""

    def __init__(
        self,
        agent_id: str,
        enable_external_tracing: bool = False,
        auto_load: bool = True,
    ):
        self.agent_id = agent_id
        self.enable_external_tracing = enable_external_tracing
        self.traces: List[TraceEvent] = []
        self.current_trace_stack: List[str] = []
        self._lock = threading.RLock()

        # External tracing integrations
        self.external_tracers = {}
        self._setup_external_tracers()

        # Performance tracking
        self.performance_stats = {
            "total_operations": 0,
            "total_errors": 0,
            "average_duration": 0.0,
            "component_stats": {},
        }

        # Auto-load existing traces if requested
        if auto_load:
            self.load_traces()

    def _setup_external_tracers(self):
        """Setup external tracing integrations (MLflow, Langfuse, etc.)."""
        if not self.enable_external_tracing:
            return

        # MLflow integration
        try:
            import mlflow

            mlflow.set_experiment(f"SuperOptix-{self.agent_id}")
            self.external_tracers["mlflow"] = mlflow
            print(f"✅ MLflow tracing enabled for agent {self.agent_id}")
        except ImportError:
            print("⚠️  MLflow not available - install with: pip install mlflow")

        # Langfuse integration
        try:
            from langfuse import Langfuse

            langfuse = Langfuse()
            if langfuse.auth_check():
                self.external_tracers["langfuse"] = langfuse
                print(f"✅ Langfuse tracing enabled for agent {self.agent_id}")
        except ImportError:
            print("⚠️  Langfuse not available - install with: pip install langfuse")
        except Exception:
            print("⚠️  Langfuse authentication failed - check credentials")

    @contextmanager
    def trace_operation(self, operation_name: str, component: str, **metadata):
        """Context manager for tracing operations with automatic timing."""
        event_id = str(uuid.uuid4())
        start_time = time.time()
        parent_id = self.current_trace_stack[-1] if self.current_trace_stack else None

        with self._lock:
            self.current_trace_stack.append(event_id)

        try:
            # Create start event
            start_event = TraceEvent(
                event_id=event_id,
                timestamp=datetime.now(),
                event_type=f"{operation_name}_start",
                component=component,
                data={"operation": operation_name, **metadata},
                parent_id=parent_id,
                metadata=metadata,
            )
            self._add_trace_event(start_event)

            yield event_id

            # Create success end event
            duration = (time.time() - start_time) * 1000
            end_event = TraceEvent(
                event_id=f"{event_id}_end",
                timestamp=datetime.now(),
                event_type=f"{operation_name}_end",
                component=component,
                data={"operation": operation_name, "duration_ms": duration, **metadata},
                parent_id=event_id,
                duration_ms=duration,
                status="success",
            )
            self._add_trace_event(end_event)
            self._update_performance_stats(component, duration, success=True)

        except Exception as e:
            # Create error end event
            duration = (time.time() - start_time) * 1000
            error_event = TraceEvent(
                event_id=f"{event_id}_error",
                timestamp=datetime.now(),
                event_type=f"{operation_name}_error",
                component=component,
                data={
                    "operation": operation_name,
                    "error": str(e),
                    "duration_ms": duration,
                    **metadata,
                },
                parent_id=event_id,
                duration_ms=duration,
                status="error",
            )
            self._add_trace_event(error_event)
            self._update_performance_stats(component, duration, success=False)
            raise
        finally:
            with self._lock:
                if (
                    self.current_trace_stack
                    and self.current_trace_stack[-1] == event_id
                ):
                    self.current_trace_stack.pop()

    def add_event(
        self,
        event_type: str,
        component: str,
        data: Dict[str, Any] = None,
        status: str = "info",
        metadata: Dict[str, Any] = None,
    ):
        """Add a standalone trace event."""
        event = TraceEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type=event_type,
            component=component,
            data=data or {},
            parent_id=self.current_trace_stack[-1]
            if self.current_trace_stack
            else None,
            status=status,
            metadata=metadata,
        )
        self._add_trace_event(event)

    def _add_trace_event(self, event: TraceEvent):
        """Add trace event to internal storage and external tracers."""
        with self._lock:
            self.traces.append(event)

        # Send to external tracers
        self._send_to_external_tracers(event)

    def _send_to_external_tracers(self, event: TraceEvent):
        """Send trace event to external tracing systems."""
        # MLflow integration
        if "mlflow" in self.external_tracers:
            try:
                mlflow = self.external_tracers["mlflow"]
                with mlflow.start_run(
                    nested=True, run_name=f"{event.component}_{event.event_type}"
                ):
                    mlflow.log_params(
                        {
                            "event_type": event.event_type,
                            "component": event.component,
                            "agent_id": self.agent_id,
                            "status": event.status,
                        }
                    )
                    if event.duration_ms:
                        mlflow.log_metric("duration_ms", event.duration_ms)
                    mlflow.log_dict(event.data, f"event_data_{event.event_id[:8]}.json")
            except Exception as e:
                print(f"Warning: MLflow logging failed: {e}")

        # Langfuse integration
        if "langfuse" in self.external_tracers:
            try:
                langfuse = self.external_tracers["langfuse"]
                langfuse.trace(
                    name=event.event_type,
                    input=event.data,
                    metadata={
                        "component": event.component,
                        "agent_id": self.agent_id,
                        "event_id": event.event_id,
                        "parent_id": event.parent_id,
                        "status": event.status,
                        "duration_ms": event.duration_ms,
                    },
                )
            except Exception as e:
                print(f"Warning: Langfuse logging failed: {e}")

    def _update_performance_stats(self, component: str, duration: float, success: bool):
        """Update performance statistics."""
        with self._lock:
            self.performance_stats["total_operations"] += 1
            if not success:
                self.performance_stats["total_errors"] += 1

            # Update average duration
            total_ops = self.performance_stats["total_operations"]
            current_avg = self.performance_stats["average_duration"]
            new_avg = ((current_avg * (total_ops - 1)) + duration) / total_ops
            self.performance_stats["average_duration"] = new_avg

            # Update component-specific stats
            if component not in self.performance_stats["component_stats"]:
                self.performance_stats["component_stats"][component] = {
                    "operations": 0,
                    "errors": 0,
                    "avg_duration": 0.0,
                }

            comp_stats = self.performance_stats["component_stats"][component]
            comp_stats["operations"] += 1
            if not success:
                comp_stats["errors"] += 1

            comp_ops = comp_stats["operations"]
            comp_avg = comp_stats["avg_duration"]
            comp_stats["avg_duration"] = (
                (comp_avg * (comp_ops - 1)) + duration
            ) / comp_ops

    def get_traces_by_component(self, component: str) -> List[TraceEvent]:
        """Get all traces for a specific component."""
        with self._lock:
            return [t for t in self.traces if t.component == component]

    def get_traces_by_type(self, event_type: str) -> List[TraceEvent]:
        """Get all traces of a specific type."""
        with self._lock:
            return [t for t in self.traces if t.event_type == event_type]

    def get_error_traces(self) -> List[TraceEvent]:
        """Get all error traces for debugging."""
        with self._lock:
            return [t for t in self.traces if t.status == "error"]

    def export_traces(
        self, format: str = "jsonl", filename: Optional[str] = None
    ) -> str:
        """
        Export traces to a file or return as a string.
        Defaults to appending to a .jsonl file for the agent.
        """
        with self._lock:
            if not self.traces:
                return ""

            if format == "jsonl":
                output_path = None
                if filename:
                    output_path = Path(filename)
                else:
                    # Default to the project's trace directory
                    project_root = Path.cwd()  # Assumes CWD is project root
                    traces_dir = project_root / ".superoptix" / "traces"
                    traces_dir.mkdir(parents=True, exist_ok=True)
                    output_path = traces_dir / f"{self.agent_id}.jsonl"

                # Append traces to the file in JSON Lines format
                lines_to_write = [json.dumps(t.to_dict()) for t in self.traces]
                with open(output_path, "a") as f:
                    for line in lines_to_write:
                        f.write(line + "\n")

                # We don't print here to keep the agent run output clean
                # console.print(f"Traces exported to {output_path}")
                return "\n".join(lines_to_write)

            elif format == "json":
                trace_data = {
                    "agent_id": self.agent_id,
                    "export_timestamp": datetime.now().isoformat(),
                    "summary": self.get_trace_summary(),
                    "traces": [t.to_dict() for t in self.traces],
                }
                json_str = json.dumps(trace_data, indent=2, default=str)

                if filename:
                    with open(filename, "w") as f:
                        f.write(json_str)
                return json_str

            else:
                raise ValueError(f"Unsupported export format: {format}")

    def clear_traces(self):
        """Clear all stored traces."""
        with self._lock:
            self.traces.clear()
            self.performance_stats = {
                "total_operations": 0,
                "total_errors": 0,
                "average_duration": 0.0,
                "component_stats": {},
            }
        print(f"Cleared all traces for agent {self.agent_id}")

    def get_trace_tree(self) -> Dict[str, Any]:
        """Get traces organized as a hierarchical tree."""
        with self._lock:
            root_traces = [t for t in self.traces if t.parent_id is None]

            def build_tree(parent_id: str) -> List[Dict[str, Any]]:
                children = [t for t in self.traces if t.parent_id == parent_id]
                return [
                    {"event": child.to_dict(), "children": build_tree(child.event_id)}
                    for child in children
                ]

            return {
                "agent_id": self.agent_id,
                "root_traces": [
                    {"event": root.to_dict(), "children": build_tree(root.event_id)}
                    for root in root_traces
                ],
            }

    def load_traces(self, days: int = None) -> int:
        """Load traces from stored JSONL files."""
        loaded_count = 0

        # Look for trace files in multiple locations
        trace_paths = self._find_trace_files()

        for trace_path in trace_paths:
            try:
                with open(trace_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue

                        try:
                            trace_data = json.loads(line)
                            # Convert back to TraceEvent
                            trace_event = self._dict_to_trace_event(trace_data)

                            # Filter by days if specified
                            if days is not None:
                                days_ago = datetime.now() - timedelta(days=days)
                                if trace_event.timestamp < days_ago:
                                    continue

                            # Add to traces if not already present
                            if not any(
                                t.event_id == trace_event.event_id for t in self.traces
                            ):
                                self.traces.append(trace_event)
                                loaded_count += 1

                        except json.JSONDecodeError as e:
                            print(
                                f"Warning: Failed to parse trace line in {trace_path}: {e}"
                            )
                            continue

            except Exception as e:
                print(f"Warning: Failed to load traces from {trace_path}: {e}")
                continue

        # Sort traces by timestamp
        self.traces.sort(key=lambda t: t.timestamp)
        return loaded_count

    def _find_trace_files(self) -> List[Path]:
        """Find all trace files for this agent."""
        trace_files = []

        # Search patterns for trace files
        search_locations = [
            Path.cwd() / ".superoptix" / "traces",
            Path.cwd() / "swe" / ".superoptix" / "traces",
            Path.cwd() / "superoptix" / "swe" / ".superoptix" / "traces",
            Path.cwd() / "superoptix" / "swe" / "traces",
        ]

        for location in search_locations:
            if location.exists():
                # Look for exact agent match
                agent_file = location / f"{self.agent_id}.jsonl"
                if agent_file.exists():
                    trace_files.append(agent_file)

                # Also look for any JSONL files if we want all traces
                if self.agent_id == "*" or self.agent_id is None:
                    for jsonl_file in location.glob("*.jsonl"):
                        if jsonl_file not in trace_files:
                            trace_files.append(jsonl_file)

        return trace_files

    def _dict_to_trace_event(self, data: Dict[str, Any]) -> TraceEvent:
        """Convert dictionary back to TraceEvent object."""
        # Parse timestamp
        timestamp = datetime.fromisoformat(data["timestamp"])

        return TraceEvent(
            event_id=data["event_id"],
            timestamp=timestamp,
            event_type=data["event_type"],
            component=data["component"],
            data=data["data"],
            parent_id=data.get("parent_id"),
            duration_ms=data.get("duration_ms"),
            status=data.get("status", "success"),
            metadata=data.get("metadata"),
        )

    @staticmethod
    def get_all_available_agents() -> List[str]:
        """Get list of all agents that have trace files."""
        agents = set()

        search_locations = [
            Path.cwd() / ".superoptix" / "traces",
            Path.cwd() / "swe" / ".superoptix" / "traces",
            Path.cwd() / "superoptix" / "swe" / ".superoptix" / "traces",
            Path.cwd() / "superoptix" / "swe" / "traces",
        ]

        for location in search_locations:
            if location.exists():
                for jsonl_file in location.glob("*.jsonl"):
                    agent_name = jsonl_file.stem
                    agents.add(agent_name)

        return sorted(list(agents))

    def get_trace_summary(self, days: int = None) -> Dict[str, Any]:
        """Get comprehensive trace summary with analytics."""
        with self._lock:
            # Filter traces by days if specified
            traces_to_analyze = self.traces
            if days is not None:
                from datetime import timedelta

                cutoff_date = datetime.now() - timedelta(days=days)
                traces_to_analyze = [
                    t for t in self.traces if t.timestamp >= cutoff_date
                ]

            total_events = len(traces_to_analyze)
            success_events = len(
                [t for t in traces_to_analyze if t.status == "success"]
            )
            error_events = len([t for t in traces_to_analyze if t.status == "error"])
            warning_events = len(
                [t for t in traces_to_analyze if t.status == "warning"]
            )
            components = set(t.component for t in traces_to_analyze)

            # Calculate performance metrics
            durations = [
                t.duration_ms for t in traces_to_analyze if t.duration_ms is not None
            ]

            # Get most common errors
            errors = [
                t.data.get("error", "Unknown error")
                for t in traces_to_analyze
                if t.status == "error"
            ]
            from collections import Counter

            most_common_errors = Counter(errors).most_common(5)

            summary = {
                "agent_id": self.agent_id,
                "total_events": total_events,
                "success_events": success_events,
                "error_events": error_events,
                "warning_events": warning_events,
                "error_rate": error_events / total_events if total_events > 0 else 0,
                "components_traced": list(components),
                "average_duration_ms": sum(durations) / len(durations)
                if durations
                else 0,
                "median_duration_ms": sorted(durations)[len(durations) // 2]
                if durations
                else 0,
                "p95_duration_ms": sorted(durations)[int(len(durations) * 0.95)]
                if durations
                else 0,
                "min_duration_ms": min(durations) if durations else 0,
                "max_duration_ms": max(durations) if durations else 0,
                "external_tracers": list(self.external_tracers.keys()),
                "performance_stats": self.performance_stats,
                "trace_count": len(traces_to_analyze),
                "most_common_errors": most_common_errors,
                "days_analyzed": days,
            }

            return summary
