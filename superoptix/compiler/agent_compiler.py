import re
import os
import json
from pathlib import Path
from typing import Any, Dict

import yaml
from jinja2 import Environment, FileSystemLoader
from rich.console import Console

console = Console()


def clean_filter(text):
    """A Jinja2 filter to clean up multiline strings for docstrings."""
    return " ".join(text.strip().split())


def to_pascal_case(text: str) -> str:
    """
    Converts snake_case to PascalCase, preserving compound words.

    Examples:
        research_agent_deepagents -> ResearchAgentDeepAgents
        sentiment_analyzer -> SentimentAnalyzer
    """
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", str(text or ""))
    words = [w for w in normalized.split("_") if w]
    pascal_words = []

    for word in words:
        # Preserve known compound words/frameworks
        if word.lower() in ["deepagents", "crewai", "openai"]:
            # Keep compound words capitalized properly
            if word.lower() == "deepagents":
                pascal_words.append("DeepAgents")
            elif word.lower() == "crewai":
                pascal_words.append("CrewAI")
            elif word.lower() == "openai":
                pascal_words.append("OpenAI")
            else:
                pascal_words.append(word.capitalize())
        else:
            pascal_words.append(word.capitalize())

    return "".join(pascal_words)


def to_snake_case(text: str) -> str:
    """Converts any text to snake_case for Python compatibility."""
    if not text:
        return text

    # First, strip all whitespace from beginning and end
    text = text.strip()

    # First, handle camelCase and PascalCase
    text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
    text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)

    # Replace spaces, hyphens, and other non-alphanumeric chars with underscores
    text = re.sub(r"[^a-zA-Z0-9_]", "_", text)

    # Convert to lowercase
    text = text.lower()

    # Remove multiple consecutive underscores
    text = re.sub(r"_+", "_", text)

    # Remove leading/trailing underscores
    text = text.strip("_")

    # Ensure it starts with a letter or underscore (Python identifier rules)
    if text and text[0].isdigit():
        text = f"field_{text}"

    return text or "field"


def convert_names_to_snake_case(data: Any) -> Any:
    """Recursively convert all 'name' fields in the data structure to snake_case."""
    if isinstance(data, dict):
        converted = {}
        for key, value in data.items():
            if key == "name" and isinstance(value, str):
                # Convert the name field to snake_case
                converted[key] = to_snake_case(value)
            else:
                # Recursively process nested structures
                converted[key] = convert_names_to_snake_case(value)
        return converted
    elif isinstance(data, list):
        return [convert_names_to_snake_case(item) for item in data]
    else:
        return data


def _normalize_persona(persona: Any) -> Dict[str, Any]:
    """Normalize persona to a consistent dict shape used by templates."""
    default_persona = {
        "name": "",
        "role": "AI Assistant",
        "instructions": "",
        "goal": "",
        "backstory": "",
        "traits": [],
    }

    if isinstance(persona, str):
        normalized = dict(default_persona)
        normalized["instructions"] = persona.strip()
        return normalized

    if not isinstance(persona, dict):
        return dict(default_persona)

    normalized = dict(default_persona)
    normalized["name"] = str(persona.get("name", "") or "").strip()
    normalized["role"] = str(persona.get("role", "") or "AI Assistant").strip()

    instructions = (
        persona.get("instructions")
        or persona.get("instruction")
        or persona.get("personality")
        or ""
    )
    normalized["instructions"] = str(instructions).strip()
    normalized["goal"] = str(persona.get("goal", "") or "").strip()
    normalized["backstory"] = str(persona.get("backstory", "") or "").strip()

    traits = persona.get("traits", [])
    if isinstance(traits, str):
        traits = [part.strip() for part in traits.split(",") if part.strip()]
    elif not isinstance(traits, list):
        traits = []
    normalized["traits"] = [
        str(trait).strip() for trait in traits if str(trait).strip()
    ]

    return normalized


