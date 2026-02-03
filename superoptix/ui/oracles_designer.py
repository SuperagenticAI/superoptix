"""SuperOptiX Oracles Agent Designer Interface."""

import sys
from datetime import datetime
from pathlib import Path

import streamlit as st
import yaml

# Enhanced UI configuration
st.set_page_config(
    page_title="SuperOptiX Oracles Agent Designer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Constants based on metaspec.yaml and existing oracle agents
AGENT_TYPES = [
    "Autonomous",
    "Supervised",
    "Interactive",
    "Reactive",
    "Deliberative",
    "Hybrid",
]
DEVELOPMENT_STAGES = ["alpha", "beta", "stable"]
NAMESPACES = [
    "software",
    "education",
    "business",
    "healthcare",
    "finance",
    "marketing",
    "support",
    "custom",
]

# --- Language Model Configuration ---
PROVIDER_MAP = {
    "local": {
        "options": ["ollama", "vllm", "sg_lang", "mlx", "lm_studio", "custom"],
        "help": "Select a local provider like Ollama or vLLM.",
    },
    "self-hosted": {
        "options": ["custom"],
        "help": "For custom, self-hosted endpoints.",
    },
    "cloud": {
        "options": [
            "openai",
            "anthropic",
            "google",
            "azure",
            "mistral",
            "cohere",
            "groq",
            "deepseek",
            "bedrock",
            "sagemaker",
            "vertex_ai",
            "anyscale",
            "fireworks_ai",
            "together_ai",
            "perplexity",
            "openrouter",
            "replicate",
            "custom",
        ],
        "help": "Select a cloud-based provider. Ensure you have set the corresponding API key environment variable.",
    },
}
MODEL_LOCATIONS = list(PROVIDER_MAP.keys())

COMMON_ROLES = [
    "Software Developer",
    "Data Analyst",
    "Content Writer",
    "Customer Support",
    "Math Tutor",
    "Elementary Math Teacher",
    "Language Tutor",
    "Research Assistant",
    "Code Reviewer",
    "Technical Writer",
    "Business Analyst",
    "Marketing Assistant",
    "QA Engineer",
    "Customer Support Representative",
]

PERSONALITY_TRAITS = [
    "analytical",
    "detail-oriented",
    "problem-solver",
    "patient",
    "encouraging",
    "clear",
    "witty",
    "formal",
    "friendly",
    "professional",
    "creative",
    "logical",
    "helpful",
    "knowledgeable",
    "engaging",
    "culturally aware",
]

BUILTIN_METRICS = [
    "answer_exact_match",
    "answer_passage_match",
    "semantic_f1",
    "rouge_l",
    "bleu",
    "meteor",
    "answer_correctness",
    "faithfulness",
    "context_relevance",
]

FEATURE_SPECIFICATION_TYPES = ["llm_eval", "human_eval", "pytest"]


def load_agent_config():
    """Load agent configuration from command line args or environment."""
    try:
        if len(sys.argv) > 1:
            return {
                "agent_name": sys.argv[1],
                "level": sys.argv[2] if len(sys.argv) > 2 else "oracles",
            }

        import os

        return {
            "agent_name": os.getenv("SUPER_AGENT_NAME", "my_agent"),
            "level": os.getenv("SUPER_AGENT_LEVEL", "oracles"),
        }
    except Exception:
        return {"agent_name": "my_agent", "level": "oracles"}


def save_agent_playbook(agent_config, agent_name):
    """Save agent playbook to the appropriate directory structure."""
    try:
        project_root = Path.cwd()

        # Find project name from .super file
        super_file = project_root / ".super"
        if super_file.exists():
            with open(super_file, "r") as f:
                project_config = yaml.safe_load(f)
                project_name = project_config.get("project", "agents")
        else:
            project_name = "agents"

        # Create directory structure
        agent_dir = (
            project_root / project_name / "agents" / agent_name.lower() / "playbook"
        )
        agent_dir.mkdir(parents=True, exist_ok=True)

        # Convert agent_config to proper playbook format
        agent_id = agent_name.lower().replace(" ", "_").replace("-", "_")
        current_time = datetime.now().isoformat()

        playbook_data = {
            "apiVersion": "agent/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": agent_config["metadata"]["display_name"],
                "id": agent_id,
                "namespace": agent_config["metadata"]["namespace"],
                "version": agent_config["metadata"]["version"],
                "stage": agent_config["metadata"]["stage"],
                "level": agent_config["metadata"]["level"],
                "agent_type": agent_config["metadata"]["type"],
                "description": agent_config["metadata"]["description"],
                "created_at": current_time,
                "updated_at": current_time,
            },
            "spec": {
                "language_model": {
                    "location": agent_config["llm"].get("location", "local"),
                    "provider": agent_config["llm"]["provider"],
                    "model": agent_config["llm"]["model"],
                    **(
                        {"api_base": agent_config["llm"]["api_base"]}
                        if "api_base" in agent_config["llm"]
                        else {}
                    ),
                },
                "persona": agent_config["persona"],
                "tasks": agent_config["tasks"],
                "agentflow": agent_config["agentflow"],
                "evaluation": {
                    "builtin_metrics": [
                        {
                            "name": metric,
                            "threshold": agent_config["evaluation"]["metric_threshold"],
                        }
                        for metric in agent_config["evaluation"]["builtin_metrics"]
                    ]
                },
            },
        }

        # Add feature specifications if scenarios are present
        if "scenarios" in agent_config and agent_config["scenarios"]:
            playbook_data["spec"]["feature_specifications"] = {
                "scenarios": agent_config["scenarios"]
            }

        # Add optimization if present
        if "optimization" in agent_config:
            opt_config = agent_config["optimization"]
            playbook_data["spec"]["optimization"] = {
                "strategy": opt_config["strategy"],
                "metric": opt_config["metric"],
                "metric_threshold": opt_config["metric_threshold"],
                f"{opt_config['strategy']}_config": {
                    "max_bootstrapped_demos": opt_config["max_bootstrapped_demos"],
                    "max_rounds": opt_config["max_rounds"],
                },
            }

        # Save playbook
        playbook_path = agent_dir / f"{agent_name.lower()}_playbook.yaml"
        with open(playbook_path, "w") as f:
            yaml.dump(playbook_data, f, default_flow_style=False, sort_keys=False)

        relative_path = playbook_path.relative_to(project_root)
        return (
            True,
            str(relative_path),
            f"Agent '{agent_config['metadata']['display_name']}' created successfully! Saved to: {relative_path}",
        )
    except Exception as e:
        return False, None, f"Error saving playbook: {str(e)}"


