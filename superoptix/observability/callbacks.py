"""DSPy Callback system for SuperOptiX observability."""

from datetime import datetime
from typing import Any, Dict

from dspy.utils.callback import BaseCallback

from .tracer import SuperOptixTracer


class SuperOptixCallback(BaseCallback):
    """Custom DSPy callback for comprehensive SuperOptiX observability."""

    def __init__(self, tracer: SuperOptixTracer, memory_system=None):
        self.tracer = tracer
        self.memory = memory_system
        self.module_stack = []
        self.call_stack = []

    def on_module_start(self, call_id, inputs):
        """Called when a DSPy module starts execution."""
        module_info = {
            "call_id": call_id,
            "inputs": self._truncate_data(str(inputs), 200),
            "input_count": len(inputs) if isinstance(inputs, dict) else 1,
            "module_type": self._infer_module_type(inputs),
        }

        # Add to tracer
        self.tracer.add_event(
            event_type="dspy_module_start",
            component="dspy_module",
            data=module_info,
            status="info",
        )

        # Add to memory tracking if available
        if self.memory:
            self.memory.add_interaction_event(
                event_type="dspy_module_start",
                description=f"DSPy module started: {call_id}",
                data=module_info,
            )

        self.module_stack.append(
            {"call_id": call_id, "start_time": datetime.now(), "inputs": inputs}
        )

    def on_module_end(self, call_id, outputs, exception):
        """Called when a DSPy module completes execution."""
        # Find corresponding start event
        start_event = None
        for i, event in enumerate(self.module_stack):
            if event["call_id"] == call_id:
                start_event = self.module_stack.pop(i)
                break

        # Calculate duration
        duration_ms = None
        if start_event:
            duration = datetime.now() - start_event["start_time"]
            duration_ms = duration.total_seconds() * 1000

        if exception:
            status = "error"
            result_info = {
                "error": str(exception),
                "error_type": type(exception).__name__,
                "call_id": call_id,
                "duration_ms": duration_ms,
            }
        else:
            status = "success"
            result_info = {
                "outputs": self._truncate_data(str(outputs), 200),
                "output_count": len(outputs) if isinstance(outputs, dict) else 1,
                "call_id": call_id,
                "duration_ms": duration_ms,
                "output_keys": list(outputs.keys())
                if isinstance(outputs, dict)
                else [],
            }

        # Add to tracer
        self.tracer.add_event(
            event_type="dspy_module_end",
            component="dspy_module",
            data=result_info,
            status=status,
        )

        # Add to memory tracking if available
        if self.memory:
            self.memory.add_interaction_event(
                event_type="dspy_module_end",
                description=f"DSPy module completed: {call_id}",
                data={**result_info, "status": status},
            )

    def on_lm_start(self, call_id, inputs):
        """Called when LM call starts."""
        lm_info = {
            "call_id": call_id,
            "prompt_length": len(str(inputs)),
            "timestamp": datetime.now().isoformat(),
            "input_preview": self._truncate_data(str(inputs), 100),
        }

        # Add to tracer
        self.tracer.add_event(
            event_type="llm_call_start",
            component="language_model",
            data=lm_info,
            status="info",
        )

        # Add to memory tracking if available
        if self.memory:
            self.memory.add_interaction_event(
                event_type="llm_call_start",
                description="Language model call initiated",
                data=lm_info,
            )

        self.call_stack.append(
            {"call_id": call_id, "start_time": datetime.now(), "type": "lm_call"}
        )

    def on_lm_end(self, call_id, outputs, exception):
        """Called when LM call completes."""
        # Find corresponding start event
        start_event = None
        for i, event in enumerate(self.call_stack):
            if event["call_id"] == call_id and event["type"] == "lm_call":
                start_event = self.call_stack.pop(i)
                break

        # Calculate duration
        duration_ms = None
        if start_event:
            duration = datetime.now() - start_event["start_time"]
            duration_ms = duration.total_seconds() * 1000

        if exception:
            lm_result = {
                "error": str(exception),
                "error_type": type(exception).__name__,
                "call_id": call_id,
                "duration_ms": duration_ms,
                "status": "failed",
            }
            status = "error"
        else:
            lm_result = {
                "response_length": len(str(outputs)),
                "call_id": call_id,
                "duration_ms": duration_ms,
                "status": "success",
                "response_preview": self._truncate_data(str(outputs), 100),
            }
            status = "success"

        # Add to tracer
        self.tracer.add_event(
            event_type="llm_call_end",
            component="language_model",
            data=lm_result,
            status=status,
        )

        # Add to memory tracking if available
        if self.memory:
            self.memory.add_interaction_event(
                event_type="llm_call_end",
                description="Language model call completed",
                data=lm_result,
            )

    def on_adapter_format_start(self, call_id, inputs):
        """Called when adapter starts formatting input prompt."""
        format_info = {
            "call_id": call_id,
            "input_size": len(str(inputs)),
            "timestamp": datetime.now().isoformat(),
        }

        self.tracer.add_event(
            event_type="adapter_format_start",
            component="dspy_adapter",
            data=format_info,
            status="info",
        )

    def on_adapter_format_end(self, call_id, outputs, exception):
        """Called when adapter completes formatting input prompt."""
        if exception:
            format_result = {
                "error": str(exception),
                "call_id": call_id,
                "status": "failed",
            }
            status = "error"
        else:
            format_result = {
                "formatted_size": len(str(outputs)),
                "call_id": call_id,
                "status": "success",
            }
            status = "success"

        self.tracer.add_event(
            event_type="adapter_format_end",
            component="dspy_adapter",
            data=format_result,
            status=status,
        )

    def on_adapter_parse_start(self, call_id, inputs):
        """Called when adapter starts parsing LM output."""
        parse_info = {
            "call_id": call_id,
            "raw_output_size": len(str(inputs)),
            "timestamp": datetime.now().isoformat(),
        }

        self.tracer.add_event(
            event_type="adapter_parse_start",
            component="dspy_adapter",
            data=parse_info,
            status="info",
        )

    def on_adapter_parse_end(self, call_id, outputs, exception):
        """Called when adapter completes parsing LM output."""
        if exception:
            parse_result = {
                "error": str(exception),
                "call_id": call_id,
                "status": "failed",
            }
            status = "error"
        else:
            parse_result = {
                "parsed_fields": list(outputs.keys())
                if isinstance(outputs, dict)
                else [],
                "call_id": call_id,
                "status": "success",
            }
            status = "success"

        self.tracer.add_event(
            event_type="adapter_parse_end",
            component="dspy_adapter",
            data=parse_result,
            status=status,
        )

    def on_tool_start(self, call_id, inputs):
        """Called when tool execution starts."""
        tool_info = {
            "call_id": call_id,
            "tool_inputs": self._truncate_data(str(inputs), 100),
            "timestamp": datetime.now().isoformat(),
        }

        # Add to tracer
        self.tracer.add_event(
            event_type="tool_execution_start",
            component="tool_system",
            data=tool_info,
            status="info",
        )

        # Add to memory tracking if available
        if self.memory:
            self.memory.add_interaction_event(
                event_type="tool_execution_start",
                description="Tool execution started",
                data=tool_info,
            )

        self.call_stack.append(
            {"call_id": call_id, "start_time": datetime.now(), "type": "tool_call"}
        )

    def on_tool_end(self, call_id, outputs, exception):
        """Called when tool execution completes."""
        # Find corresponding start event
        start_event = None
        for i, event in enumerate(self.call_stack):
            if event["call_id"] == call_id and event["type"] == "tool_call":
                start_event = self.call_stack.pop(i)
                break

        # Calculate duration
        duration_ms = None
        if start_event:
            duration = datetime.now() - start_event["start_time"]
            duration_ms = duration.total_seconds() * 1000

        if exception:
            tool_result = {
                "error": str(exception),
                "error_type": type(exception).__name__,
                "call_id": call_id,
                "duration_ms": duration_ms,
                "status": "failed",
            }
            status = "error"
        else:
            tool_result = {
                "tool_outputs": self._truncate_data(str(outputs), 100),
                "call_id": call_id,
                "duration_ms": duration_ms,
                "status": "success",
            }
            status = "success"

        # Add to tracer
        self.tracer.add_event(
            event_type="tool_execution_end",
            component="tool_system",
            data=tool_result,
            status=status,
        )

        # Add to memory tracking if available
        if self.memory:
            self.memory.add_interaction_event(
                event_type="tool_execution_end",
                description="Tool execution completed",
                data=tool_result,
            )

    def on_evaluate_start(self, call_id, inputs):
        """Called when evaluation starts."""
        eval_info = {
            "call_id": call_id,
            "eval_inputs": self._truncate_data(str(inputs), 100),
            "timestamp": datetime.now().isoformat(),
        }

        self.tracer.add_event(
            event_type="evaluation_start",
            component="evaluation_system",
            data=eval_info,
            status="info",
        )

        self.call_stack.append(
            {"call_id": call_id, "start_time": datetime.now(), "type": "evaluation"}
        )

    def on_evaluate_end(self, call_id, outputs, exception):
        """Called when evaluation completes."""
        # Find corresponding start event
        start_event = None
        for i, event in enumerate(self.call_stack):
            if event["call_id"] == call_id and event["type"] == "evaluation":
                start_event = self.call_stack.pop(i)
                break

        # Calculate duration
        duration_ms = None
        if start_event:
            duration = datetime.now() - start_event["start_time"]
            duration_ms = duration.total_seconds() * 1000

        if exception:
            eval_result = {
                "error": str(exception),
                "call_id": call_id,
                "duration_ms": duration_ms,
                "status": "failed",
            }
            status = "error"
        else:
            eval_result = {
                "eval_results": self._truncate_data(str(outputs), 200),
                "call_id": call_id,
                "duration_ms": duration_ms,
                "status": "success",
            }
            status = "success"

        self.tracer.add_event(
            event_type="evaluation_end",
            component="evaluation_system",
            data=eval_result,
            status=status,
        )

    def _truncate_data(self, data: str, max_length: int) -> str:
        """Truncate data to prevent excessive logging."""
        if len(data) > max_length:
            return data[:max_length] + "..."
        return data

    def _infer_module_type(self, inputs) -> str:
        """Infer the type of DSPy module based on inputs."""
        if isinstance(inputs, dict):
            if "reasoning" in inputs or "rationale" in inputs:
                return "ChainOfThought"
            elif "context" in inputs and "question" in inputs:
                return "RAG"
            elif "query" in inputs:
                return "Predict"
            else:
                return "Unknown"
        return "Simple"

    def get_callback_stats(self) -> Dict[str, Any]:
        """Get statistics about callback activity."""
        return {
            "active_modules": len(self.module_stack),
            "active_calls": len(self.call_stack),
            "tracer_events": len(self.tracer.traces),
            "memory_enabled": self.memory is not None,
        }
