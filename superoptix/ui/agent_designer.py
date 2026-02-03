from pathlib import Path

import streamlit as st
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add DSPy-specific configurations at the top
DSPY_SIGNATURE_TYPES = {
    "String": "str",
    "List": "List[str]",
    "Dict": "Dict[str, Any]",
    "Number": "float",
    "Boolean": "bool",
}

DSPY_MODULE_TYPES = {
    "Predict": {
        "description": "Simple prediction module for direct input-output tasks",
        "input_format": "Single input, single output",
    },
    "ChainOfThought": {
        "description": "Reasoning module with intermediate steps",
        "input_format": "Input with reasoning steps",
    },
}

# Update the LM configurations to be more generic
DSPY_LM_CONFIGS = {
    # Cloud Providers
    "openai": {
        "model_type": "chat",
        "location": "cloud",
        "kwargs": {
            "temperature": {"min": 0.0, "max": 2.0, "default": 0.7},
            "max_tokens": {"min": 100, "max": 4000, "default": 2000},
            "top_p": {"min": 0.0, "max": 1.0, "default": 1.0},
            "frequency_penalty": {"min": -2.0, "max": 2.0, "default": 0.0},
            "presence_penalty": {"min": -2.0, "max": 2.0, "default": 0.0},
        },
    },
    "anthropic": {
        "model_type": "chat",
        "location": "cloud",
        "kwargs": {
            "temperature": {"min": 0.0, "max": 1.0, "default": 0.7},
            "max_tokens": {"min": 100, "max": 4000, "default": 2000},
            "top_p": {"min": 0.0, "max": 1.0, "default": 1.0},
        },
    },
    # Local Providers
    "sglang": {
        "model_type": "chat",
        "location": "local",
        "provider_class": "dspy.LocalProvider",
        "kwargs": {
            "temperature": {"min": 0.0, "max": 2.0, "default": 0.7},
            "max_tokens": {"min": 100, "max": 4000, "default": 2000},
            "timeout": {"min": 300, "max": 1800, "default": 1800},
        },
    },
    "ollama": {
        "model_type": "chat",
        "location": "local",
        "provider_class": "dspy.OllamaProvider",
        "default": True,  # Mark as default provider
        "port": 11434,
        "kwargs": {
            "temperature": {"min": 0.0, "max": 2.0, "default": 0.7},
            "max_tokens": {"min": 100, "max": 4000, "default": 2000},
            "top_p": {"min": 0.0, "max": 1.0, "default": 1.0},
            "repeat_penalty": {"min": 1.0, "max": 2.0, "default": 1.1},
        },
    },
    "mlx": {
        "model_type": "chat",
        "location": "local",
        "provider_class": "dspy.MLXProvider",
        "port": 8000,
        "kwargs": {
            "temperature": {"min": 0.0, "max": 2.0, "default": 0.7},
            "max_tokens": {"min": 100, "max": 4000, "default": 2000},
        },
    },
    "lmstudio": {
        "model_type": "chat",
        "location": "local",
        "provider_class": "dspy.LMStudioProvider",
        "port": 1234,
        "kwargs": {
            "temperature": {"min": 0.0, "max": 2.0, "default": 0.7},
            "max_tokens": {"min": 100, "max": 4000, "default": 2000},
            "top_p": {"min": 0.0, "max": 1.0, "default": 1.0},
        },
    },
}

# Update the DSPY_METRICS with more comprehensive evaluation metrics
DSPY_METRICS = {
    "accuracy": "Basic correctness of the output",
    "exact_match": "Exact string matching with expected output",
    "f1_score": "Balance between precision and recall",
    "rouge_score": "Text summarization quality metrics",
    "bleu_score": "Translation quality metric",
    "bertscore": "Semantic similarity using BERT embeddings",
    "faithfulness": "Output's faithfulness to input facts",
    "coherence": "Logical flow and consistency",
    "relevance": "Output relevance to the input query",
    "toxicity": "Detect harmful or inappropriate content",
    "hallucination": "Check for made-up information",
}

# Add evaluation categories for better organization
EVALUATION_CATEGORIES = {
    "robustness": {
        "name": "Robustness Testing",
        "description": "Test agent behavior under various conditions",
        "examples": [
            "Input with typos or misspellings",
            "Incomplete or ambiguous queries",
            "Multiple topics in one query",
            "Very long or very short inputs",
        ],
    },
    "safety": {
        "name": "Safety Testing",
        "description": "Verify agent handles sensitive scenarios appropriately",
        "examples": [
            "Harmful or toxic content",
            "Personal information requests",
            "Controversial topics",
            "Adversarial prompts",
        ],
    },
    "quality": {
        "name": "Output Quality",
        "description": "Assess the quality of agent responses",
        "examples": [
            "Factual accuracy",
            "Response completeness",
            "Format consistency",
            "Citation of sources",
        ],
    },
    "edge_cases": {
        "name": "Edge Cases",
        "description": "Test boundary conditions and special cases",
        "examples": [
            "Empty or null inputs",
            "Maximum length inputs",
            "Special characters",
            "Non-standard formats",
        ],
    },
}

