"""
Framework Registry for multi-framework support.

This module provides a central registry of all supported agent frameworks
and their corresponding adapters. The registry allows the SuperOptiX CLI
to dynamically route compilation and optimization requests to the appropriate
framework-specific adapter.

Supported Frameworks:
- DSPy (current, enhanced)
- Microsoft Agent Framework
- OpenAI Agents SDK
- DeepAgent (LangGraph-based)
- CrewAI
- Google ADK
- Pydantic AI
"""

from typing import Any, Dict, List, Type

from ..core.base_component import BaseComponent


class FrameworkAdapter:
    """
    Base class for framework-specific adapters.

    Each adapter is responsible for:
    1. Converting SuperSpec playbooks to framework-specific code
    2. Wrapping framework agents as BaseComponent instances
    3. Extracting optimizable variables for GEPA
    4. Generating deployable code
    """

    framework_name: str = "base"
    requires_async: bool = False

    @classmethod
    def compile_from_playbook(cls, playbook: Dict[str, Any], output_path: str) -> str:
        """
        Compile SuperSpec playbook to framework-specific code.

        Args:
            playbook: Parsed SuperSpec YAML playbook
            output_path: Directory to write generated code

        Returns:
            Path to generated agent file
        """
        raise NotImplementedError(
            f"{cls.__name__} must implement compile_from_playbook()"
        )

    @classmethod
    def create_component(cls, playbook: Dict[str, Any], **kwargs) -> BaseComponent:
        """
        Create a BaseComponent instance from a playbook.

        This method wraps the framework-specific agent in a framework-agnostic
        BaseComponent interface, enabling universal optimization with GEPA.

        Args:
            playbook: Parsed SuperSpec YAML playbook
            **kwargs: Additional configuration

        Returns:
            BaseComponent instance wrapping the framework agent
        """
        raise NotImplementedError(f"{cls.__name__} must implement create_component()")

    @classmethod
    def get_optimizable_variable(cls, playbook: Dict[str, Any]) -> str:
        """
        Extract the optimizable variable from the playbook.

        Different frameworks use different variable names:
        - DSPy: signature instructions
        - Microsoft: instructions
        - OpenAI: instructions
        - DeepAgent: system_prompt
        - CrewAI: role/goal/backstory
        - Google ADK: description

        Args:
            playbook: Parsed SuperSpec YAML playbook

        Returns:
            The optimizable variable (prompt/instructions/etc.)
        """
        raise NotImplementedError(
            f"{cls.__name__} must implement get_optimizable_variable()"
        )


class DSPyFrameworkAdapter(FrameworkAdapter):
    """Adapter for DSPy framework (current implementation)."""

    framework_name = "dspy"
    requires_async = False

    @classmethod
    def compile_from_playbook(cls, playbook: Dict[str, Any], output_path: str) -> str:
        """Compile SuperSpec to DSPy pipeline (existing implementation)."""
        # This will delegate to the existing AgentCompiler
        # We keep the current excellent DSPy workflow unchanged
        from ..compiler.agent_compiler import AgentCompiler

        compiler = AgentCompiler(playbook, output_path)
        return compiler.compile()

    @classmethod
    def create_component(cls, playbook: Dict[str, Any], **kwargs) -> BaseComponent:
        """Create BaseComponent wrapping DSPy agent."""
        # This will be implemented when integrating with universal GEPA
        raise NotImplementedError("DSPy BaseComponent integration pending")

    @classmethod
    def get_optimizable_variable(cls, playbook: Dict[str, Any]) -> str:
        """Extract DSPy signature instructions."""
        return playbook.get("persona", {}).get("instructions", "")


