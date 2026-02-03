"""
OpenAI Agents SDK adapter shim for Optimas integration within SuperOptiX.

Provides `create_component_from_openai` to wrap an OpenAI-backed callable as
an Optimas BaseComponent without introducing a hard dependency on Optimas
package structure.
"""

from __future__ import annotations

from typing import List, Any, Dict, Callable

try:
    from optimas.arch.base import BaseComponent
    from optimas.adapt.utils import format_input_fields
except Exception as e:
    raise ImportError(
        "Optimas must be installed to use optimas-openai target.\nInstall: pip install optimas-ai"
    ) from e


def create_component_from_openai(
    agent_callable: Callable[..., Dict[str, Any]],
    input_fields: List[str],
    output_fields: List[str],
    description: str = "OpenAI Agent component",
    initial_prompt: str = "",
) -> BaseComponent:
    class OpenAIModule(BaseComponent):
        def __init__(self):
            super().__init__(
                description=description,
                input_fields=input_fields,
                output_fields=output_fields,
                variable=initial_prompt,
            )
            self._callable = agent_callable

        def forward(self, **inputs) -> dict:
            prompt_str = format_input_fields(**inputs)
            result = self._callable(
                **inputs, prompt=prompt_str, _system_prompt=self.variable
            )
            if not isinstance(result, dict):
                raise ValueError("OpenAI agent callable must return a dict of outputs")
            # Adapt generic 'response' to the component's declared outputs
            mapped: Dict[str, Any] = {}
            for k in self.output_fields:
                if k in result:
                    mapped[k] = result.get(k)
                elif "response" in result and len(self.output_fields) == 1:
                    mapped[k] = result.get("response")
                else:
                    mapped[k] = None
            return mapped

    return OpenAIModule()