def load_templates_from_playbooks():
    """Scans the built-in agents directory and loads them as templates."""
    templates_by_industry = {}
    try:
        # Assumes the script is in ui/, goes up to find the root, then to agents/
        agents_dir = Path(__file__).parent.parent / "agents"
        if not agents_dir.exists():
            return {}

        for industry_dir in agents_dir.iterdir():
            if industry_dir.is_dir():
                industry_name = industry_dir.name
                # Skip demo templates and demo-related directories
                if "demo" in industry_name.lower():
                    continue

                templates_by_industry[industry_name] = []
                for playbook_path in industry_dir.rglob("*_playbook.yaml"):
                    try:
                        with open(playbook_path, "r") as f:
                            playbook = yaml.safe_load(f)

                        metadata = playbook.get("metadata", {})
                        spec = playbook.get("spec", {})
                        persona = spec.get("persona", {})
                        task = spec.get("tasks", [{}])[0]
                        inputs = task.get("inputs", [])
                        outputs = task.get("outputs", [])
                        agentflow = spec.get("agentflow", [{}])[0]
                        feature_specifications = spec.get("feature_specifications", {})
                        scenarios = feature_specifications.get("scenarios", [])

                        template_data = {
                            "display_name": metadata.get(
                                "name",
                                playbook_path.stem.replace("_playbook", "").title(),
                            ),
                            "role": persona.get("role"),
                            "goal": persona.get("goal"),
                            "traits": persona.get("traits", []),
                            "task_name": task.get("name"),
                            "task_instruction": task.get("instruction"),
                            # For backward compatibility, keep the old single input/output format
                            "input_name": inputs[0].get("name") if inputs else None,
                            "input_description": inputs[0].get("description")
                            if inputs
                            else None,
                            "output_name": outputs[0].get("name") if outputs else None,
                            "output_description": outputs[0].get("description")
                            if outputs
                            else None,
                            # New: Store complete inputs and outputs arrays
                            "inputs": inputs,
                            "outputs": outputs,
                            "scenarios": scenarios,
                            "agentflow_name": agentflow.get("name"),
                            "agentflow_type": agentflow.get("type"),
                            "agentflow_task": agentflow.get("task"),
                        }
                        templates_by_industry[industry_name].append(template_data)
                    except Exception as e:
                        st.warning(f"Could not load template from {playbook_path}: {e}")
                        continue

        return templates_by_industry
    except Exception as e:
        st.error(f"Error loading templates: {e}")
        return {}