class MicrosoftFrameworkAdapter(FrameworkAdapter):
    """Adapter for Microsoft Agent Framework."""

    framework_name = "microsoft"
    requires_async = True

    @classmethod
    def compile_from_playbook(cls, playbook: Dict[str, Any], output_path: str) -> str:
        """Compile SuperSpec to Microsoft Agent Framework code."""
        from pathlib import Path
        from jinja2 import Environment, FileSystemLoader
        from datetime import datetime

        # Get template
        template_dir = Path(__file__).parent.parent / "templates" / "pipeline"
        env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            if text and text[0].isdigit():
                text = f"field_{text}"
            return text or "field"

        env.filters["to_pascal_case"] = to_pascal_case
        env.filters["to_snake_case"] = to_snake_case

        # Load template
        template = env.get_template("microsoft_agent_pipeline.py.jinja2")

        # Extract agent name from output path (not from playbook metadata!)
        output_file = Path(output_path)
        filename = output_file.stem
        if "_microsoft_pipeline" in filename:
            agent_name = filename.replace("_microsoft_pipeline", "")
        else:
            agent_name = filename.replace("_pipeline", "")

        if not agent_name or agent_name == "pipeline":
            agent_name = playbook.get("metadata", {}).get("name", "agent")
            agent_name = to_snake_case(agent_name)

        # Prepare context
        context = {
            "agent_name": agent_name,
            "metadata": playbook.get("metadata", {}),
            "spec": playbook.get("spec", {}),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Render template
        code = template.render(**context)

        # Write to output path
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(code)

        return str(output_file)

    @classmethod
    def create_component(cls, playbook: Dict[str, Any], **kwargs) -> BaseComponent:
        """Create BaseComponent wrapping Microsoft agent."""
        # This will be used by Universal GEPA optimizer
        # For now, we need to compile and import the generated module
        import importlib.util
        import sys
        from pathlib import Path

        # Compile to temp location
        import tempfile

        temp_dir = Path(tempfile.mkdtemp())

        # Extract agent name from playbook metadata first
        agent_name = playbook.get("metadata", {}).get("name", "agent")

        # Use agent name in temp filename so compile_from_playbook uses correct name
        output_path = temp_dir / f"{agent_name}_microsoft_pipeline.py"
        cls.compile_from_playbook(playbook, str(output_path))

        # Import the generated module
        module_name = agent_name.replace("-", "_")
        spec = importlib.util.spec_from_file_location(module_name, output_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Agent name already extracted above

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            return text or "agent"

        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        agent_name_snake = to_snake_case(agent_name)
        agent_name_pascal = to_pascal_case(agent_name_snake)

        # Get the component class
        component_class = getattr(module, f"{agent_name_pascal}Component")

        # Create and return instance
        return component_class(**kwargs)

    @classmethod
    def get_optimizable_variable(cls, playbook: Dict[str, Any]) -> str:
        """Extract Microsoft agent instructions."""
        persona = playbook.get("spec", {}).get("persona", {})
        return persona.get("instructions", persona.get("role", ""))


class OpenAIFrameworkAdapter(FrameworkAdapter):
    """Adapter for OpenAI Agents SDK."""

    framework_name = "openai"
    requires_async = False

    @classmethod
    def compile_from_playbook(cls, playbook: Dict[str, Any], output_path: str) -> str:
        """Compile SuperSpec to OpenAI Agents SDK code."""
        from pathlib import Path
        from jinja2 import Environment, FileSystemLoader
        from datetime import datetime

        # Get template
        template_dir = Path(__file__).parent.parent / "templates" / "pipeline"
        env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            if text and text[0].isdigit():
                text = f"field_{text}"
            return text or "field"

        env.filters["to_pascal_case"] = to_pascal_case
        env.filters["to_snake_case"] = to_snake_case

        # Load template
        template = env.get_template("openai_pipeline.py.jinja2")

        # Extract agent name from output path (not from playbook metadata!)
        output_file = Path(output_path)
        filename = output_file.stem
        if "_openai_pipeline" in filename:
            agent_name = filename.replace("_openai_pipeline", "")
        else:
            agent_name = filename.replace("_pipeline", "")

        if not agent_name or agent_name == "pipeline":
            agent_name = playbook.get("metadata", {}).get("name", "agent")
            agent_name = to_snake_case(agent_name)

        # Prepare context
        context = {
            "agent_name": agent_name,
            "metadata": playbook.get("metadata", {}),
            "spec": playbook.get("spec", {}),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Render template
        code = template.render(**context)

        # Write to output path
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(code)

        return str(output_file)

    @classmethod
    def create_component(cls, playbook: Dict[str, Any], **kwargs) -> BaseComponent:
        """Create BaseComponent wrapping OpenAI agent."""
        # This will be used by Universal GEPA optimizer
        import importlib.util
        import sys
        from pathlib import Path

        # Compile to temp location
        import tempfile

        temp_dir = Path(tempfile.mkdtemp())

        # Extract agent name from playbook metadata first
        agent_name = playbook.get("metadata", {}).get("name", "agent")

        # Use agent name in temp filename so compile_from_playbook uses correct name
        output_path = temp_dir / f"{agent_name}_openai_pipeline.py"
        cls.compile_from_playbook(playbook, str(output_path))

        # Import the generated module
        module_name = agent_name.replace("-", "_")
        spec = importlib.util.spec_from_file_location(module_name, output_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Agent name already extracted above

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            return text or "agent"

        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        agent_name_snake = to_snake_case(agent_name)
        agent_name_pascal = to_pascal_case(agent_name_snake)

        # Get the component class
        component_class = getattr(module, f"{agent_name_pascal}Component")

        # Create and return instance
        return component_class(**kwargs)

    @classmethod
    def get_optimizable_variable(cls, playbook: Dict[str, Any]) -> str:
        """Extract OpenAI agent instructions."""
        persona = playbook.get("spec", {}).get("persona", {})
        return persona.get("instructions", persona.get("role", ""))


class DeepAgentsFrameworkAdapter(FrameworkAdapter):
    """Adapter for DeepAgents (LangGraph-based)."""

    framework_name = "deepagents"
    requires_async = True

    @classmethod
    def compile_from_playbook(cls, playbook: Dict[str, Any], output_path: str) -> str:
        """Compile SuperSpec to DeepAgent code."""
        from pathlib import Path
        from jinja2 import Environment, FileSystemLoader
        from datetime import datetime

        # Get template
        template_dir = Path(__file__).parent.parent / "templates" / "pipeline"
        env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            if text and text[0].isdigit():
                text = f"field_{text}"
            return text or "field"

        env.filters["to_pascal_case"] = to_pascal_case
        env.filters["to_snake_case"] = to_snake_case

        # Load template
        template = env.get_template("deepagents_pipeline.py.jinja2")

        # Extract agent name from output path (not from playbook metadata!)
        # This ensures the class name matches what the runner expects
        # e.g., "code_reviewer_deepagents_pipeline.py" → "code_reviewer"
        output_file = Path(output_path)
        filename = output_file.stem  # e.g., "code_reviewer_deepagents_pipeline"
        # Remove framework suffix if present
        if "_deepagents_pipeline" in filename:
            agent_name = filename.replace("_deepagents_pipeline", "")
        else:
            agent_name = filename.replace("_pipeline", "")

        # Fallback to playbook metadata if we can't extract from filename
        if not agent_name or agent_name == "pipeline":
            agent_name = playbook.get("metadata", {}).get("name", "agent")
            agent_name = to_snake_case(agent_name)

        # Prepare context
        context = {
            "agent_name": agent_name,
            "metadata": playbook.get("metadata", {}),
            "spec": playbook.get("spec", {}),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Render template
        code = template.render(**context)

        # Write to output path
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(code)

        return str(output_file)

    @classmethod
    def create_component(cls, playbook: Dict[str, Any], **kwargs) -> BaseComponent:
        """Create BaseComponent wrapping DeepAgents agent."""
        import importlib.util
        import sys
        from pathlib import Path

        # Compile to temp location
        import tempfile

        temp_dir = Path(tempfile.mkdtemp())

        # Extract agent name from playbook metadata first
        agent_name = playbook.get("metadata", {}).get("name", "agent")

        # Use agent name in temp filename so compile_from_playbook uses correct name
        output_path = temp_dir / f"{agent_name}_deepagents_pipeline.py"
        cls.compile_from_playbook(playbook, str(output_path))

        # Import the generated module
        module_name = agent_name.replace("-", "_")
        spec = importlib.util.spec_from_file_location(module_name, output_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Agent name already extracted above

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            return text or "agent"

        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        agent_name_snake = to_snake_case(agent_name)
        agent_name_pascal = to_pascal_case(agent_name_snake)

        # Get the component class
        component_class = getattr(module, f"{agent_name_pascal}Component")

        # Create and return instance
        return component_class(**kwargs)

    @classmethod
    def get_optimizable_variable(cls, playbook: Dict[str, Any]) -> str:
        """Extract DeepAgent system_prompt."""
        persona = playbook.get("spec", {}).get("persona", {})
        return persona.get("instructions", persona.get("role", ""))


class CrewAIFrameworkAdapter(FrameworkAdapter):
    """Adapter for CrewAI framework."""

    framework_name = "crewai"
    requires_async = False

    @classmethod
    def compile_from_playbook(cls, playbook: Dict[str, Any], output_path: str) -> str:
        """Compile SuperSpec to CrewAI code."""
        from pathlib import Path
        from jinja2 import Environment, FileSystemLoader
        from datetime import datetime

        # Get template
        template_dir = Path(__file__).parent.parent / "templates" / "pipeline"
        env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            if text and text[0].isdigit():
                text = f"field_{text}"
            return text or "field"

        env.filters["to_pascal_case"] = to_pascal_case
        env.filters["to_snake_case"] = to_snake_case

        # Load template
        template = env.get_template("crewai_pipeline.py.jinja2")

        # Extract agent name from output path (not from playbook metadata!)
        output_file = Path(output_path)
        filename = output_file.stem
        if "_crewai_pipeline" in filename:
            agent_name = filename.replace("_crewai_pipeline", "")
        else:
            agent_name = filename.replace("_pipeline", "")

        if not agent_name or agent_name == "pipeline":
            agent_name = playbook.get("metadata", {}).get("name", "agent")
            agent_name = to_snake_case(agent_name)

        # Prepare context
        context = {
            "agent_name": agent_name,
            "metadata": playbook.get("metadata", {}),
            "spec": playbook.get("spec", {}),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Render template
        code = template.render(**context)

        # Write to output path
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(code)

        return str(output_file)

    @classmethod
    def create_component(cls, playbook: Dict[str, Any], **kwargs) -> BaseComponent:
        """Create BaseComponent wrapping CrewAI agent."""
        # This will be used by Universal GEPA optimizer
        import importlib.util
        import sys
        from pathlib import Path

        # Compile to temp location
        import tempfile

        temp_dir = Path(tempfile.mkdtemp())

        # Extract agent name from playbook metadata first
        agent_name = playbook.get("metadata", {}).get("name", "agent")

        # Use agent name in temp filename so compile_from_playbook uses correct name
        output_path = temp_dir / f"{agent_name}_crewai_pipeline.py"
        cls.compile_from_playbook(playbook, str(output_path))

        # Import the generated module
        module_name = agent_name.replace("-", "_")
        spec = importlib.util.spec_from_file_location(module_name, output_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Agent name already extracted above

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            return text or "agent"

        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        agent_name_snake = to_snake_case(agent_name)
        agent_name_pascal = to_pascal_case(agent_name_snake)

        # Get the component class
        component_class = getattr(module, f"{agent_name_pascal}Component")

        # Create and return instance
        return component_class(**kwargs)

    @classmethod
    def get_optimizable_variable(cls, playbook: Dict[str, Any]) -> str:
        """Extract CrewAI role/goal/backstory."""
        persona = playbook.get("spec", {}).get("persona", {})
        # CrewAI uses role + goal + backstory pattern
        role = persona.get("role", "")
        goal = persona.get("goal", "")
        backstory = persona.get("backstory", "")
        return f"Role: {role}\nGoal: {goal}\nBackstory: {backstory}"


class GoogleADKFrameworkAdapter(FrameworkAdapter):
    """Adapter for Google Agent Development Kit (ADK)."""

    framework_name = "google-adk"
    requires_async = False

    @classmethod
    def compile_from_playbook(cls, playbook: Dict[str, Any], output_path: str) -> str:
        """Compile SuperSpec to Google ADK code."""
        from pathlib import Path
        from jinja2 import Environment, FileSystemLoader
        from datetime import datetime

        # Get template
        template_dir = Path(__file__).parent.parent / "templates" / "pipeline"
        env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            if text and text[0].isdigit():
                text = f"field_{text}"
            return text or "field"

        env.filters["to_pascal_case"] = to_pascal_case
        env.filters["to_snake_case"] = to_snake_case

        # Load template
        template = env.get_template("google_adk_pipeline.py.jinja2")

        # Extract agent name from output path (not from playbook metadata!)
        output_file = Path(output_path)
        filename = output_file.stem
        if "_google_adk_pipeline" in filename:
            agent_name = filename.replace("_google_adk_pipeline", "")
        else:
            agent_name = filename.replace("_pipeline", "")

        if not agent_name or agent_name == "pipeline":
            agent_name = playbook.get("metadata", {}).get("name", "agent")
            agent_name = to_snake_case(agent_name)

        # Prepare context
        context = {
            "agent_name": agent_name,
            "metadata": playbook.get("metadata", {}),
            "spec": playbook.get("spec", {}),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Render template
        code = template.render(**context)

        # Write to output path
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(code)

        return str(output_file)

    @classmethod
    def create_component(cls, playbook: Dict[str, Any], **kwargs) -> BaseComponent:
        """Create BaseComponent wrapping Google ADK agent."""
        # This will be used by Universal GEPA optimizer
        import importlib.util
        import sys
        from pathlib import Path

        # Compile to temp location
        import tempfile

        temp_dir = Path(tempfile.mkdtemp())

        # Extract agent name from playbook metadata first
        agent_name = playbook.get("metadata", {}).get("name", "agent")

        # Use agent name in temp filename so compile_from_playbook uses correct name
        output_path = temp_dir / f"{agent_name}_google_adk_pipeline.py"
        cls.compile_from_playbook(playbook, str(output_path))

        # Import the generated module
        module_name = agent_name.replace("-", "_")
        spec = importlib.util.spec_from_file_location(module_name, output_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Agent name already extracted above

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            return text or "agent"

        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        agent_name_snake = to_snake_case(agent_name)
        agent_name_pascal = to_pascal_case(agent_name_snake)

        # Get the component class
        component_class = getattr(module, f"{agent_name_pascal}Component")

        # Create and return instance
        return component_class(**kwargs)

    @classmethod
    def get_optimizable_variable(cls, playbook: Dict[str, Any]) -> str:
        """Extract Google ADK instruction."""
        persona = playbook.get("spec", {}).get("persona", {})
        return persona.get("instructions", persona.get("role", ""))


class PydanticAIFrameworkAdapter(FrameworkAdapter):
    """Adapter for Pydantic AI framework."""

    framework_name = "pydantic-ai"
    requires_async = True  # Pydantic AI uses async agents

    @classmethod
    def compile_from_playbook(cls, playbook: Dict[str, Any], output_path: str) -> str:
        """Compile SuperSpec to Pydantic AI code."""
        from pathlib import Path
        from jinja2 import Environment, FileSystemLoader
        from datetime import datetime

        # Get template
        template_dir = Path(__file__).parent.parent / "templates" / "pipeline"
        env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            if text and text[0].isdigit():
                text = f"field_{text}"
            return text or "field"

        env.filters["to_pascal_case"] = to_pascal_case
        env.filters["to_snake_case"] = to_snake_case

        # Load template
        template = env.get_template("pydantic_ai_pipeline.py.jinja2")

        # Extract agent name from output path (not from playbook metadata!)
        output_file = Path(output_path)
        filename = output_file.stem
        if "_pydantic_ai_pipeline" in filename:
            agent_name = filename.replace("_pydantic_ai_pipeline", "")
        else:
            agent_name = filename.replace("_pipeline", "")

        if not agent_name or agent_name == "pipeline":
            # Get from metadata and convert to valid identifier
            metadata_name = playbook.get("metadata", {}).get("name", "agent")
            agent_name = to_snake_case(metadata_name)
        else:
            # Ensure agent_name is valid identifier (no spaces, special chars)
            agent_name = to_snake_case(agent_name)

        # Prepare context
        context = {
            "agent_name": agent_name,
            "metadata": playbook.get("metadata", {}),
            "spec": playbook.get("spec", {}),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Render template
        code = template.render(**context)

        # Write to output path
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(code)

        return str(output_file)

    @classmethod
    def create_component(cls, playbook: Dict[str, Any], **kwargs) -> BaseComponent:
        """Create BaseComponent wrapping Pydantic AI agent."""
        # This will be used by Universal GEPA optimizer
        import importlib.util
        import sys
        from pathlib import Path

        # Compile to temp location
        import tempfile

        temp_dir = Path(tempfile.mkdtemp())

        # Extract agent name from playbook metadata first
        agent_name = playbook.get("metadata", {}).get("name", "agent")

        # Use agent name in temp filename so compile_from_playbook uses correct name
        output_path = temp_dir / f"{agent_name}_pydantic_ai_pipeline.py"
        cls.compile_from_playbook(playbook, str(output_path))

        # Import the generated module
        module_name = agent_name.replace("-", "_")
        spec = importlib.util.spec_from_file_location(module_name, output_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Agent name already extracted above

        def to_snake_case(text: str) -> str:
            import re

            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            return text or "agent"

        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        agent_name_snake = to_snake_case(agent_name)
        agent_name_pascal = to_pascal_case(agent_name_snake)

        # Get the component class
        component_class = getattr(module, f"{agent_name_pascal}Component")

        # Extract model config from playbook for component initialization
        spec = playbook.get("spec", {})
        model_config = {}
        if "language_model" in spec:
            lm = spec["language_model"]
            model_str = lm.get("model", "llama3.1:8b")
            provider = lm.get("provider", "ollama").lower()
            
            # Ensure model has ollama: prefix if provider is ollama or model lacks prefix
            known_providers = ["ollama", "openai", "anthropic", "google", "bedrock", "azure", "cohere", "mistral", "deepseek", "groq", "together", "fireworks", "litellm", "gateway"]
            has_provider_prefix = any(model_str.startswith(f"{p}:") for p in known_providers)
            
            if not has_provider_prefix and (provider == "ollama" or ":" in model_str):
                # Add ollama: prefix if it looks like an Ollama model
                ollama_indicators = [":8b", ":7b", ":13b", ":70b", "llama", "mistral", "codellama", "phi", "gemma", "qwen"]
                if any(indicator in model_str.lower() for indicator in ollama_indicators):
                    model_str = f"ollama:{model_str}"
            
            model_config = {
                "model": model_str,
                "provider": provider,
                "api_base": lm.get("api_base"),
                "temperature": lm.get("temperature"),
            }

        # Extract spec for MCP configuration access
        spec_data = playbook.get("spec", {})
        
        # Create and return instance with model_config and spec
        # Note: Component will load spec from playbook_path if provided, but we also pass it
        # for cases where playbook_path might not be available (temp compilation)
        return component_class(
            model_config=model_config,
            spec_data=spec_data,  # Pass spec directly for MCP config access
            **kwargs
        )

    @classmethod
    def get_optimizable_variable(cls, playbook: Dict[str, Any]) -> str:
        """Extract Pydantic AI agent instructions."""
        persona = playbook.get("spec", {}).get("persona", {})
        # Pydantic AI uses 'instructions' as the optimizable variable
        instructions = persona.get("instructions", "")
        if not instructions:
            # Build from role/goal/backstory if instructions not explicitly set
            parts = []
            if persona.get("role"):
                parts.append(persona["role"])
            if persona.get("goal"):
                parts.append(f"\nGoal: {persona['goal']}")
            if persona.get("backstory"):
                parts.append(f"\nBackstory: {persona['backstory']}")
            instructions = "\n".join(parts) if parts else "You are a helpful AI assistant."
        return instructions


class ClaudeAgentSDKFrameworkAdapter(FrameworkAdapter):
    """Adapter for Claude Agent SDK framework.

    Claude Agent SDK provides powerful agentic capabilities with:
    - In-process MCP tool servers
    - Bidirectional sessions with ClaudeSDKClient
    - Hook system for tool permission and control
    - Async-first architecture

    Optimizable Variable: system_prompt (the agent's system instructions)
    """

    framework_name = "claude-sdk"
    requires_async = True  # Claude Agent SDK is async-first

    @classmethod
    def compile_from_playbook(cls, playbook: Dict[str, Any], output_path: str) -> str:
        """Compile SuperSpec to Claude Agent SDK code."""
        from pathlib import Path
        from jinja2 import Environment, FileSystemLoader
        from datetime import datetime

        # Get template
        template_dir = Path(__file__).parent.parent / "templates" / "pipeline"
        env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        def to_snake_case(text: str) -> str:
            import re
            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            if text and text[0].isdigit():
                text = f"field_{text}"
            return text or "field"

        env.filters["to_pascal_case"] = to_pascal_case
        env.filters["to_snake_case"] = to_snake_case

        # Load template
        template = env.get_template("claude_sdk_pipeline.py.jinja2")

        # Extract agent name from output path
        output_file = Path(output_path)
        filename = output_file.stem
        if "_claude_sdk_pipeline" in filename:
            agent_name = filename.replace("_claude_sdk_pipeline", "")
        else:
            agent_name = filename.replace("_pipeline", "")

        if not agent_name or agent_name == "pipeline":
            metadata_name = playbook.get("metadata", {}).get("name", "agent")
            agent_name = to_snake_case(metadata_name)
        else:
            agent_name = to_snake_case(agent_name)

        # Prepare context
        context = {
            "agent_name": agent_name,
            "metadata": playbook.get("metadata", {}),
            "spec": playbook.get("spec", {}),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Render template
        code = template.render(**context)

        # Write to output path
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(code)

        return str(output_file)

    @classmethod
    def create_component(cls, playbook: Dict[str, Any], **kwargs) -> BaseComponent:
        """Create BaseComponent wrapping Claude Agent SDK agent."""
        import importlib.util
        import sys
        from pathlib import Path
        import tempfile

        # Compile to temp location
        temp_dir = Path(tempfile.mkdtemp())
        agent_name = playbook.get("metadata", {}).get("name", "agent")
        output_path = temp_dir / f"{agent_name}_claude_sdk_pipeline.py"
        cls.compile_from_playbook(playbook, str(output_path))

        # Import the generated module
        module_name = agent_name.replace("-", "_")
        spec = importlib.util.spec_from_file_location(module_name, output_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Convert names
        def to_snake_case(text: str) -> str:
            import re
            text = text.strip()
            text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
            text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
            text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
            text = text.lower()
            text = re.sub(r"_+", "_", text)
            text = text.strip("_")
            return text or "agent"

        def to_pascal_case(text: str) -> str:
            return "".join(word.capitalize() for word in text.split("_"))

        agent_name_snake = to_snake_case(agent_name)
        agent_name_pascal = to_pascal_case(agent_name_snake)

        # Get the component class
        component_class = getattr(module, f"{agent_name_pascal}Component")

        # Extract model config from playbook
        spec_data = playbook.get("spec", {})
        model_config = {}
        if "language_model" in spec_data:
            lm = spec_data["language_model"]
            model_config = {
                "model": lm.get("model", "claude-sonnet-4-5"),
                "provider": lm.get("provider", "anthropic"),
            }

        return component_class(
            model_config=model_config,
            spec_data=spec_data,
            **kwargs
        )

    @classmethod
    def get_optimizable_variable(cls, playbook: Dict[str, Any]) -> str:
        """Extract Claude SDK system_prompt as the optimizable variable."""
        persona = playbook.get("spec", {}).get("persona", {})
        # Use instructions if available, otherwise build from role/goal/backstory
        instructions = persona.get("instructions", "")
        if not instructions:
            parts = []
            if persona.get("role"):
                parts.append(persona["role"])
            if persona.get("goal"):
                parts.append(f"\nGoal: {persona['goal']}")
            if persona.get("backstory"):
                parts.append(f"\nBackstory: {persona['backstory']}")
            instructions = "\n".join(parts) if parts else "You are a helpful AI assistant."
        return instructions


class FrameworkRegistry:
    """
    Central registry of all supported agent frameworks.

    This registry provides:
    1. Discovery: List all available frameworks
    2. Routing: Get the appropriate adapter for a framework
    3. Validation: Check if a framework is supported
    4. Metadata: Framework capabilities and requirements
    """

    _adapters: Dict[str, Type[FrameworkAdapter]] = {
        "dspy": DSPyFrameworkAdapter,
        "microsoft": MicrosoftFrameworkAdapter,
        "openai": OpenAIFrameworkAdapter,
        "deepagents": DeepAgentsFrameworkAdapter,
        "crewai": CrewAIFrameworkAdapter,
        "google-adk": GoogleADKFrameworkAdapter,
        "pydantic-ai": PydanticAIFrameworkAdapter,
        "claude-sdk": ClaudeAgentSDKFrameworkAdapter,
    }

    @classmethod
    def get_adapter(cls, framework: str) -> Type[FrameworkAdapter]:
        """
        Get the adapter class for the specified framework.

        Args:
            framework: Framework name (e.g., "dspy", "crewai", "openai")

        Returns:
            FrameworkAdapter subclass for the framework

        Raises:
            ValueError: If framework is not supported
        """
        framework = framework.lower()
        if framework not in cls._adapters:
            available = ", ".join(cls.list_frameworks())
            raise ValueError(
                f"Unsupported framework: '{framework}'. Available: {available}"
            )
        return cls._adapters[framework]

    @classmethod
    def list_frameworks(cls) -> List[str]:
        """
        List all supported framework names.

        Returns:
            List of framework names
        """
        return list(cls._adapters.keys())

    @classmethod
    def is_supported(cls, framework: str) -> bool:
        """
        Check if a framework is supported.

        Args:
            framework: Framework name to check

        Returns:
            True if framework is supported
        """
        return framework.lower() in cls._adapters

    @classmethod
    def get_framework_info(cls, framework: str) -> Dict[str, Any]:
        """
        Get metadata about a framework.

        Args:
            framework: Framework name

        Returns:
            Dict with framework metadata (name, async requirement, etc.)
        """
        adapter = cls.get_adapter(framework)
        return {
            "name": adapter.framework_name,
            "requires_async": adapter.requires_async,
            "implemented": adapter.compile_from_playbook
            != FrameworkAdapter.compile_from_playbook,
        }

    @classmethod
    def compile_agent(
        cls, framework: str, playbook: Dict[str, Any], output_path: str
    ) -> str:
        """
        Compile an agent playbook using the specified framework.

        This is the main entry point for multi-framework compilation.

        Args:
            framework: Target framework name
            playbook: Parsed SuperSpec YAML playbook
            output_path: Directory to write generated code

        Returns:
            Path to generated agent file
        """
        adapter = cls.get_adapter(framework)
        return adapter.compile_from_playbook(playbook, output_path)

    @classmethod
    def create_component(
        cls, framework: str, playbook: Dict[str, Any], **kwargs
    ) -> BaseComponent:
        """
        Create a BaseComponent from a playbook using the specified framework.

        This is used by the universal GEPA optimizer.

        Args:
            framework: Target framework name
            playbook: Parsed SuperSpec YAML playbook
            **kwargs: Additional configuration

        Returns:
            BaseComponent wrapping the framework agent
        """
        adapter = cls.get_adapter(framework)
        return adapter.create_component(playbook, **kwargs)

    @classmethod
    def register_adapter(cls, framework: str, adapter: Type[FrameworkAdapter]) -> None:
        """
        Register a custom framework adapter.

        This allows users to add support for additional frameworks.

        Args:
            framework: Framework name
            adapter: FrameworkAdapter subclass
        """
        cls._adapters[framework.lower()] = adapter