# First, add DSPy-specific evaluation configurations at the top
DSPY_EVALUATION_TYPES = {
    "basic": {
        "name": "Basic Metrics",
        "metrics": ["exact_match", "f1_score"],
        "description": "Simple evaluation using exact match and F1 score",
    },
    "text": {
        "name": "Text Metrics",
        "metrics": ["rouge_score", "bleurt_score", "bertscore"],
        "description": "Advanced NLP metrics for text generation",
    },
}

# Update the constants at the top
LITELLM_PROVIDERS = {
    "cloud": {
        "default": "openai",
        "examples": [
            "openai",
            "anthropic",
            "azure",
            "cohere",
            "amazon/bedrock",
            "google/vertex-ai",
            "mistral",
        ],
    },
    "local": {
        "default": "ollama",
        "examples": ["ollama", "vllm", "together-ai", "deepinfra", "lmstudio", "palm"],
    },
}

# Add supported input/output types
SUPPORTED_FORMATS = [
    "text",
    "markdown",
    "json",
    "csv",
    "image",
    "audio",
    "video",
    "binary",
    "embeddings",
    "vector",
    "table",
]

# Update the EXAMPLE_CONFIGS with simpler templates
EXAMPLE_CONFIGS = {
    "research": {
        "persona": {
            "name": "ResearchGPT",
            "role": "Research Assistant",
            "goal": "Create research summaries",
            "job_description": "Research topics, write summaries, find insights",
            "audience": "academic",
            "traits": "analytical\norganized\nprecise",
            "backstory": "Expert at summarizing research topics",
        },
        "task": {
            "name": "research_summary",
            "description": "Create research summaries with main points and key findings",
            "input_config": [{"name": "topic", "type": "text"}],
            "output_config": [{"name": "summary", "type": "markdown"}],
            "example_input": "What are the main uses of AI in healthcare?",
            "example_output": """AI in Healthcare:
1. Diagnosis accuracy
2. Patient monitoring
3. Treatment plans""",
        },
        "evaluation": {
            "metrics": ["exact_match", "f1_score"],
            "num_shots": 3,
            "threshold": 0.80,
            "edge_cases": [
                {
                    "scenario": "Complex Query",
                    "input": "Compare AI in healthcare vs finance",
                    "expected_output": "Should provide comparison and key differences",
                },
                {
                    "scenario": "Ambiguous Request",
                    "input": "Explain AI impact",
                    "expected_output": "Should ask for clarification and scope",
                },
            ],
        },
    },
    "sentiment": {
        "persona": {
            "name": "SentimentGPT",
            "role": "Sentiment Analyzer",
            "goal": "Analyze text sentiment",
            "job_description": "Detect sentiment and rate confidence",
            "audience": "business",
            "traits": "accurate\nreliable\nconsistent",
            "backstory": "Expert in sentiment analysis",
        },
        "task": {
            "name": "sentiment_analysis",
            "description": "Analyze sentiment and provide confidence scores",
            "input_config": [{"name": "text", "type": "text"}],
            "output_config": [{"name": "sentiment", "type": "text"}],
            "example_input": "This new feature is amazing!",
            "example_output": "Positive (90%)",
        },
        "evaluation": {
            "metrics": ["exact_match", "f1_score"],
            "num_shots": 3,
            "threshold": 0.80,
            "edge_cases": [
                {
                    "scenario": "Mixed Sentiment",
                    "input": "Good features but poor performance",
                    "expected_output": "Should detect mixed emotions",
                },
                {
                    "scenario": "Sarcasm",
                    "input": "Just what I needed, another error",
                    "expected_output": "Should identify sarcastic tone",
                },
            ],
        },
    },
}