def render_sidebar():
    """Render the sidebar with navigation and help."""
    with st.sidebar:
        st.title("🎨 Oracles Designer")
        st.markdown("---")

        # Load templates
        templates = load_templates_from_playbooks()

        if templates:
            st.subheader("📚 Templates")
            # Set software as default industry
            industry_options = list(templates.keys())
            default_industry_index = 0
            if "software" in industry_options:
                default_industry_index = industry_options.index("software")

            selected_industry = st.selectbox(
                "Industry", industry_options, index=default_industry_index
            )

            if selected_industry and templates[selected_industry]:
                # Set first template as default
                template_options = [
                    t["display_name"] for t in templates[selected_industry]
                ]
                selected_template = st.selectbox(
                    "Template",
                    template_options,
                    index=0,  # Default to first template
                )

                if selected_template:
                    template = next(
                        t
                        for t in templates[selected_industry]
                        if t["display_name"] == selected_template
                    )

                    if st.button("📋 Load Template"):
                        # Load template data into session state
                        st.session_state.template_loaded = True
                        st.session_state.template_data = template

                        # Load inputs and outputs from template
                        if template.get("inputs"):
                            st.session_state.current_inputs = template.get("inputs", [])
                        if template.get("outputs"):
                            st.session_state.current_outputs = template.get(
                                "outputs", []
                            )

                        # Load scenarios from template
                        if template.get("scenarios"):
                            st.session_state.current_scenarios = template.get(
                                "scenarios", []
                            )

                        st.rerun()

                # Add clear template button if template is loaded
                if (
                    hasattr(st.session_state, "current_template")
                    and st.session_state.current_template
                ):
                    if st.button("🗑️ Clear Template"):
                        st.session_state.current_template = None
                        st.session_state.current_inputs = [
                            {
                                "name": "",
                                "type": "str",
                                "description": "",
                                "required": True,
                            }
                        ]
                        st.session_state.current_outputs = [
                            {"name": "", "type": "str", "description": ""}
                        ]
                        st.session_state.current_scenarios = []
                        st.rerun()

        st.markdown("---")
        st.markdown("### 🆘 Help")
        st.markdown("""
        **Oracles Tier Agents:**
        - Specialized in specific domains
        - Use few-shot bootstrapping optimization
        - Focus on accuracy and reliability
        - Ideal for production use cases
        """)