class AgentCompiler:
    """Compiles agent playbook into a framework-specific pipeline."""

    def __init__(self):
        self.project_root = self._find_project_root()
        self.template_env = Environment(
            loader=FileSystemLoader(
                Path(__file__).parent.parent / "templates" / "pipeline"
            ),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.template_env.filters["clean"] = clean_filter
        self.template_env.filters["to_pascal_case"] = to_pascal_case
        self.template_env.filters["to_snake_case"] = to_snake_case

        # Minimal DSPy template - Signature + Module + run path only (PyTorch-like)
        self.minimal_template = "dspy_pipeline_minimal.py.jinja2"

        # Protocol-first template (Agenspy approach) - automatic tool discovery via protocols
        # This template uses protocol-first approach for automatic tool discovery from MCP servers
        self.agenspy_template = "dspy_pipeline_agenspy.py.jinja2"

        # Optimas templates (target-specific)
        self.optimas_templates = {
            "optimas-dspy": "optimas_dspy_pipeline.py.jinja2",
            "optimas-crewai": "optimas_crewai_pipeline.py.jinja2",
            "optimas-autogen": "optimas_autogen_pipeline.py.jinja2",
            "optimas-openai": "optimas_openai_pipeline.py.jinja2",
        }

    def _find_project_root(self) -> Path:
        """Find project root by looking for .super file."""
        current_dir = Path.cwd()
        while current_dir != current_dir.parent:
            if (current_dir / ".super").exists():
                return current_dir
            current_dir = current_dir.parent
        raise FileNotFoundError(
            "Could not find .super file. Please run 'super init <project_name>' first."
        )

    def _load_playbook_and_get_context(
        self, agent_name: str, tier_level: str = None
    ) -> Dict[str, Any]:
        """Loads playbook and creates a context dictionary for templates."""
        with open(self.project_root / ".super") as f:
            system_name = yaml.safe_load(f).get("project")

        playbook_path = next(
            (self.project_root / system_name / "agents").rglob(
                f"**/{agent_name}_playbook.yaml"
            ),
            None,
        )

        if not playbook_path:
            # Fallback to searching the source agents directory
            package_root = Path(__file__).parent.parent.parent
            playbook_path = next(
                package_root.rglob(f"**/agents/**/{agent_name}_playbook.yaml"), None
            )
            if not playbook_path:
                raise FileNotFoundError(f"Playbook for agent '{agent_name}' not found.")

        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)

        # Convert all name fields to snake_case for DSPy compatibility
        playbook_snake_case = convert_names_to_snake_case(playbook)

        console.print(
            "[dim]🐍 Converted field names to snake_case for DSPy compatibility[/]"
        )

        # Tierless OSS pipeline model: all capabilities are controlled by SuperSpec flags.
        effective_tier = "unified"

        spec = playbook_snake_case.get("spec", {})
        self._apply_dspy_superspec_overrides(spec)
        spec["persona"] = _normalize_persona(spec.get("persona", {}))

        # Resolve signature fields from SuperSpec first, then fallback to first task.
        # This keeps generated DSPy signatures aligned with the richer schema users define.
        spec["input_fields"], spec["output_fields"] = self._resolve_signature_fields(
            spec
        )

        return {
            "metadata": playbook_snake_case.get("metadata", {}),
            "spec": spec,
            "agent_name": to_snake_case(agent_name),
            "tier_level": effective_tier,
        }

    def _map_dspy_field_type(self, raw_type: Any) -> str:
        """Map SuperSpec field types to Python/DSPy annotations (including generics)."""
        field_type = str(raw_type or "str").strip()
        if not field_type:
            return "str"

        # Support generic style declarations like list[str], dict[str, int], typing.List[str].
        generic = self._parse_generic_type(field_type)
        if generic:
            return generic

        primitive = field_type.lower()
        primitive_map = {
            "string": "str",
            "text": "str",
            "str": "str",
            "int": "int",
            "integer": "int",
            "float": "float",
            "number": "float",
            "double": "float",
            "decimal": "float",
            "bool": "bool",
            "boolean": "bool",
            "list": "list",
            "array": "list",
            "dict": "dict",
            "object": "dict",
            "json": "dict",
            "map": "dict",
            "any": "Any",
        }
        return primitive_map.get(primitive, "str")

    def _split_generic_args(self, args: str) -> list[str]:
        """Split generic args while preserving nested brackets."""
        parts: list[str] = []
        current: list[str] = []
        depth = 0
        for ch in args:
            if ch == "[":
                depth += 1
                current.append(ch)
                continue
            if ch == "]":
                depth -= 1
                current.append(ch)
                continue
            if ch == "," and depth == 0:
                token = "".join(current).strip()
                if token:
                    parts.append(token)
                current = []
                continue
            current.append(ch)

        token = "".join(current).strip()
        if token:
            parts.append(token)
        return parts

    def _parse_generic_type(self, raw_type: str) -> str | None:
        """Parse generic type strings into canonical Python annotations."""
        match = re.match(r"^\s*([A-Za-z_][\w\.]*)\s*\[(.+)\]\s*$", raw_type)
        if not match:
            return None

        base_raw, args_raw = match.group(1), match.group(2)
        base = base_raw.split(".")[-1].lower()
        args = self._split_generic_args(args_raw)
        parsed_args = [self._map_dspy_field_type(arg) for arg in args]

        if base in {"list", "sequence", "array"}:
            inner = parsed_args[0] if parsed_args else "str"
            return f"list[{inner}]"
        if base in {"set"}:
            inner = parsed_args[0] if parsed_args else "str"
            return f"set[{inner}]"
        if base in {"tuple"}:
            inner = ", ".join(parsed_args) if parsed_args else "str"
            return f"tuple[{inner}]"
        if base in {"dict", "mapping", "map", "object"}:
            if len(parsed_args) >= 2:
                return f"dict[{parsed_args[0]}, {parsed_args[1]}]"
            if len(parsed_args) == 1:
                return f"dict[str, {parsed_args[0]}]"
            return "dict"
        if base in {"optional"}:
            inner = parsed_args[0] if parsed_args else "str"
            return f"Optional[{inner}]"
        if base in {"union"} and parsed_args:
            return " | ".join(parsed_args)
        if base == "literal" and parsed_args:
            # Keep literal-like semantics simple and avoid extra imports.
            return "str"
        return None

    def _normalize_signature_fields(self, raw_fields: Any) -> list[Dict[str, Any]]:
        """
        Normalize field definitions into a consistent list shape for templates.

        Supports both list- and dict-based field declarations and enriches each field with:
        - dspy_type: mapped Python/DSPy annotation type
        - default_repr: Python-safe literal for optional defaults
        """
        if not raw_fields:
            return []

        if isinstance(raw_fields, dict):
            fields_list = []
            for name, value in raw_fields.items():
                if isinstance(value, dict):
                    field_obj = dict(value)
                    field_obj.setdefault("name", name)
                else:
                    field_obj = {"name": name, "type": value}
                fields_list.append(field_obj)
        elif isinstance(raw_fields, list):
            fields_list = raw_fields
        else:
            return []

        normalized: list[Dict[str, Any]] = []
        for index, field in enumerate(fields_list):
            if not isinstance(field, dict):
                continue

            name = to_snake_case(str(field.get("name") or f"field_{index + 1}"))
            dspy_type = self._map_dspy_field_type(field.get("type"))
            description = str(field.get("description") or "").strip() or "Field"
            enum_values = field.get("enum")
            if isinstance(enum_values, list) and enum_values:
                enum_text = ", ".join(str(v) for v in enum_values)
                description = f"{description} Allowed values: {enum_text}."
            schema = field.get("schema")
            if isinstance(schema, dict):
                if isinstance(schema.get("properties"), dict):
                    property_names = ", ".join(schema["properties"].keys())
                    if property_names:
                        description = f"{description} Object keys: {property_names}."
                item_type = schema.get("items")
                if isinstance(item_type, dict) and item_type.get("type"):
                    description = (
                        f"{description} List item type: {item_type.get('type')}."
                    )

            required = bool(field.get("required", True))
            has_default = "default" in field
            default_value = field.get("default")
            default_repr = repr(default_value) if has_default else "None"

            normalized.append(
                {
                    **field,
                    "name": name,
                    "description": description,
                    "required": required,
                    "dspy_type": dspy_type,
                    "has_default": has_default,
                    "default_repr": default_repr,
                }
            )

        return normalized

    def _resolve_signature_fields(
        self, spec: Dict[str, Any]
    ) -> tuple[list[Dict[str, Any]], list[Dict[str, Any]]]:
        """
        Resolve signature fields with precedence:
        1. spec.input_fields / spec.output_fields
        2. first task inputs/outputs
        """
        input_fields = self._normalize_signature_fields(spec.get("input_fields"))
        output_fields = self._normalize_signature_fields(spec.get("output_fields"))

        if input_fields and output_fields:
            return input_fields, output_fields

        tasks = spec.get("tasks", [])
        if isinstance(tasks, list) and tasks:
            first_task = tasks[0] if isinstance(tasks[0], dict) else {}
            if not input_fields:
                input_fields = self._normalize_signature_fields(
                    first_task.get("inputs")
                )
            if not output_fields:
                output_fields = self._normalize_signature_fields(
                    first_task.get("outputs")
                )

        return input_fields, output_fields

    def _apply_dspy_superspec_overrides(self, spec: Dict[str, Any]) -> None:
        """
        Apply SuperSpec `spec.dspy` automation overrides to legacy runtime keys.

        This keeps templates/runners backward-compatible while allowing users to
        configure DSPy (module + GEPA + RLM) from a single SuperSpec block.
        """
        dspy_cfg = spec.get("dspy")
        if not isinstance(dspy_cfg, dict):
            return

        # 1) Module -> reasoning method
        module = dspy_cfg.get("module")
        if module:
            reasoning = spec.get("reasoning")
            if not isinstance(reasoning, dict):
                reasoning = {}
            if module == "react":
                reasoning["method"] = "react"
            elif module == "rlm":
                reasoning["method"] = "rlm"
            elif module == "predict":
                reasoning["method"] = "predict"
            elif module == "program_of_thought":
                reasoning["method"] = "program_of_thought"
            elif module == "parallel":
                reasoning["method"] = "parallel"
            else:
                reasoning["method"] = "chain_of_thought"
            spec["reasoning"] = reasoning

        # 1b) Optional module parameters
        module_params = dspy_cfg.get("module_params")
        if isinstance(module_params, dict):
            reasoning = spec.get("reasoning")
            if not isinstance(reasoning, dict):
                reasoning = {}
            for key in [
                "max_iterations",
                "parallel_workers",
                "temperature",
                "max_tokens",
            ]:
                if key in module_params and module_params[key] is not None:
                    reasoning[key] = module_params[key]
            spec["reasoning"] = reasoning

        # 2) DSPy RLM -> spec.rlm
        dspy_rlm = dspy_cfg.get("rlm")
        if isinstance(dspy_rlm, dict):
            rlm_cfg = spec.get("rlm")
            if not isinstance(rlm_cfg, dict):
                rlm_cfg = {}

            # Enable RLM when requested via module or explicit flag.
            if module == "rlm":
                rlm_cfg["enabled"] = True
            if "enabled" in dspy_rlm:
                rlm_cfg["enabled"] = bool(dspy_rlm.get("enabled"))

            if "max_iters" in dspy_rlm:
                rlm_cfg["max_iters"] = dspy_rlm.get("max_iters")
            elif "max_iterations" in dspy_rlm:
                rlm_cfg["max_iters"] = dspy_rlm.get("max_iterations")

            if "max_llm_calls" in dspy_rlm:
                rlm_cfg["max_llm_calls"] = dspy_rlm.get("max_llm_calls")

            spec["rlm"] = rlm_cfg

        # 3) DSPy GEPA -> spec.optimization.optimizer.params
        dspy_gepa = dspy_cfg.get("gepa")
        if isinstance(dspy_gepa, dict):
            gepa_enabled = bool(dspy_gepa.get("enabled", False))
            has_gepa_knobs = any(k != "enabled" for k in dspy_gepa.keys())
            if gepa_enabled or has_gepa_knobs:
                optimization = spec.get("optimization")
                if not isinstance(optimization, dict):
                    optimization = {}
                optimization["enabled"] = True

                optimizer = optimization.get("optimizer")
                if not isinstance(optimizer, dict):
                    optimizer = {}
                optimizer["name"] = "GEPA"

                params = optimizer.get("params")
                if not isinstance(params, dict):
                    params = {}

                key_map = {
                    "auto": "auto",
                    "task_model": "task_model",
                    "reflection_model": "reflection_lm",
                    "reflection_lm": "reflection_lm",
                    "candidate_selection_strategy": "candidate_selection_strategy",
                    "skip_perfect_score": "skip_perfect_score",
                    "reflection_minibatch_size": "reflection_minibatch_size",
                    "perfect_score": "perfect_score",
                    "failure_score": "failure_score",
                    "use_merge": "use_merge",
                    "max_merge_invocations": "max_merge_invocations",
                    "max_full_evals": "max_full_evals",
                    "max_metric_calls": "max_metric_calls",
                    "track_stats": "track_stats",
                    "seed": "seed",
                }
                for src_key, dst_key in key_map.items():
                    if src_key in dspy_gepa and dspy_gepa[src_key] is not None:
                        params[dst_key] = dspy_gepa[src_key]

                optimizer["params"] = params
                optimization["optimizer"] = optimizer
                spec["optimization"] = optimization

        # 4) Adapter preferences (runner will apply centrally).
        adapter_cfg = dspy_cfg.get("adapter")
        if isinstance(adapter_cfg, dict):
            spec["_dspy_adapter"] = {
                "mode": adapter_cfg.get("mode"),
                "type": adapter_cfg.get("type"),
                "native_function_calling": adapter_cfg.get(
                    "native_function_calling", False
                ),
                "strict": adapter_cfg.get("strict"),
                "retry_on_parse_error": adapter_cfg.get("retry_on_parse_error"),
                "fallback_adapter": adapter_cfg.get("fallback_adapter"),
            }

        # 5) Tools preferences for ReAct automation.
        tools_cfg = dspy_cfg.get("tools")
        if isinstance(tools_cfg, dict):
            mode = tools_cfg.get("mode", "builtin")

            if mode == "none":
                # Explicitly disable all tool paths.
                spec["tool_backend"] = "dspy"
                spec.pop("mcp_servers", None)
                spec["tool_calling"] = {
                    "enabled": False,
                    "available_tools": [],
                }
            elif mode == "mcp":
                # Use protocol-first path for MCP tool discovery.
                spec["tool_backend"] = "agenspy"
                if "mcp_servers" in tools_cfg and isinstance(
                    tools_cfg.get("mcp_servers"), list
                ):
                    spec["mcp_servers"] = tools_cfg.get("mcp_servers")
            elif mode in {"stackone", "stackone_discovery"}:
                # Runner/template will fetch + convert StackOne tools at runtime.
                spec["tool_backend"] = "dspy"
                spec.pop("mcp_servers", None)
                existing_tool_calling = spec.get("tool_calling", {})
                if not isinstance(existing_tool_calling, dict):
                    existing_tool_calling = {}
                existing_tool_calling.setdefault("enabled", True)
                existing_tool_calling.setdefault("available_tools", [])
                spec["tool_calling"] = existing_tool_calling
            else:
                # Builtin tools map to existing tool_calling shape used by templates.
                builtin_tools = tools_cfg.get("builtin_tools", [])
                spec["tool_backend"] = "dspy"
                spec.pop("mcp_servers", None)
                if isinstance(builtin_tools, list) and builtin_tools:
                    spec["tool_calling"] = {
                        "enabled": True,
                        "available_tools": builtin_tools,
                    }
                else:
                    spec["tool_calling"] = {
                        "enabled": False,
                        "available_tools": [],
                    }

        # 6) Signature behavior (simple vs structured outputs)
        signature_cfg = dspy_cfg.get("signature")
        if isinstance(signature_cfg, dict):
            output_mode = (
                str(signature_cfg.get("output_mode", "simple")).strip().lower()
            )
            if output_mode not in {"simple", "structured"}:
                output_mode = "simple"
            spec["_dspy_signature"] = {"output_mode": output_mode}

        # 7) Assertions/guardrails
        assertions_cfg = dspy_cfg.get("assertions")
        if isinstance(assertions_cfg, dict):
            mode = str(assertions_cfg.get("mode", "fail_fast")).strip().lower()
            if mode not in {"fail_fast", "warn_only"}:
                mode = "fail_fast"
            metric_weight = assertions_cfg.get("metric_weight", 0.3)
            try:
                metric_weight = float(metric_weight)
            except (TypeError, ValueError):
                metric_weight = 0.3
            metric_weight = min(1.0, max(0.0, metric_weight))

            spec["_dspy_assertions"] = {
                "enabled": bool(assertions_cfg.get("enabled", True)),
                "mode": mode,
                "metric_weight": metric_weight,
                "required_fields": assertions_cfg.get("required_fields", []),
                "non_empty": assertions_cfg.get("non_empty", []),
                "enum": assertions_cfg.get("enum", {}),
                "max_length": assertions_cfg.get("max_length", {}),
                "custom_regex": assertions_cfg.get("custom_regex", {}),
            }

    def _get_pipeline_path(self, agent_name: str, target: str | None = None) -> Path:
        """Constructs the path for the output pipeline file."""
        with open(self.project_root / ".super") as f:
            system_name = yaml.safe_load(f).get("project")

        agent_dir = self.project_root / system_name / "agents" / agent_name
        if target and target != "dspy":
            suffix = target.replace("-", "_")
            return agent_dir / "pipelines" / f"{agent_name}_{suffix}_pipeline.py"
        return agent_dir / "pipelines" / f"{agent_name}_pipeline.py"

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Renders a Jinja2 template."""
        template = self.template_env.get_template(template_name)
        return template.render(context)

    def _write_compiled_spec_sidecar(
        self, pipeline_path: Path, spec: Dict[str, Any]
    ) -> str:
        """Write resolved spec next to generated pipeline and return filename."""
        sidecar = pipeline_path.with_name(f"{pipeline_path.stem}_compiled_spec.json")
        sidecar.parent.mkdir(parents=True, exist_ok=True)
        sidecar.write_text(
            json.dumps(spec or {}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return sidecar.name

    def _get_dspy_template(
        self,
        tier_level: str,
        compile_profile: str,
        use_protocol_first: bool,
        use_abstracted: bool,
        use_explicit: bool,
    ) -> str:
        """Select unified DSPy template (tierless OSS model)."""
        if use_protocol_first:
            return self.agenspy_template
        return self.minimal_template

    def compile(
        self,
        args,
        tier_level: str = None,
        use_abstracted: bool = False,
        use_explicit: bool = True,
        compile_profile: str = "minimal",
    ) -> None:
        """Compile agent playbook into a runnable pipeline."""
        try:
            agent_name = args.name
            target = getattr(args, "target", "dspy")
            framework = getattr(args, "framework", "dspy")

            # If framework is specified and not dspy, use the new multi-framework registry
            if framework != "dspy":
                self._compile_with_framework_registry(
                    agent_name,
                    framework,
                    tier_level,
                    compile_profile,
                    args=args,
                )
                return

            # Otherwise, use the existing DSPy compilation path
            context = self._load_playbook_and_get_context(agent_name, tier_level)
            context["compile_target"] = target
            context["compile_profile"] = compile_profile
            is_local_mode = bool(getattr(args, "local", False)) or bool(
                getattr(args, "local_ollama", False)
            )
            is_cloud_mode = bool(getattr(args, "cloud", False))
            if is_local_mode and is_cloud_mode:
                raise ValueError("Use only one of --local or --cloud.")

            runtime_mode = (
                "local" if is_local_mode else ("cloud" if is_cloud_mode else "auto")
            )
            provider_override = getattr(args, "provider", None)
            model_override = getattr(args, "model", None)

            if is_local_mode and not provider_override:
                provider_override = "ollama"
            if is_local_mode and not model_override:
                model_override = "llama3.1:8b"

            context["runtime_mode"] = runtime_mode
            context["provider_override"] = provider_override
            context["model_override"] = model_override
            # Ollama-first default: keep local path available unless user explicitly forces cloud.
            context["include_local_ollama_code"] = not is_cloud_mode
            if getattr(args, "rlm", False):
                spec = context.get("spec", {})
                rlm_cfg = spec.get("rlm", {})
                if not isinstance(rlm_cfg, dict):
                    rlm_cfg = {}
                rlm_cfg["enabled"] = True
                spec["rlm"] = rlm_cfg
            pipeline_path = self._get_pipeline_path(agent_name, target)
            pipeline_path.parent.mkdir(parents=True, exist_ok=True)

            # Detect tool backend (protocol-first vs tool-first)
            spec = context.get("spec", {})
            tool_backend = spec.get("tool_backend", "dspy")  # Default to tool-first
            mcp_servers = spec.get("mcp_servers", [])
            use_protocol_first = (tool_backend == "agenspy") or (len(mcp_servers) > 0)

            # Choose template
            effective_tier = context["tier_level"]
            if target == "dspy":
                template_name = self._get_dspy_template(
                    tier_level=effective_tier,
                    compile_profile=compile_profile,
                    use_protocol_first=use_protocol_first,
                    use_abstracted=use_abstracted,
                    use_explicit=use_explicit,
                )
            else:
                template_name = self.optimas_templates.get(target)
                if not template_name:
                    raise ValueError(f"Unsupported compile target: {target}")

            # Show compilation message with unified pipeline approach details
            if use_protocol_first:
                mode_text = "Protocol-First DSPy pipeline (Agenspy + MCP discovery)"
            elif compile_profile == "optimized":
                mode_text = "Unified DSPy pipeline (minimal code + GEPA optimization via runner)"
            else:
                mode_text = (
                    "Unified DSPy pipeline (minimal PyTorch-like Signature + Module)"
                )

            console.print(f"\n[bold green]🤖 Generating {mode_text}...[/bold green]")

            if target != "dspy":
                console.print(
                    "[cyan]🧠 Optimas Target: Generating pipeline wired to Optimas adapters[/]"
                )
            elif use_protocol_first:
                # NEW: Protocol-first template
                console.print(
                    "[cyan]🔌 Protocol-First Approach: Automatic tool discovery from MCP servers[/]"
                )
                console.print(
                    "[green]🤖 Agenspy Integration: Vendored protocol-first components[/]"
                )
                console.print(
                    "[bright_yellow]🛠️  Auto Tool Discovery: No manual tool loading or registration[/]"
                )
                console.print(
                    "[magenta]🎯 Key Differentiator: Protocol-level optimization + session management[/]"
                )
                if mcp_servers:
                    console.print(
                        f"[bright_cyan]📡 MCP Servers: {len(mcp_servers)} configured ({', '.join(mcp_servers[:2])}{'...' if len(mcp_servers) > 2 else ''})[/]"
                    )
            else:
                console.print(
                    "[cyan]🔧 Unified Capabilities: RLM, GEPA, tools, assertions, structured outputs, RAG (when configured).[/]"
                )

            context["compiled_spec_filename"] = self._write_compiled_spec_sidecar(
                pipeline_path, context.get("spec", {})
            )
            full_pipeline_code = self._render_template(template_name, context)
            pipeline_path.write_text(full_pipeline_code)

            if use_protocol_first:
                approach_note = " (protocol-first/agenspy)"
            elif compile_profile == "optimized":
                approach_note = " (optimized/unified)"
            else:
                approach_note = " (unified)"

            console.print(
                f"✅ Successfully generated DSPy pipeline{approach_note} at: {pipeline_path}"
            )

            # Show guidance based on approach (only in verbose mode)
            if getattr(args, "verbose", False):
                if use_protocol_first:
                    # NEW: Protocol-first guidance
                    console.print("\n[dim]💡 Protocol-first pipeline features:[/]")
                    console.print(
                        "[dim]   • Automatic tool discovery from MCP servers[/]"
                    )
                    console.print(
                        "[dim]   • No manual tool loading or registration required[/]"
                    )
                    console.print(
                        "[dim]   • Protocol-level optimization compatible with GEPA[/]"
                    )
                    console.print(
                        "[dim]   • Session management for stateful interactions[/]"
                    )
                    console.print(
                        "[dim]   • Foundation for Agent2Agent protocol (future)[/]"
                    )
                    console.print(
                        "[dim]   • Key differentiator: SuperOptiX protocol-first approach[/]"
                    )
                elif compile_profile == "minimal":
                    console.print("\n[dim]💡 Minimal DSPy pipeline features:[/]")
                    console.print(
                        "[dim]   • Pure DSPy Signature + Module + forward patterns[/]"
                    )
                    console.print(
                        "[dim]   • Lightweight run path with playbook model/persona config[/]"
                    )
                    console.print(
                        "[dim]   • Optional RLM: use --rlm or spec.rlm.enabled=true[/]"
                    )
                    console.print(
                        "[dim]   • No evaluation/optimization scaffolding in generated code[/]"
                    )
                    console.print(
                        "[dim]   • Recompile with --optimize for full train/evaluate support[/]"
                    )
                elif compile_profile == "optimized":
                    console.print(
                        "\n[dim]💡 Optimizable minimal DSPy pipeline features:[/]"
                    )
                    console.print(
                        "[dim]   • Pure DSPy Signature + Module + forward patterns[/]"
                    )
                    console.print(
                        "[dim]   • Optimization orchestration handled in SuperOptiX runner[/]"
                    )
                    console.print(
                        "[dim]   • GEPA optimization path (no secondary optimizer fallback)[/]"
                    )
                    console.print(
                        "[dim]   • Default optimize models: task=gemini-2.5-flash-lite, teacher=gemini-2.5-flash[/]"
                    )
                self.show_tier_features("unified")

        except FileNotFoundError as e:
            console.print(f"\n[bold red]❌ Error:[/] {e}")
        except Exception as e:
            console.print(f"\n[bold red]❌ Compilation failed:[/] {e}")
            raise

    def _compile_with_framework_registry(
        self,
        agent_name: str,
        framework: str,
        tier_level: str = None,
        compile_profile: str = "minimal",
        args=None,
    ) -> None:
        """
        Compile using the new multi-framework registry.

        This method routes compilation to framework-specific adapters.
        """
        from ..adapters.framework_registry import FrameworkRegistry

        try:
            # Load playbook
            context = self._load_playbook_and_get_context(agent_name, tier_level)
            self._apply_framework_runtime_overrides(
                context, args=args, framework=framework
            )

            # Framework-specific compile-time guidance
            if framework == "claude-sdk":
                self._show_claude_sdk_compile_guidance(context)

            # Get the framework adapter
            console.print(
                f"\n[bold green]🚀 Compiling with {framework.upper()} framework...[/bold green]"
            )

            # Get output path
            pipeline_path = self._get_pipeline_path(agent_name, framework)
            pipeline_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if framework is implemented
            framework_info = FrameworkRegistry.get_framework_info(framework)

            if not framework_info["implemented"]:
                console.print(
                    f"\n[bold yellow]⚠️  {framework.upper()} framework adapter is not yet implemented.[/bold yellow]"
                )
                console.print(f"\n[cyan]📋 Implementation Status:[/]")
                console.print(f"  • Framework: {framework_info['name']}")
                console.print(f"  • Async Required: {framework_info['requires_async']}")
                console.print(f"  • Status: Coming soon!")
                console.print(f"\n[dim]💡 Use --framework dspy (default) for now.[/]")
                console.print(f"[dim]📅 Multi-framework support roadmap:[/]")
                console.print(f"[dim]  • Week 4: Microsoft Agent Framework[/]")
                console.print(f"[dim]  • Week 5: OpenAI Agents SDK[/]")
                console.print(f"[dim]  • Week 6: DeepAgent (LangGraph)[/]")
                console.print(f"[dim]  • Week 7: CrewAI[/]")
                console.print(f"[dim]  • Week 8: Google ADK[/]")
                return

            # Use FrameworkRegistry to compile
            generated_path = FrameworkRegistry.compile_agent(
                framework=framework,
                playbook=context,
                output_path=str(pipeline_path),
                compile_profile=compile_profile,
            )

            console.print(
                f"✅ Successfully compiled with {framework.upper()} framework: {generated_path}"
            )

        except Exception as e:
            console.print(f"\n[bold red]❌ Framework compilation failed:[/] {e}")
            raise

    def _apply_framework_runtime_overrides(
        self, context: Dict[str, Any], args: Any, framework: str
    ) -> None:
        """
        Apply CLI runtime/model overrides to non-DSPy framework playbook context.

        This keeps generated pipeline templates minimal while preserving explicit
        runtime selection behavior from CLI flags.
        """
        if args is None:
            return

        spec = context.get("spec", {})
        if not isinstance(spec, dict):
            return

        lm = spec.get("language_model")
        if not isinstance(lm, dict):
            lm = {}
            spec["language_model"] = lm

        provider_override = getattr(args, "provider", None)
        model_override = getattr(args, "model", None)
        is_local_mode = bool(getattr(args, "local", False)) or bool(
            getattr(args, "local_ollama", False)
        )
        is_cloud_mode = bool(getattr(args, "cloud", False))

        if provider_override:
            lm["provider"] = provider_override
        if model_override:
            lm["model"] = model_override

        if is_local_mode and not provider_override:
            lm["provider"] = "ollama"
        if is_local_mode and not model_override:
            lm["model"] = "llama3.1:8b"

        # Pydantic-AI gateway/direct runtime controls.
        if framework == "pydantic-ai":
            use_gateway = bool(getattr(args, "gateway", False))
            use_direct = bool(getattr(args, "direct", False))
            gateway_url = getattr(args, "gateway_url", None)
            gateway_key_env = getattr(args, "gateway_key_env", None)

            if gateway_url:
                use_gateway = True

            if use_gateway:
                lm["runtime_mode"] = "gateway"
                gateway_cfg = lm.get("gateway")
                if not isinstance(gateway_cfg, dict):
                    gateway_cfg = {}
                gateway_cfg["enabled"] = True
                if gateway_url:
                    gateway_cfg["base_url"] = gateway_url
                if gateway_key_env:
                    gateway_cfg["api_key_env"] = gateway_key_env
                lm["gateway"] = gateway_cfg
                if not lm.get("provider"):
                    lm["provider"] = "gateway"
            elif use_direct:
                lm["runtime_mode"] = "direct"
                gateway_cfg = lm.get("gateway")
                if isinstance(gateway_cfg, dict):
                    gateway_cfg["enabled"] = False
                    lm["gateway"] = gateway_cfg

            # --cloud should never force local defaults for Pydantic.
            if is_cloud_mode and lm.get("provider") == "ollama" and provider_override:
                lm["provider"] = provider_override

        spec["language_model"] = lm
        context["spec"] = spec

    def _show_claude_sdk_compile_guidance(self, context: Dict[str, Any]) -> None:
        """Show compile-time checks and guidance for Claude SDK playbooks."""
        spec = context.get("spec", {})
        lm = spec.get("language_model", {})
        provider = str(lm.get("provider", "anthropic")).lower()
        model = str(lm.get("model", "claude-sonnet-4-5")).strip()

        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        anthropic_base_url = os.getenv("ANTHROPIC_BASE_URL", "").strip()
        use_bedrock = os.getenv("CLAUDE_CODE_USE_BEDROCK") == "1"
        use_vertex = os.getenv("CLAUDE_CODE_USE_VERTEX") == "1"
        use_foundry = os.getenv("CLAUDE_CODE_USE_FOUNDRY") == "1"

        console.print("\n[bold cyan]🔎 Claude SDK Runtime Configuration Check[/]")
        console.print(f"[dim]provider={provider} model={model}[/]")

        supported_providers = {
            "anthropic",
            "bedrock",
            "vertex",
            "foundry",
            "azure",
            "aws",
            "gcp",
        }
        if provider not in supported_providers:
            console.print(
                "[yellow]⚠️  Unsupported provider for Claude SDK in playbook.[/]"
            )
            console.print(
                "[yellow]   Set spec.language_model.provider to anthropic|bedrock|vertex|foundry and recompile.[/]"
            )

        if (
            provider == "anthropic"
            and not anthropic_base_url
            and not model.startswith("claude-")
        ):
            console.print(
                "[yellow]⚠️  provider='anthropic' expects a Claude model name.[/]"
            )
            console.print(
                "[yellow]   Update spec.language_model.model to e.g. claude-opus-4-5, claude-sonnet-4-5, or claude-haiku-4-5 "
                "(or snapshots: claude-opus-4-5-20251101, claude-sonnet-4-5-20250929, claude-haiku-4-5-20251001).[/]"
            )

        auth_ok = False
        if provider == "anthropic":
            auth_ok = bool(anthropic_api_key or anthropic_base_url)
            if not auth_ok:
                console.print("[yellow]⚠️  Missing auth for provider='anthropic'.[/]")
                console.print(
                    "[yellow]   Set ANTHROPIC_API_KEY (or ANTHROPIC_BASE_URL for a compatible endpoint) before run.[/]"
                )
        elif provider in {"bedrock", "aws"}:
            auth_ok = use_bedrock
            if not auth_ok:
                console.print(
                    "[yellow]⚠️  provider='bedrock' requires CLAUDE_CODE_USE_BEDROCK=1 and AWS credentials.[/]"
                )
        elif provider in {"vertex", "gcp"}:
            auth_ok = use_vertex
            if not auth_ok:
                console.print(
                    "[yellow]⚠️  provider='vertex' requires CLAUDE_CODE_USE_VERTEX=1 and GCP credentials.[/]"
                )
        elif provider in {"foundry", "azure"}:
            auth_ok = use_foundry
            if not auth_ok:
                console.print(
                    "[yellow]⚠️  provider='foundry'/'azure' requires CLAUDE_CODE_USE_FOUNDRY=1 and Azure credentials.[/]"
                )

        if auth_ok:
            console.print("[green]✅ Claude SDK auth prerequisites detected.[/]")
        else:
            console.print(
                "[cyan]ℹ️  Pipeline will compile, but run will fail until runtime auth is configured.[/]"
            )

        console.print("\n[bold cyan]📘 Claude SDK Playbook Example[/]")
        console.print(
            """[dim]spec:
  language_model:
    location: cloud
    provider: anthropic
    model: claude-sonnet-4-5
    temperature: 0.2[/]"""
        )
        console.print("[dim]Alternative models: claude-opus-4-5, claude-haiku-4-5[/]")
        console.print(
            "[dim]Stable snapshots: claude-opus-4-5-20251101, claude-sonnet-4-5-20250929, claude-haiku-4-5-20251001[/]"
        )

        console.print("\n[bold cyan]🔐 API Key Setup[/]")
        console.print("[dim]export ANTHROPIC_API_KEY='sk-ant-...'\n[/]")
        console.print(
            "[dim]Then run: super agent run "
            f'{context.get("agent_name", "your_agent")} --framework claude-sdk --goal "..."[/]'
        )

    def _extract_tier_level(
        self, playbook_snake_case: Dict[str, Any], user_tier: str = None
    ) -> str:
        """Legacy compatibility shim: OSS now uses a single unified pipeline model."""
        return "unified"

    def show_tier_features(self, tier: str = None):
        """Show unified OSS pipeline capabilities."""
        console.print("\n[bold blue]🎯 Unified DSPy Pipeline Features[/]")
        features = [
            "Minimal, readable DSPy Signature + Module pipeline generation",
            "RLM and ReAct/module automation via SuperSpec",
            "GEPA optimization lifecycle with runner-managed orchestration",
            "Structured outputs + assertions + blended optimization metrics",
            "Tool and MCP integration driven by SuperSpec configuration",
            "RAG/memory/tooling features enabled by config instead of tiers",
        ]
        for feature in features:
            console.print(f"[green]  ✅ {feature}[/]")