# Update initialize_session_state to include DSPy-specific fields
def initialize_session_state(agent_name: str, level: str):
    """Initialize session state with all required variables."""
    if "step" not in st.session_state:
        st.session_state.step = 0

    # Add gold_examples initialization
    if "gold_examples" not in st.session_state:
        st.session_state.gold_examples = [{"input": "", "output": ""}]

    # Add input/output count initialization
    if "num_inputs" not in st.session_state:
        st.session_state.num_inputs = 1

    if "num_outputs" not in st.session_state:
        st.session_state.num_outputs = 1

    # Initialize all task-related session state variables
    if "output_format" not in st.session_state:
        st.session_state.output_format = "Markdown"

    if "task_name" not in st.session_state:
        st.session_state.task_name = "research_task"

    if "task_description" not in st.session_state:
        st.session_state.task_description = "Analyze topics and create summaries"

    if "task_output_desc" not in st.session_state:
        st.session_state.task_output_desc = "A structured summary with key findings"

    if "examples" not in st.session_state:
        st.session_state.examples = [{"topic": "", "summary": ""}]

    if "form_data" not in st.session_state:
        st.session_state.form_data = {
            "metadata": {
                "name": agent_name,
                "namespace": "default",
                "version": "0.0.1",
                "stage": "alpha",
                "level": level,
                "replicas": 1,
                "agent_type": "Autonomous",
            },
            "spec": {
                "components": {
                    "llms": {
                        "provider": "ollama",
                        "model": "llama3.2:1b",
                        "location": "local",
                        "config": {
                            "temperature": 0.7,
                            "max_tokens": 2000,
                            "api_base": "http://localhost:11434",
                        },
                    },
                    "persona": {
                        "name": "",
                        "role": "Research Assistant",
                        "goal": "Analyze research topics and provide comprehensive summaries",
                        "job_description": "Conduct research and generate well-structured summaries",
                        "audience": "technical",
                        "traits": ["analytical", "thorough", "detail-oriented"],
                        "backstory": "",
                    },
                    "tasks": [
                        {
                            "name": "research_task",
                            "description": "Analyze topics and create summaries",
                            "inputs": [],  # Will be populated from user input
                            "outputs": [],  # Will be populated from user input
                            "golden_examples": [],
                        }
                    ],
                    "evaluation": {
                        "metrics": ["exact_match", "f1_score"],
                        "num_shots": 3,
                        "threshold": 0.80,
                        "edge_cases": [
                            {
                                "scenario": "Mixed sentiment text: The interface is beautiful and user-friendly, but the system is extremely slow and crashes frequently.",
                                "expected": "Should:\n- Identify mixed sentiment\n- Weight different aspects\n- Provide balanced analysis\n- Include confidence scores\n- Note contradicting elements",
                            },
                            {
                                "scenario": "Sarcastic text: Oh great, another fantastic update that breaks everything. Just what we needed!",
                                "expected": "Should:\n- Detect sarcasm\n- Identify true negative sentiment\n- Note linguistic markers\n- Consider context\n- Provide confidence level",
                            },
                        ],
                    },
                }
            },
        }

    if "threshold" not in st.session_state:
        st.session_state.threshold = 0.8

    if "evaluation_frequency" not in st.session_state:
        st.session_state.evaluation_frequency = 24


def save_playbook(playbook: dict) -> Path:
    """Save playbook to file system."""
    # Add API version header
    playbook_with_header = {"apiVersion": "agentic/v1", "kind": "Playbook", **playbook}

    agent_name = playbook["metadata"]["name"].lower()
    project_root = Path.cwd()
    system_name = project_root.name

    playbook_dir = project_root / f"{system_name}" / "agents" / agent_name / "playbook"
    playbook_dir.mkdir(parents=True, exist_ok=True)

    playbook_path = playbook_dir / f"{agent_name}_playbook.yaml"
    with open(playbook_path, "w") as f:
        yaml.dump(playbook_with_header, f, sort_keys=False)

    return playbook_path


def build_model_config(provider, model, location, config):
    """Build model configuration without provider class."""
    return {
        "provider": provider,
        "model": model,
        "model_type": DSPY_LM_CONFIGS[provider]["model_type"],
        "location": location,
        "config": config,
    }


def render_dspy_signature_config(col1, col2):
    """Render DSPy signature configuration."""
    with col1:
        st.selectbox(
            "Module Type",
            options=list(DSPY_MODULE_TYPES.keys()),
            key="dspy_module_type",
            help="Select DSPy module type for implementation",
        )

        if st.session_state.dspy_module_type:
            st.info(
                f"📝 {DSPY_MODULE_TYPES[st.session_state.dspy_module_type]['description']}"
            )

    with col2:
        st.selectbox(
            "Input Type",
            options=list(DSPY_SIGNATURE_TYPES.keys()),
            key="input_type",
            help="Type hint for DSPy Signature",
        )

        st.selectbox(
            "Output Type",
            options=list(DSPY_SIGNATURE_TYPES.keys()),
            key="output_type",
            help="Type hint for DSPy Signature",
        )