def main():
    """Main application function."""
    # Initialize session state
    if "current_inputs" not in st.session_state:
        st.session_state.current_inputs = [
            {"name": "", "type": "str", "description": "", "required": True}
        ]
    if "current_outputs" not in st.session_state:
        st.session_state.current_outputs = [
            {"name": "", "type": "str", "description": ""}
        ]
    if "current_scenarios" not in st.session_state:
        st.session_state.current_scenarios = []
    if "num_inputs" not in st.session_state:
        st.session_state.num_inputs = 1
    if "num_outputs" not in st.session_state:
        st.session_state.num_outputs = 1
    if "num_scenarios" not in st.session_state:
        st.session_state.num_scenarios = 0
    if "current_template" not in st.session_state:
        st.session_state.current_template = None

    # Load agent configuration
    config = load_agent_config()
    agent_name = config["agent_name"]
    level = config["level"]

    # Render sidebar
    render_sidebar()

    # Main content
    st.title("🎨 SuperOptiX Oracles Agent Designer")
    st.markdown(f"**Creating:** {agent_name} | **Tier:** {level.title()}")

    # Initialize template variable
    template = None

    # Check if template was loaded
    if (
        hasattr(st.session_state, "template_loaded")
        and st.session_state.template_loaded
    ):
        template = st.session_state.template_data
        st.success(
            f"✅ Template '{template['display_name']}' loaded! Fill in the form below to customize."
        )

        # Store template data in session state for persistent use
        st.session_state.current_template = template

        # Load scenarios from template
        if template.get("scenarios"):
            st.session_state.current_scenarios = template.get("scenarios", [])

        # Clear the flag
        st.session_state.template_loaded = False
    else:
        # Use stored template data if available
        if hasattr(st.session_state, "current_template"):
            template = st.session_state.current_template

    # Debug: Show template status
    if template:
        with st.expander("🔍 Debug: Template Status", expanded=False):
            st.write(f"**Template:** {template.get('display_name', 'Unknown')}")
            st.write(f"**Task Name:** {template.get('task_name', 'Not set')}")
            st.write(f"**Provider:** {template.get('provider', 'Not set')}")
            st.write(f"**Model:** {template.get('model', 'Not set')}")
            st.write(f"**Inputs:** {len(template.get('inputs', []))}")
            st.write(f"**Outputs:** {len(template.get('outputs', []))}")
            st.write(f"**Scenarios:** {len(template.get('scenarios', []))}")

        # Auto-generate default scenarios if none exist and inputs/outputs are defined
        if (
            not st.session_state.current_scenarios
            and any(
                inp["name"]
                for inp in st.session_state.current_inputs
                if inp["name"] and inp["name"].strip()
            )
            and any(
                out["name"]
                for out in st.session_state.current_outputs
                if out["name"] and out["name"].strip()
            )
        ):
            # Get valid input/output names
            valid_inputs = [
                inp["name"]
                for inp in st.session_state.current_inputs
                if inp["name"] and inp["name"].strip()
            ]
            valid_outputs = [
                out["name"]
                for out in st.session_state.current_outputs
                if out["name"] and out["name"].strip()
            ]

            if valid_inputs and valid_outputs:
                # Create a basic scenario
                default_scenario = {
                    "name": "basic_task_scenario",
                    "description": "A basic scenario to test the agent's core functionality",
                    "input": {valid_inputs[0]: "Sample input for testing"},
                    "expected_output": {
                        valid_outputs[0]: "Expected output for the given input"
                    },
                }
                st.session_state.current_scenarios = [default_scenario]
                st.info(
                    "💡 A default scenario has been created based on your input/output definitions. You can modify or add more scenarios."
                )

    # === FORM SECTIONS ===

    # 1. Basic Information
    with st.expander("📝 1. Basic Information", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            display_name = st.text_input(
                "Agent Display Name",
                value=template.get("display_name", "") if template else "",
                help="Human-readable name for your agent",
            )

            namespace = st.selectbox(
                "Namespace",
                NAMESPACES,
                index=NAMESPACES.index(template.get("namespace", "software"))
                if template
                else 0,
                help="Domain or industry category",
            )

            version = st.text_input("Version", value="1.0.0", help="Agent version")

        with col2:
            agent_type = st.selectbox(
                "Agent Type",
                AGENT_TYPES,
                index=AGENT_TYPES.index(template.get("agent_type", "Supervised"))
                if template
                else 1,
                help="How the agent operates",
            )

            stage = st.selectbox(
                "Development Stage",
                DEVELOPMENT_STAGES,
                index=DEVELOPMENT_STAGES.index(template.get("stage", "alpha"))
                if template
                else 0,
                help="Current development phase",
            )

            description = st.text_area(
                "Description",
                value=template.get("description", "") if template else "",
                help="Brief description of what the agent does",
            )

    # 2. Language Model Configuration
    with st.expander("🧠 2. Language Model", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            model_location = st.selectbox(
                "Model Location", MODEL_LOCATIONS, help="Where your model is hosted"
            )

            provider_options = PROVIDER_MAP[model_location]["options"]
            provider = st.selectbox(
                "Provider", provider_options, help=PROVIDER_MAP[model_location]["help"]
            )

        with col2:
            model = st.text_input(
                "Model Name",
                value="llama3.2:1b" if provider == "ollama" else "",
                help="Specific model identifier",
            )

            api_base = st.text_input(
                "API Base URL (Optional)",
                value="http://localhost:11434" if provider == "ollama" else "",
                help="Custom API endpoint (leave empty for default)",
            )

    # 3. Persona Configuration
    with st.expander("👤 3. Persona", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            persona_name = st.text_input(
                "Persona Name",
                value=template.get("persona_name", "Agent") if template else "Agent",
                help="Name for the agent's persona",
            )

            role = st.text_input(
                "Role",
                value=template.get("role", "") if template else "",
                help="Professional role or title",
            )

        with col2:
            goal = st.text_area(
                "Goal",
                value=template.get("goal", "") if template else "",
                help="Primary objective or mission",
            )

            # Filter template traits to only include valid ones
            template_traits = template.get("traits", []) if template else []

            # Ensure template_traits is a list
            if not isinstance(template_traits, list):
                template_traits = []
                st.warning(
                    "⚠️ Template traits were not in the expected format and have been reset."
                )

            valid_template_traits = [
                trait for trait in template_traits if trait in PERSONALITY_TRAITS
            ]

            # Show warning if there are invalid traits
            invalid_traits = [
                trait for trait in template_traits if trait not in PERSONALITY_TRAITS
            ]
            if invalid_traits:
                st.warning(
                    f"⚠️ Some traits from the template are not in the standard list and will be ignored: {invalid_traits}"
                )

            selected_traits = st.multiselect(
                "Personality Traits",
                PERSONALITY_TRAITS,
                default=valid_template_traits,
                help="Character traits that define the agent's personality",
            )

    # 4. Task Configuration
    with st.expander("🎯 4. Task Configuration", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            task_name = st.text_input(
                "Task Name",
                value=template.get("task_name", "") if template else "",
                help="Unique identifier for the task",
            )

            task_instruction = st.text_area(
                "Task Instruction",
                value=template.get("task_instruction", "") if template else "",
                help="Detailed instructions for the task",
            )

        with col2:
            flow_step_name = st.text_input(
                "Flow Step Name",
                value=template.get("agentflow_name", "") if template else "",
                help="Name of the workflow step",
            )

            flow_step_type = st.selectbox(
                "Flow Step Type",
                ["Generate", "Analyze", "Process", "Validate"],
                index=0
                if template and template.get("agentflow_type", "") == "Generate"
                else 0,
                help="Type of operation in the workflow",
            )

            flow_step_task = st.text_input(
                "Flow Step Task",
                value=template.get("agentflow_task", "") if template else "",
                help="Task to execute in this step",
            )

        # Input/Output Schema
        st.subheader("📥 Inputs")
        for i, input_item in enumerate(st.session_state.current_inputs):
            col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
            with col1:
                input_item["name"] = st.text_input(
                    f"Name {i + 1}",
                    value=input_item.get("name", ""),
                    key=f"input_name_{i}",
                )
            with col2:
                input_item["type"] = st.selectbox(
                    f"Type {i + 1}",
                    ["str", "int", "float", "bool", "list", "dict"],
                    index=0,
                    key=f"input_type_{i}",
                )
            with col3:
                input_item["description"] = st.text_input(
                    f"Description {i + 1}",
                    value=input_item.get("description", ""),
                    key=f"input_desc_{i}",
                )
            with col4:
                input_item["required"] = st.checkbox(
                    f"Required {i + 1}",
                    value=input_item.get("required", True),
                    key=f"input_req_{i}",
                )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Add Input"):
                st.session_state.current_inputs.append(
                    {"name": "", "type": "str", "description": "", "required": True}
                )
                st.rerun()
        with col2:
            if (
                st.button("➖ Remove Input")
                and len(st.session_state.current_inputs) > 1
            ):
                st.session_state.current_inputs.pop()
                st.rerun()

        st.subheader("📤 Outputs")
        for i, output_item in enumerate(st.session_state.current_outputs):
            col1, col2, col3 = st.columns([2, 2, 4])
            with col1:
                output_item["name"] = st.text_input(
                    f"Name {i + 1}",
                    value=output_item.get("name", ""),
                    key=f"output_name_{i}",
                )
            with col2:
                output_item["type"] = st.selectbox(
                    f"Type {i + 1}",
                    ["str", "int", "float", "bool", "list", "dict"],
                    index=0,
                    key=f"output_type_{i}",
                )
            with col3:
                output_item["description"] = st.text_input(
                    f"Description {i + 1}",
                    value=output_item.get("description", ""),
                    key=f"output_desc_{i}",
                )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Add Output"):
                st.session_state.current_outputs.append(
                    {"name": "", "type": "str", "description": ""}
                )
                st.rerun()
        with col2:
            if (
                st.button("➖ Remove Output")
                and len(st.session_state.current_outputs) > 1
            ):
                st.session_state.current_outputs.pop()
                st.rerun()

    # 5. Evaluation Configuration
    with st.expander("📊 5. Evaluation", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            selected_metrics = st.multiselect(
                "Built-in Metrics",
                BUILTIN_METRICS,
                default=["answer_correctness"],
                help="Metrics to evaluate agent performance",
            )

        with col2:
            metric_threshold = st.slider(
                "Metric Threshold",
                0.0,
                1.0,
                0.7,
                help="Target score for evaluation metrics",
            )

    # 6. Feature Specifications (Scenarios)
    with st.expander("🧪 6. Feature Specifications", expanded=False):
        st.info("Define test scenarios to validate your agent's behavior.")

        # Get current input/output names for scenario creation
        valid_inputs = [
            inp["name"]
            for inp in st.session_state.current_inputs
            if inp["name"]
            and inp["name"].strip()
            and inp["name"] not in [f"input_{i + 1}" for i in range(10)]
        ]
        valid_outputs = [
            out["name"]
            for out in st.session_state.current_outputs
            if out["name"]
            and out["name"].strip()
            and out["name"] not in [f"output_{i + 1}" for i in range(10)]
        ]

        # Display existing scenarios
        for i, scenario in enumerate(st.session_state.current_scenarios):
            with st.container():
                st.markdown(f"**Scenario {i + 1}:** {scenario.get('name', '')}")

                # Scenario name and description
                col1, col2 = st.columns(2)
                with col1:
                    scenario["name"] = st.text_input(
                        f"Name {i + 1}",
                        value=scenario.get("name", ""),
                        key=f"scenario_name_{i}",
                    )
                with col2:
                    scenario["description"] = st.text_area(
                        f"Description {i + 1}",
                        value=scenario.get("description", ""),
                        key=f"scenario_desc_{i}",
                    )

                # Input values
                if valid_inputs:
                    st.markdown("**Input Values:**")
                    input_cols = st.columns(min(3, len(valid_inputs)))
                    scenario["input"] = scenario.get("input", {})
                    for j, input_name in enumerate(valid_inputs):
                        col_idx = j % 3
                        with input_cols[col_idx]:
                            scenario["input"][input_name] = st.text_input(
                                f"{input_name}:",
                                value=scenario.get("input", {}).get(input_name, ""),
                                key=f"scenario_input_{i}_{input_name}",
                            )

                # Expected output values
                if valid_outputs:
                    st.markdown("**Expected Output Values:**")
                    output_cols = st.columns(min(3, len(valid_outputs)))
                    scenario["expected_output"] = scenario.get("expected_output", {})
                    for j, output_name in enumerate(valid_outputs):
                        col_idx = j % 3
                        with output_cols[col_idx]:
                            scenario["expected_output"][output_name] = st.text_input(
                                f"{output_name}:",
                                value=scenario.get("expected_output", {}).get(
                                    output_name, ""
                                ),
                                key=f"scenario_output_{i}_{output_name}",
                            )

                if st.button(f"❌ Remove Scenario {i + 1}", key=f"remove_scenario_{i}"):
                    st.session_state.current_scenarios.pop(i)
                    st.rerun()
                st.markdown("---")

        # Add new scenario
        with st.form("add_scenario"):
            col1, col2 = st.columns(2)
            with col1:
                new_scenario_name = st.text_input(
                    "Scenario Name", key="new_scenario_name"
                )
                new_scenario_desc = st.text_area("Description", key="new_scenario_desc")
            with col2:
                # Show input fields based on actual input names
                if valid_inputs:
                    st.markdown("**Input Values:**")
                    input_values = {}
                    for input_name in valid_inputs:
                        input_value = st.text_input(
                            f"{input_name}:", key=f"scenario_input_{input_name}"
                        )
                        if input_value:
                            input_values[input_name] = input_value
                else:
                    st.warning("⚠️ Define inputs first to create scenarios")
                    input_values = {}

                # Show output fields based on actual output names
                if valid_outputs:
                    st.markdown("**Expected Output Values:**")
                    output_values = {}
                    for output_name in valid_outputs:
                        output_value = st.text_input(
                            f"{output_name}:", key=f"scenario_output_{output_name}"
                        )
                        if output_value:
                            output_values[output_name] = output_value
                else:
                    st.warning("⚠️ Define outputs first to create scenarios")
                    output_values = {}

            if st.form_submit_button("➕ Add Scenario"):
                if new_scenario_name and new_scenario_desc:
                    scenario_data = {
                        "name": new_scenario_name,
                        "description": new_scenario_desc,
                        "input": input_values,
                        "expected_output": output_values,
                    }
                    st.session_state.current_scenarios.append(scenario_data)
                    st.rerun()

    # 7. Optimization Configuration
    with st.expander("⚙️ 7. Optimization (Optional)", expanded=False):
        enable_optimization = st.checkbox("Enable Automatic Optimization", value=True)
        if enable_optimization:
            st.info(
                "For oracles agents, we use few_shot_bootstrapping strategy. Advanced optimizers like MiPRO and CoPRO are available for Sage level agents and above."
            )

            col1, col2 = st.columns(2)
            with col1:
                optimization_strategy = st.selectbox(
                    "Optimization Strategy",
                    ["few_shot_bootstrapping"],
                    help="Strategy for improving agent performance",
                )
                try:
                    metric_default_index = BUILTIN_METRICS.index("answer_correctness")
                except ValueError:
                    metric_default_index = 0
                optimization_metric = st.selectbox(
                    "Optimization Metric",
                    BUILTIN_METRICS,
                    index=metric_default_index,
                    help="Metric to optimize for",
                )
            with col2:
                max_bootstrapped_demos = st.number_input(
                    "Max Demos",
                    1,
                    10,
                    4,
                    help="Maximum number of bootstrapped demonstrations",
                )
                max_rounds = st.number_input(
                    "Max Rounds", 1, 5, 1, help="Maximum optimization rounds"
                )

            optimization_metric_threshold = st.slider(
                "Optimization Metric Threshold",
                0.0,
                1.0,
                0.7,
                help="Target score for the optimization metric",
            )

    # === FORM FOR FINAL SUBMISSION ===
    with st.form("oracles_agent_designer", clear_on_submit=False):
        st.subheader("🚀 Generate Agent")
        st.markdown(
            "Review your configuration above, then click the button below to create your agent playbook."
        )

        # Show summary of current configuration
        with st.expander("📋 Configuration Summary", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Basic Info:**")
                st.write(f"- Name: {display_name}")
                st.write(f"- Role: {role}")
                st.write(f"- Model: {provider}/{model}")
                st.write(f"- Task: {task_name}")
            with col2:
                st.write("**I/O Schema:**")
                valid_inputs_summary = [
                    inp["name"]
                    for inp in st.session_state.current_inputs
                    if inp["name"]
                    and inp["name"] not in [f"input_{i + 1}" for i in range(10)]
                ]
                valid_outputs_summary = [
                    out["name"]
                    for out in st.session_state.current_outputs
                    if out["name"]
                    and out["name"] not in [f"output_{i + 1}" for i in range(10)]
                ]
                st.write(
                    f"- Inputs: {', '.join(valid_inputs_summary) if valid_inputs_summary else 'None defined'}"
                )
                st.write(
                    f"- Outputs: {', '.join(valid_outputs_summary) if valid_outputs_summary else 'None defined'}"
                )
                st.write(
                    f"- Scenarios: {len(st.session_state.current_scenarios)} scenarios"
                )

        # Submit button
        submitted = st.form_submit_button("🚀 Create Agent", use_container_width=True)

        # Store form data in session state for validation
        if submitted:
            st.session_state.form_data = {
                "display_name": display_name,
                "task_name": task_name,
                "provider": provider,
                "model": model,
                "namespace": namespace,
                "version": version,
                "description": description,
                "agent_type": agent_type,
                "stage": stage,
                "model_location": model_location,
                "api_base": api_base,
                "persona_name": persona_name,
                "role": role,
                "goal": goal,
                "selected_traits": selected_traits,
                "task_instruction": task_instruction,
                "flow_step_name": flow_step_name,
                "flow_step_type": flow_step_type,
                "flow_step_task": flow_step_task,
                "selected_metrics": selected_metrics,
                "metric_threshold": metric_threshold,
                "enable_optimization": enable_optimization,
                "optimization_strategy": optimization_strategy
                if enable_optimization
                else None,
                "optimization_metric": optimization_metric
                if enable_optimization
                else None,
                "max_bootstrapped_demos": max_bootstrapped_demos
                if enable_optimization
                else None,
                "max_rounds": max_rounds if enable_optimization else None,
                "optimization_metric_threshold": optimization_metric_threshold
                if enable_optimization
                else None,
            }

    # Handle form submission
    if submitted and hasattr(st.session_state, "form_data"):
        form_data = st.session_state.form_data

        # Validate required fields
        if (
            not form_data["display_name"]
            or not form_data["task_name"]
            or not form_data["provider"]
            or not form_data["model"]
        ):
            st.error(
                "❌ Please fill in all required fields: Agent Name, Task Name, Provider, and Model."
            )
            return

        # Use session state data for inputs, outputs, and scenarios
        inputs = st.session_state.current_inputs
        outputs = st.session_state.current_outputs
        scenarios = st.session_state.current_scenarios

        # Validate inputs and outputs
        valid_inputs = [
            inp
            for inp in inputs
            if inp["name"]
            and inp["name"].strip()
            and inp["name"] not in [f"input_{i + 1}" for i in range(10)]
        ]
        valid_outputs = [
            out
            for out in outputs
            if out["name"]
            and out["name"].strip()
            and out["name"] not in [f"output_{i + 1}" for i in range(10)]
        ]

        if not valid_inputs:
            st.error("❌ Please define at least one input with a proper name.")
            return

        if not valid_outputs:
            st.error("❌ Please define at least one output with a proper name.")
            return

        # Prepare agent configuration
        agent_config = {
            "metadata": {
                "name": agent_name,
                "display_name": form_data["display_name"],
                "namespace": form_data["namespace"],
                "version": form_data["version"],
                "description": form_data["description"],
                "level": level,
                "type": form_data["agent_type"],
                "stage": form_data["stage"],
            },
            "llm": {
                "location": form_data["model_location"],
                "provider": form_data["provider"],
                "model": form_data["model"],
                **(
                    {"api_base": form_data["api_base"]} if form_data["api_base"] else {}
                ),
            },
            "persona": {
                "name": form_data["persona_name"],
                "role": form_data["role"],
                "goal": form_data["goal"],
                "traits": form_data["selected_traits"],
            },
            "tasks": [
                {
                    "name": form_data["task_name"],
                    "instruction": form_data["task_instruction"],
                    "inputs": valid_inputs,
                    "outputs": valid_outputs,
                }
            ],
            "agentflow": [
                {
                    "name": form_data["flow_step_name"],
                    "type": form_data["flow_step_type"],
                    "task": form_data["flow_step_task"],
                }
            ],
            "evaluation": {
                "builtin_metrics": form_data["selected_metrics"],
                "metric_threshold": form_data["metric_threshold"],
            },
        }

        # Add optimization if enabled
        if form_data["enable_optimization"]:
            agent_config["optimization"] = {
                "strategy": form_data["optimization_strategy"],
                "metric": form_data["optimization_metric"],
                "max_bootstrapped_demos": form_data["max_bootstrapped_demos"],
                "max_rounds": form_data["max_rounds"],
                "metric_threshold": form_data["optimization_metric_threshold"],
            }

        # Add scenarios to agent_config
        if scenarios:
            agent_config["scenarios"] = scenarios

        # Generate and save agent playbook
        try:
            with st.spinner("🔄 Generating agent playbook..."):
                success, playbook_path, message = save_agent_playbook(
                    agent_config, agent_name
                )

            if success:
                st.success(f"✅ {message}")

                # Show summary
                with st.expander("📄 Generated Playbook Summary", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**📁 Agent Details:**")
                        st.write(f"- **Name:** {form_data['display_name']}")
                        st.write(f"- **Level:** {level.title()}")
                        st.write(f"- **Namespace:** {form_data['namespace']}")
                        st.write(f"- **Role:** {form_data['role']}")

                        st.write("**🧠 Language Model:**")
                        st.write(f"- **Provider:** {form_data['provider']}")
                        st.write(f"- **Model:** {form_data['model']}")
                        if form_data["api_base"]:
                            st.write(f"- **API Base:** {form_data['api_base']}")

                    with col2:
                        st.write("**⚙️ Task Configuration:**")
                        st.write(f"- **Task:** {form_data['task_name']}")
                        st.write(f"- **Inputs:** {len(valid_inputs)} defined")
                        st.write(f"- **Outputs:** {len(valid_outputs)} defined")
                        st.write(f"- **Scenarios:** {len(scenarios)} scenarios")

                        st.write("**🚀 Agent Flow:**")
                        st.write(f"- **Step:** {form_data['flow_step_name']}")
                        st.write(f"- **Type:** {form_data['flow_step_type']}")
                        st.write(f"- **Task:** {form_data['flow_step_task']}")

                # Show next steps
                st.markdown("### 🎯 Next Steps")
                st.markdown(f"""
                1. **📂 Review:** Your playbook has been saved to `{playbook_path}`
                2. **🧪 Test:** Run functional tests to validate your agent
                3. **🚀 Deploy:** Use the agent in your SuperOptiX orchestra
                """)

                # Action buttons
                if st.button("🔄 Create Another Agent", use_container_width=True):
                    # Clear session state and rerun
                    for key in list(st.session_state.keys()):
                        if key.startswith(
                            ("current_", "num_", "input_", "output_", "ft_")
                        ):
                            del st.session_state[key]
                    st.rerun()

            else:
                st.error(f"❌ {message}")

        except Exception as e:
            st.error(f"❌ Error generating playbook: {str(e)}")
            st.exception(e)


if __name__ == "__main__":
    main()