# Update the clean_text function to better handle cleaning
def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and special characters."""
    if isinstance(text, str):
        # Remove special characters except basic punctuation
        cleaned = "".join(char for char in text if char.isprintable())
        # Normalize whitespace
        cleaned = " ".join(
            line.strip() for line in cleaned.splitlines() if line.strip()
        )
        return cleaned
    return text


# Update how persona traits are processed
def process_traits(traits_text: str) -> list:
    """Process traits string into a clean list."""
    if isinstance(traits_text, str):
        return [trait.strip() for trait in traits_text.splitlines() if trait.strip()]
    return traits_text if isinstance(traits_text, list) else []


def process_examples(examples: list) -> list:
    """Process and clean gold examples."""
    return [
        {"input": clean_text(example["input"]), "output": clean_text(example["output"])}
        for example in examples
        if example["input"].strip() and example["output"].strip()
    ]


def process_edge_cases(cases: list) -> list:
    """Process and clean edge cases."""
    return [
        {
            "scenario": clean_text(case["scenario"]),
            "input": clean_text(case["input"]),
            "expected_output": clean_text(case["expected_output"]),
        }
        for case in cases
        if case["scenario"].strip()
        and case["input"].strip()
        and case["expected_output"].strip()
    ]


def generate_gherkin_playbook(playbook: dict) -> str:
    """Generate Gherkin format playbook following best practices."""
    try:
        persona = playbook["spec"]["components"]["persona"]
        task = playbook["spec"]["components"]["tasks"][0]
        llm = playbook["spec"]["components"]["llms"]
        eval_config = playbook["spec"]["components"].get("evaluation", {})

        gherkin = f"""@agent
Feature: {playbook["metadata"]["name"]}
  As a {persona.get("role", "Agent")}
  I want to {persona.get("goal", "complete tasks")}
  So that I can assist {persona.get("audience", "users")} effectively

  @setup
  Background: Agent Configuration
    Given I am configured with the following LLM settings:
      | Provider    | {llm.get("provider", "default")} |
      | Model      | {llm.get("model", "default")}    |
      | Location   | {llm.get("location", "local")}   |
    And I have the following personality traits:
      | Trait | Description |
"""
        # Add traits and job descriptions
        traits = persona.get("traits", [])
        job_desc = persona.get("job_description", "").split("\n")
        for i, trait in enumerate(traits):
            desc = job_desc[i].strip() if i < len(job_desc) else ""
            gherkin += f"      | {trait} | {desc} |\n"

        # Add task definition
        gherkin += f"""
  @task
  Scenario: {task.get("name", "Default Task")}
    Given I receive a task request
    When I process the input of type "{task.get("inputs", [{}])[0].get("type", "text")}"
    Then I should generate output of type "{task.get("outputs", [{}])[0].get("type", "text")}"
    And ensure the response meets the following criteria:
      | Requirement | Description |
"""
        # Add task description as requirements
        for req in task.get("description", "").split("\n"):
            if req.strip():
                gherkin += (
                    f"      | {req.strip().replace('- ', '')} | Must be satisfied |\n"
                )

        # Add examples if present
        if task.get("golden_examples"):
            gherkin += "\n    Examples:\n      | Input | Expected Output |\n"
            for example in task.get("golden_examples", []):
                input_text = example.get("input", "").replace("\n", " ")[:50]
                output_text = example.get("output", "").replace("\n", " ")[:50]
                gherkin += f"      | {input_text} | {output_text} |\n"

        # Add evaluation criteria
        gherkin += f"""
  @evaluation
  Rule: Quality Standards
    Background:
      Given evaluation metrics are configured:
        | Metric    | Threshold |
        | {" | ".join(eval_config.get("metrics", ["exact_match"]))} | {eval_config.get("threshold", 0.8)} |
      And using {eval_config.get("num_shots", 3)} examples for few-shot learning

"""
        # Add edge cases
        if eval_config.get("edge_cases"):
            gherkin += "    @edge_cases\n"
            for case in eval_config.get("edge_cases", []):
                gherkin += f"""    Scenario: {case.get("scenario", "Edge Case")}
      Given the challenging input "{case.get("input", "")}"
      When processing the edge case
      Then the output should satisfy:
"""
                for req in case.get("expected_output", "").split("\n"):
                    if req.strip():
                        gherkin += f"        * {req.strip().replace('- ', '')}\n"
                gherkin += "\n"

        return gherkin

    except Exception as e:
        return f"Error generating Gherkin: {str(e)}\nPlease ensure all required fields are filled."


# Update the YAML generation in the final review
def generate_clean_yaml(playbook: dict) -> str:
    """Generate clean YAML without empty fields and extra whitespace."""

    def clean_dict(d: dict) -> dict:
        if not isinstance(d, dict):
            if isinstance(d, str):
                return clean_text(d)
            return d
        return {
            k: clean_dict(v) if isinstance(v, (dict, str)) else v
            for k, v in d.items()
            if v not in (None, "", [], {})
        }

    cleaned_playbook = clean_dict(playbook)
    return yaml.dump(
        cleaned_playbook,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
        width=80,
        indent=2,
    ).strip()


def main(agent_name: str, level: str):
    """Main UI function with CLI provided agent details."""
    st.set_page_config(
        page_title=f"🤖 {agent_name.title()} Agent Designer", layout="wide"
    )

    initialize_session_state(agent_name, level)

    # Main header with agent info
    st.title(f"🤖 {agent_name.title()} Agent Designer")

    # Step headers with professional emojis
    steps = {
        0: "📝 Agent Metadata",
        1: "🤖 LLM Configuration",
        2: "👤 Persona Design",
        3: "📋 Task Definition",
        4: "🧪 Evaluation Setup",
        5: "🔍 Final Review",
    }

    # Show progress
    st.progress(st.session_state.step / (len(steps) - 1))

    # Show current step header
    st.header(f"Step {st.session_state.step + 1}: {steps[st.session_state.step]}")

    # Step-specific UI sections with navigation
    if st.session_state.step == 0:
        st.markdown("""
        ### Welcome to the Agent Designer!

        Let's create your agent in 5 easy steps:
        1. 🤖 Configure the Language Model
        2. 👤 Design the Agent Persona
        3. 📋 Define Tasks and Examples
        4. 🧪 Set up Evaluation
        5. 🔍 Review and Generate
        """)

        # Add Agent Metadata Configuration
        st.markdown("### 📝 Agent Metadata")
        col1, col2 = st.columns(2)

        with col1:
            st.text_input(
                "Name",
                value=st.session_state.form_data["metadata"]["name"],
                key="agent_name",
                help="Name of your agent",
            )

            st.text_input(
                "Namespace",
                value=st.session_state.form_data["metadata"]["namespace"],
                key="namespace",
                help="Namespace for the agent",
            )

            st.text_input(
                "Version",
                value=st.session_state.form_data["metadata"]["version"],
                key="version",
                help="Version number (e.g., 0.0.1)",
            )

        with col2:
            st.selectbox(
                "Stage",
                options=["alpha", "beta", "production"],
                index=0,
                key="stage",
                help="Development stage of the agent",
            )

            st.selectbox(
                "Level",
                options=["basic", "intermediate", "advanced"],
                key="level",
                help="Complexity level of the agent",
            )

            st.number_input(
                "Replicas",
                min_value=1,
                max_value=10,
                value=st.session_state.form_data["metadata"]["replicas"],
                key="replicas",
                help="Number of agent replicas",
            )

        # Update metadata in form_data
        st.session_state.form_data["metadata"].update(
            {
                "name": st.session_state.agent_name,
                "namespace": st.session_state.namespace,
                "version": st.session_state.version,
                "stage": st.session_state.stage,
                "level": st.session_state.level,
                "replicas": st.session_state.replicas,
            }
        )

        col1, col2 = st.columns(2)
        with col2:
            if st.button("Next ➡️", key="nav_next_0", type="primary"):
                st.session_state.step += 1
                st.rerun()

    elif st.session_state.step == 1:
        # Provider Selection
        col1, col2 = st.columns(2)

        with col1:
            location = st.selectbox(
                "Model Location *",
                options=["local", "cloud"],
                key="model_location",
                help="Choose between local and cloud-based models",
            )

            provider_help = """Enter provider name from supported providers:
For cloud: openai, anthropic, azure, cohere
For local: ollama, vllm, lmstudio"""

            st.text_input(
                "LM Provider *",
                value=LITELLM_PROVIDERS[location]["default"],
                key="llm_provider",
                help=provider_help,
            )

        with col2:
            st.text_input(
                "Model Name *",
                value="llama3.2:1b",
                key="model_name",
                help="Enter model name (e.g., llama3.2:1b)",
            )

            st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=0.7,
                step=0.1,
                key="temperature",
                help="Adjust temperature for response randomness",
            )

            st.number_input(
                "Max Tokens",
                min_value=100,
                max_value=4000,
                value=2000,
                step=100,
                key="max_tokens",
                help="Set maximum number of tokens for response",
            )

        # Update LLM configuration in form_data
        st.session_state.form_data["spec"]["components"]["llms"].update(
            {
                "provider": st.session_state.llm_provider,
                "model": st.session_state.model_name,
                "location": st.session_state.model_location,
                "config": {
                    "temperature": st.session_state.temperature,
                    "max_tokens": st.session_state.max_tokens,
                },
            }
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Previous", key="nav_prev_1"):
                st.session_state.step -= 1
                st.rerun()
        with col2:
            if st.button("Next ➡️", key="nav_next_1", type="primary"):
                st.session_state.step += 1
                st.rerun()

    elif st.session_state.step == 2:  # Persona Design
        st.markdown("### 👤 Persona Configuration")

        # Add example buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown("Choose a template or create custom:")
        with col2:
            if st.button("📚 Research Assistant"):
                example = EXAMPLE_CONFIGS["research"]["persona"]
                st.session_state.persona_name = example["name"]
                st.session_state.persona_role = example["role"]
                st.session_state.persona_goal = example["goal"]
                st.session_state.persona_job_description = example["job_description"]
                st.session_state.persona_audience = example["audience"]
                st.session_state.persona_traits = example["traits"]
                st.session_state.persona_backstory = example["backstory"]
                st.rerun()
        with col3:
            if st.button("😊 Sentiment Analyzer"):
                example = EXAMPLE_CONFIGS["sentiment"]["persona"]
                st.session_state.persona_name = example["name"]
                st.session_state.persona_role = example["role"]
                st.session_state.persona_goal = example["goal"]
                st.session_state.persona_job_description = example["job_description"]
                st.session_state.persona_audience = example["audience"]
                st.session_state.persona_traits = example["traits"]
                st.session_state.persona_backstory = example["backstory"]
                st.rerun()

        # Update persona state when template is selected
        if "persona_name" not in st.session_state:
            st.session_state.persona_name = ""
        if "persona_role" not in st.session_state:
            st.session_state.persona_role = ""
        if "persona_goal" not in st.session_state:
            st.session_state.persona_goal = ""
        if "persona_job_description" not in st.session_state:
            st.session_state.persona_job_description = ""
        if "persona_audience" not in st.session_state:
            st.session_state.persona_audience = "technical"
        if "persona_traits" not in st.session_state:
            st.session_state.persona_traits = ""
        if "persona_backstory" not in st.session_state:
            st.session_state.persona_backstory = ""

        # Persona form fields in two columns
        col1, col2 = st.columns(2)

        with col1:
            st.text_input(
                "Name",
                key="persona_name",
                value=st.session_state.form_data["spec"]["components"]["persona"][
                    "name"
                ],
                help="Name of the agent persona",
            )

            st.text_input(
                "Role",
                key="persona_role",
                value=st.session_state.form_data["spec"]["components"]["persona"][
                    "role"
                ],
                help="Role of the agent (e.g., Research Assistant)",
            )

            st.text_area(
                "Goal",
                key="persona_goal",
                value=st.session_state.form_data["spec"]["components"]["persona"][
                    "goal"
                ],
                help="Main objective of the agent",
            )

        with col2:
            st.text_area(
                "Job Description",
                key="persona_job_description",
                value=st.session_state.form_data["spec"]["components"]["persona"][
                    "job_description"
                ],
                help="Key responsibilities and tasks",
            )

            st.selectbox(
                "Audience",
                options=["technical", "business", "academic", "general"],
                key="persona_audience",
                help="Target audience for the agent",
            )

            st.text_area(
                "Traits",
                key="persona_traits",
                value="\n".join(
                    st.session_state.form_data["spec"]["components"]["persona"][
                        "traits"
                    ]
                ),
                help="Key characteristics (one per line)",
            )

            st.text_area(
                "Backstory",
                key="persona_backstory",
                value=st.session_state.form_data["spec"]["components"]["persona"][
                    "backstory"
                ],
                help="Background and experience",
            )

        # Update form data with persona configuration
        traits = process_traits(st.session_state.persona_traits)
        st.session_state.form_data["spec"]["components"]["persona"].update(
            {
                "name": clean_text(st.session_state.persona_name),
                "role": clean_text(st.session_state.persona_role),
                "goal": clean_text(st.session_state.persona_goal),
                "job_description": clean_text(st.session_state.persona_job_description),
                "audience": st.session_state.persona_audience,
                "traits": traits,
                "backstory": clean_text(st.session_state.persona_backstory),
            }
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Previous", key="nav_prev_2"):
                st.session_state.step -= 1
                st.rerun()
        with col2:
            if st.button("Next ➡️", key="nav_next_2", type="primary"):
                st.session_state.step += 1
                st.rerun()

    elif st.session_state.step == 3:  # Task Definition
        st.markdown("### 📋 Task Configuration")

        # Add example buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown("Choose a template or create custom:")
        with col2:
            if st.button("📚 Research Task"):
                example = EXAMPLE_CONFIGS["research"]["task"]
                st.session_state.task_name = example["name"]
                st.session_state.task_description = example["description"]
                st.session_state.input_name_0 = example["input_config"][0]["name"]
                st.session_state.input_type_0 = example["input_config"][0]["type"]
                st.session_state.output_name_0 = example["output_config"][0]["name"]
                st.session_state.output_type_0 = example["output_config"][0]["type"]
                st.session_state.gold_examples = [
                    {
                        "input": example["example_input"],
                        "output": example["example_output"],
                    }
                ]
                st.rerun()
        with col3:
            if st.button("😊 Sentiment Task"):
                example = EXAMPLE_CONFIGS["sentiment"]["task"]
                st.session_state.task_name = example["name"]
                st.session_state.task_description = example["description"]
                st.session_state.input_name_0 = example["input_config"][0]["name"]
                st.session_state.input_type_0 = example["input_config"][0]["type"]
                st.session_state.output_name_0 = example["output_config"][0]["name"]
                st.session_state.output_type_0 = example["output_config"][0]["type"]
                st.session_state.gold_examples = [
                    {
                        "input": example["example_input"],
                        "output": example["example_output"],
                    }
                ]
                st.rerun()

        # Basic Task Info
        st.text_input(
            "Task Name *",
            key="task_name",
            help="Name of the task (e.g., research_analysis, sentiment_analysis)",
        )

        st.text_area(
            "Task Description *",
            key="task_description",
            help="Detailed description of what the task does",
        )

        # Input/Output Configuration
        st.markdown("#### 🔄 Input/Output Configuration")

        # Input Configuration
        st.markdown("##### 📥 Input Configuration")
        col1, col2 = st.columns(2)

        with col1:
            input_name = st.text_input(
                "Input Name *",
                key="input_name_0",
                placeholder="e.g., topic, query, text",
                help="Name of the input field",
            )

        with col2:
            input_type = st.selectbox(
                "Input Type *",
                options=SUPPORTED_FORMATS,
                key="input_type_0",
                help="Data type for input",
            )

        # Output Configuration
        st.markdown("##### 📤 Output Configuration")
        col1, col2 = st.columns(2)

        with col1:
            output_name = st.text_input(
                "Output Name *",
                key="output_name_0",
                placeholder="e.g., summary, analysis, result",
                help="Name of the output field",
            )

        with col2:
            output_type = st.selectbox(
                "Output Type *",
                options=SUPPORTED_FORMATS,
                key="output_type_0",
                help="Data type for output",
            )

        # Gold Examples
        st.markdown("#### 🌟 Gold Examples")

        if "gold_examples" not in st.session_state:
            st.session_state.gold_examples = [{"input": "", "output": ""}]

        for idx, example in enumerate(st.session_state.gold_examples):
            with st.expander(f"Example {idx + 1}", expanded=True):
                example["input"] = st.text_area(
                    "Input *",
                    value=example["input"],
                    key=f"example_input_{idx}",
                    help="Enter your input example here",
                )

                example["output"] = st.text_area(
                    "Expected Output *",
                    value=example["output"],
                    key=f"example_output_{idx}",
                    help="Enter your expected output here",
                )

        # Add/Remove example buttons
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("➕ Add Example"):
                st.session_state.gold_examples.append({"input": "", "output": ""})
                st.rerun()

            if len(st.session_state.gold_examples) > 1:
                if st.button("➖ Remove Last"):
                    st.session_state.gold_examples.pop()
                    st.rerun()

        # Update task data in form_data
        task_data = {
            "name": st.session_state.task_name,
            "description": st.session_state.task_description,
            "inputs": [{"name": input_name, "type": input_type}] if input_name else [],
            "outputs": [{"name": output_name, "type": output_type}]
            if output_name
            else [],
            "golden_examples": st.session_state.gold_examples,
        }

        # Update form data with task configuration
        st.session_state.form_data["spec"]["components"]["tasks"] = [task_data]

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Previous", key="nav_prev_3"):
                st.session_state.step -= 1
                st.rerun()
        with col2:
            if st.button("Next ➡️", key="nav_next_3", type="primary"):
                st.session_state.step += 1
                st.rerun()

    elif st.session_state.step == 4:  # Evaluation Setup
        st.markdown("### 🧪 Evaluation Configuration")

        # Evaluation Overview
        st.info("""
        ### Industry Best Practices for LLM Evaluation

        1. **Comprehensive Testing**: Test across multiple dimensions including accuracy, safety, and robustness
        2. **Automated Evaluation**: Use automated metrics alongside human evaluation
        3. **Continuous Monitoring**: Regular evaluation as model/data changes
        4. **Diverse Test Sets**: Include various scenarios and edge cases
        5. **Clear Success Criteria**: Define acceptable performance thresholds
        """)

        # Metrics Selection with Categories
        st.markdown("#### 📊 Evaluation Metrics")
        col1, col2 = st.columns(2)
        with col1:
            selected_metrics = st.multiselect(
                "Select Evaluation Metrics",
                options=list(DSPY_METRICS.keys()),
                default=["accuracy", "faithfulness", "coherence"],
                help="Choose metrics for evaluating agent performance",
            )
            if selected_metrics:
                st.info("Selected metrics explanation:")
                for metric in selected_metrics:
                    st.write(f"- **{metric}**: {DSPY_METRICS[metric]}")

        with col2:
            st.session_state.evaluation_frequency = st.number_input(
                "Evaluation Frequency (hours)",
                min_value=1,
                max_value=168,
                value=24,
                help="How often to run automated evaluations",
            )

            st.session_state.threshold = st.slider(
                "Acceptance Threshold",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.threshold,
                help="Minimum score required for each metric",
            )

        # Test Cases by Category
        st.markdown("#### 🎯 Test Cases by Category")
        for category, details in EVALUATION_CATEGORIES.items():
            with st.expander(f"{details['name']}", expanded=True):
                st.markdown(f"**{details['description']}**")

                # Add test cases for this category
                if f"test_cases_{category}" not in st.session_state:
                    st.session_state[f"test_cases_{category}"] = [
                        {
                            "scenario": "",
                            "input": "",
                            "expected_output": "",
                            "success_criteria": "",
                        }
                    ]

                for idx, case in enumerate(st.session_state[f"test_cases_{category}"]):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        case["scenario"] = st.text_input(
                            "Test Scenario",
                            value=case["scenario"],
                            key=f"{category}_scenario_{idx}",
                            help="Description of what you're testing",
                        )
                    with col2:
                        st.markdown("Example scenarios:")
                        st.markdown("\n".join(f"- {ex}" for ex in details["examples"]))

                    case["input"] = st.text_area(
                        "Test Input",
                        value=case["input"],
                        key=f"{category}_input_{idx}",
                        help="Input to test the agent",
                    )

                    case["expected_output"] = st.text_area(
                        "Expected Behavior",
                        value=case["expected_output"],
                        key=f"{category}_output_{idx}",
                        help="What the agent should do",
                    )

                    case["success_criteria"] = st.text_input(
                        "Success Criteria",
                        value=case.get("success_criteria", ""),
                        key=f"{category}_criteria_{idx}",
                        help="How to determine if the test passed",
                    )

                # Add/Remove test case buttons
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(f"Add {details['name']}", key=f"add_{category}"):
                        st.session_state[f"test_cases_{category}"].append(
                            {
                                "scenario": "",
                                "input": "",
                                "expected_output": "",
                                "success_criteria": "",
                            }
                        )
                        st.rerun()

        # Combine all test cases for form_data
        all_test_cases = []
        for category in EVALUATION_CATEGORIES.keys():
            all_test_cases.extend(st.session_state[f"test_cases_{category}"])

        # Update form data
        st.session_state.form_data["spec"]["components"]["evaluation"].update(
            {
                "metrics": selected_metrics,
                "threshold": st.session_state.threshold,
                "test_cases": all_test_cases,
                "evaluation_frequency": st.session_state.evaluation_frequency,
            }
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Previous", key="nav_prev_4"):
                st.session_state.step -= 1
                st.rerun()
        with col2:
            if st.button("Next ➡️", key="nav_next_4", type="primary"):
                st.session_state.step += 1
                st.rerun()

    elif st.session_state.step == 5:  # Final Review
        st.markdown("### 🔍 Final Review")

        # Create playbook with header
        playbook_with_header = {
            "apiVersion": "agentic/v1",
            "kind": "Playbook",
            **st.session_state.form_data,
        }

        # Show both YAML and Gherkin formats
        tab1, tab2 = st.tabs(["📄 YAML Format", "🥒 Gherkin Format"])

        with tab1:
            st.code(generate_clean_yaml(playbook_with_header), language="yaml")

        with tab2:
            st.code(generate_gherkin_playbook(playbook_with_header), language="gherkin")

        # Navigation buttons for final review
        col1, col2 = st.columns(2)

        with col1:
            if st.button("⬅️ Previous", key="nav_prev_5"):
                st.session_state.step -= 1
                st.rerun()

        with col2:
            if st.button(
                "Generate Playbook 🚀", key="generate_playbook", type="primary"
            ):
                try:
                    playbook_path = save_playbook(st.session_state.form_data)
                    st.success(f"""
                    ### ✨ Agent Created Successfully!

                    Your new agent has been configured and saved at: `{playbook_path}`

                    #### 🚀 Next Steps:

                    1. **Validate the Playbook**
                    ```bash
                    soda agent validate --name {st.session_state.form_data["metadata"]["name"]}
                    ```

                    2. **Deploy the Agent**
                    ```bash
                    soda agent deploy --name {st.session_state.form_data["metadata"]["name"]}
                    ```

                    3. **Test the Agent**
                    ```bash
                    soda agent evaluate --name {st.session_state.form_data["metadata"]["name"]}
                    ```

                    4. **Monitor Logs**
                    ```bash
                    soda agent logs --name {st.session_state.form_data["metadata"]["name"]}
                    ```

                    5. **Get Help**
                    ```bash
                    soda agent --help
                    ```

                    For more information, visit our documentation at: https://docs.super.dev
                    """)
                except Exception as e:
                    st.error(f"❌ Failed to generate playbook: {str(e)}")


# Add this at the bottom of the file after all function definitions:
if __name__ == "__main__":
    import sys

    # Get agent name and level from command line arguments
    if len(sys.argv) < 3:
        print("Usage: streamlit run intern_designer.py <agent_name> <level>")
        sys.exit(1)

    agent_name = sys.argv[1]
    level = sys.argv[2]

    # Run the Streamlit app
    main(agent_name, level)
