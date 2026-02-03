"""
SuperSpec Generator

Generates agent playbook templates based on the SuperSpec DSL specification.
Provides templates for Oracles and Genies tiers with appropriate configurations.
"""

import yaml
from typing import Dict, List, Any
from datetime import datetime
from .schema import SuperSpecXSchema


class SuperSpecXGenerator:
    """Generator for SuperSpec DSL playbook templates."""

    def __init__(self):
        """Initialize the generator."""
        self.schema = SuperSpecXSchema()

    def generate_oracles_template(
        self,
        name: str,
        namespace: str = "software",
        description: str = None,
        role: str = "Assistant",
        task_name: str = "main_task",
    ) -> Dict[str, Any]:
        """
        Generate an Oracles tier agent template.

        Args:
            name: Agent name
            namespace: Agent namespace
            description: Agent description
            role: Agent role
            task_name: Primary task name

        Returns:
            Oracles agent template
        """
        agent_id = name.lower().replace(" ", "-").replace("_", "-")
        timestamp = datetime.now().isoformat()

        template = {
            "apiVersion": "agent/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": name,
                "id": agent_id,
                "namespace": namespace,
                "version": "1.0.0",
                "level": "oracles",
                "stage": "alpha",
                "agent_type": "Autonomous",
                "description": description or f"Oracles tier {role.lower()} agent",
                "tags": [namespace, "oracles", "basic"],
                "created_at": timestamp,
            },
            "spec": {
                "language_model": {
                    "location": "local",
                    "provider": "ollama",
                    "model": "llama3.2:1b",
                    "api_base": "http://localhost:11434",
                    "temperature": 0.0,
                    "max_tokens": 4000,
                    "cache": True,
                },
                "persona": {
                    "name": f"{name}Bot",
                    "role": role,
                    "goal": f"Provide helpful assistance as a {role.lower()}",
                    "traits": ["analytical", "helpful", "professional"],
                    "communication_preferences": {
                        "style": "professional",
                        "tone": "friendly",
                        "verbosity": "concise",
                    },
                },
                "tasks": [
                    {
                        "name": task_name,
                        "description": f"Main task for {role.lower()}",
                        "instruction": f"You are a {role}. Provide helpful and accurate assistance.",
                        "schema": {
                            "style": "chain_of_thought",
                            "reasoning_traces": True,
                        },
                        "inputs": [
                            {
                                "name": "query",
                                "type": "str",
                                "description": "User query or request",
                                "required": True,
                            }
                        ],
                        "outputs": [
                            {
                                "name": "response",
                                "type": "str",
                                "description": "Assistant response",
                            }
                        ],
                    }
                ],
                "agentflow": [
                    {
                        "name": "think_and_respond",
                        "type": "Think",
                        "task": task_name,
                        "config": {"reasoning_depth": 2},
                    }
                ],
                "evaluation": {
                    "builtin_metrics": [
                        {"name": "answer_correctness", "threshold": 0.7}
                    ]
                },
                "optimization": {
                    "strategy": "few_shot_bootstrapping",
                    "metric": "answer_correctness",
                    "few_shot_bootstrapping_config": {
                        "max_bootstrapped_demos": 4,
                        "max_rounds": 1,
                    },
                },
                "runtime": {
                    "caching": {"enabled": True, "backend": "memory", "ttl": 3600},
                    "monitoring": {"log_level": "info", "metrics_collection": True},
                },
            },
        }

        return template

    def generate_genies_template(
        self,
        name: str,
        namespace: str = "software",
        description: str = None,
        role: str = "Intelligent Assistant",
        task_name: str = "solve_problem",
        enable_memory: bool = True,
        enable_tools: bool = True,
        enable_rag: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate a Genies tier agent template.

        Args:
            name: Agent name
            namespace: Agent namespace
            description: Agent description
            role: Agent role
            task_name: Primary task name
            enable_memory: Enable memory system
            enable_tools: Enable tool calling
            enable_rag: Enable RAG retrieval

        Returns:
            Genies agent template
        """
        agent_id = name.lower().replace(" ", "-").replace("_", "-")
        timestamp = datetime.now().isoformat()

        template = {
            "apiVersion": "agent/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": name,
                "id": agent_id,
                "namespace": namespace,
                "version": "1.0.0",
                "level": "genies",
                "stage": "alpha",
                "agent_type": "Autonomous",
                "description": description
                or f"Genies tier {role.lower()} with tools and memory",
                "tags": [namespace, "genies", "advanced"],
                "created_at": timestamp,
            },
            "spec": {
                "language_model": {
                    "location": "local",
                    "provider": "ollama",
                    "model": "llama3.2:3b",
                    "api_base": "http://localhost:11434",
                    "temperature": 0.1,
                    "max_tokens": 4000,
                    "cache": True,
                },
                "persona": {
                    "name": f"{name}Genies",
                    "role": role,
                    "goal": "Solve problems intelligently using available tools and knowledge",
                    "traits": ["intelligent", "resourceful", "adaptive", "helpful"],
                    "communication_preferences": {
                        "style": "conversational",
                        "tone": "friendly",
                        "verbosity": "adaptive",
                    },
                },
                "tasks": [
                    {
                        "name": task_name,
                        "description": "Intelligent problem solving with tools and memory",
                        "instruction": f"You are an intelligent {role.lower()}. Use your tools and memory to solve problems effectively.",
                        "schema": {
                            "style": "chain_of_thought",
                            "reasoning_traces": True,
                        },
                        "inputs": [
                            {
                                "name": "problem",
                                "type": "str",
                                "description": "Problem to solve or task to complete",
                                "required": True,
                            },
                            {
                                "name": "context",
                                "type": "dict[str,Any]",
                                "description": "Additional context or constraints",
                                "required": False,
                            },
                        ],
                        "outputs": [
                            {
                                "name": "solution",
                                "type": "str",
                                "description": "Problem solution or task completion",
                            },
                            {
                                "name": "reasoning",
                                "type": "str",
                                "description": "Step-by-step reasoning process",
                            },
                        ],
                    }
                ],
                "agentflow": [
                    {
                        "name": "analyze_problem",
                        "type": "Think",
                        "task": task_name,
                        "config": {"reasoning_depth": 3},
                    }
                ],
            },
        }

        # Add tools if enabled
        if enable_tools:
            template["spec"]["agentflow"].append(
                {
                    "name": "use_tools",
                    "type": "ActWithTools",
                    "task": task_name,
                    "depends_on": ["analyze_problem"],
                    "config": {"max_iters": 5, "tools": ["calculator", "web_search"]},
                }
            )

            template["spec"]["tool_calling"] = {
                "enabled": True,
                "available_tools": ["calculator", "web_search", "file_operations"],
                "tool_selection_strategy": "automatic",
                "max_tool_calls": 5,
                "builtin_tools": ["calculator", "web_search"],
            }
        else:
            template["spec"]["agentflow"].append(
                {
                    "name": "generate_solution",
                    "type": "Generate",
                    "task": task_name,
                    "depends_on": ["analyze_problem"],
                }
            )

        # Add memory if enabled
        if enable_memory:
            template["spec"]["memory"] = {
                "enabled": True,
                "agent_id": agent_id,
                "backend": {
                    "type": "sqlite",
                    "config": {"db_path": f".superoptix/{agent_id}_memory.db"},
                },
                "short_term": {
                    "enabled": True,
                    "capacity": 100,
                    "retention_policy": "lru",
                    "max_conversation_length": 50,
                },
                "long_term": {
                    "enabled": True,
                    "enable_embeddings": True,
                    "embedding_model": "all-MiniLM-L6-v2",
                },
                "episodic": {
                    "enabled": True,
                    "auto_start_episodes": True,
                    "episode_boundary": "interaction",
                },
            }

        # Add RAG if enabled
        if enable_rag:
            template["spec"]["retrieval"] = {
                "enabled": True,
                "retriever_type": "ChromaDB",
                "config": {"top_k": 5, "similarity_threshold": 0.7, "chunk_size": 512},
                "vector_store": {
                    "provider": "chromadb",
                    "collection_name": f"{agent_id}_knowledge",
                    "embedding_model": "all-MiniLM-L6-v2",
                },
            }

            # Add search step to agentflow
            template["spec"]["agentflow"].insert(
                1,
                {
                    "name": "search_knowledge",
                    "type": "Search",
                    "task": task_name,
                    "depends_on": ["analyze_problem"],
                    "config": {"retriever": "chromadb", "top_k": 5},
                },
            )

        # Add common configurations
        template["spec"].update(
            {
                "evaluation": {
                    "builtin_metrics": [
                        {"name": "answer_correctness", "threshold": 0.8},
                        {"name": "semantic_f1", "threshold": 0.7},
                    ]
                },
                "optimization": {
                    "strategy": "few_shot_bootstrapping",
                    "metric": "answer_correctness",
                    "few_shot_bootstrapping_config": {
                        "max_bootstrapped_demos": 6,
                        "max_rounds": 2,
                    },
                },
                "runtime": {
                    "caching": {"enabled": True, "backend": "memory", "ttl": 3600},
                    "monitoring": {
                        "log_level": "info",
                        "metrics_collection": True,
                        "performance_tracking": True,
                    },
                    "deployment": {"streaming": True, "async_mode": False},
                },
            }
        )

        return template

    def generate_custom_template(
        self, tier: str, name: str, namespace: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a custom template based on tier and parameters.

        Args:
            tier: Agent tier (oracles or genies)
            name: Agent name
            namespace: Agent namespace
            **kwargs: Additional customization parameters

        Returns:
            Custom agent template
        """
        if tier == "oracles":
            return self.generate_oracles_template(name, namespace, **kwargs)
        elif tier == "genies":
            return self.generate_genies_template(name, namespace, **kwargs)
        else:
            raise ValueError(f"Unsupported tier: {tier}")

    def save_template(
        self, template: Dict[str, Any], file_path: str, format: str = "yaml"
    ) -> bool:
        """
        Save a template to file.

        Args:
            template: Template dictionary
            file_path: Output file path
            format: Output format (yaml or json)

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                if format.lower() == "yaml":
                    yaml.dump(template, f, default_flow_style=False, indent=2)
                elif format.lower() == "json":
                    import json

                    json.dump(template, f, indent=2, ensure_ascii=False)
                else:
                    raise ValueError(f"Unsupported format: {format}")
            return True
        except Exception:
            return False

    def generate_namespace_templates(
        self, namespace: str, output_dir: str = ".", tiers: List[str] = None
    ) -> List[str]:
        """
        Generate templates for all common roles in a namespace.

        Args:
            namespace: Target namespace
            output_dir: Output directory
            tiers: List of tiers to generate (default: both)

        Returns:
            List of generated file paths
        """
        if tiers is None:
            tiers = ["oracles", "genies"]

        # Common roles per namespace
        namespace_roles = {
            "software": [
                ("Developer Assistant", "developer", "Helps with coding tasks"),
                ("Code Reviewer", "reviewer", "Reviews code for quality"),
                ("DevOps Engineer", "devops", "Manages deployment and infrastructure"),
            ],
            "education": [
                ("Math Tutor", "math_tutor", "Teaches mathematics concepts"),
                ("Writing Coach", "writing_coach", "Helps improve writing skills"),
                ("Study Assistant", "study_assistant", "Provides study guidance"),
            ],
            "healthcare": [
                (
                    "Medical Assistant",
                    "medical_assistant",
                    "Provides medical information",
                ),
                ("Health Coach", "health_coach", "Promotes healthy lifestyle"),
                ("Pharmacy Advisor", "pharmacy_advisor", "Advises on medications"),
            ],
        }

        roles = namespace_roles.get(
            namespace,
            [("General Assistant", "assistant", f"General {namespace} assistant")],
        )

        generated_files = []

        for role_name, role_id, description in roles:
            for tier in tiers:
                template = self.generate_custom_template(
                    tier=tier,
                    name=f"{role_name}",
                    namespace=namespace,
                    description=description,
                    role=role_name,
                )

                file_path = f"{output_dir}/{namespace}_{role_id}_{tier}_playbook.yaml"
                if self.save_template(template, file_path):
                    generated_files.append(file_path)

        return generated_files

    def validate_template(self, template: Dict[str, Any]) -> List[str]:
        """
        Validate a generated template.

        Args:
            template: Template to validate

        Returns:
            List of validation errors
        """
        from .validator import SuperSpecXValidator

        validator = SuperSpecXValidator()
        result = validator.validate(template)
        return result.get("errors", [])

    def get_template_info(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get information about a template.

        Args:
            template: Template to analyze

        Returns:
            Template information
        """
        metadata = template.get("metadata", {})
        spec = template.get("spec", {})

        # Count features
        features = []
        if "memory" in spec:
            features.append("memory")
        if "tool_calling" in spec:
            features.append("tools")
        if "retrieval" in spec:
            features.append("rag")
        if "agentflow" in spec:
            features.append("agentflow")

        return {
            "name": metadata.get("name", "Unknown"),
            "tier": metadata.get("level", "unknown"),
            "namespace": metadata.get("namespace", "unknown"),
            "features": features,
            "task_count": len(spec.get("tasks", [])),
            "agentflow_steps": len(spec.get("agentflow", [])),
            "has_persona": "persona" in spec,
            "has_optimization": "optimization" in spec,
            "has_evaluation": "evaluation" in spec,
        }

    def _generate_feature_specifications(
        self,
        namespace: str,
        role: str,
        tier: str,
        task_inputs: List[Dict],
        task_outputs: List[Dict],
    ) -> Dict:
        """Generate comprehensive BDD feature specifications with scenarios based on namespace and role."""

        # Create input/output field mappings from tasks
        input_fields = {
            inp["name"]: inp.get("description", "Input field") for inp in task_inputs
        }
        output_fields = {
            out["name"]: out.get("description", "Output field") for out in task_outputs
        }

        # Get the first input and output field names for scenario generation
        primary_input = list(input_fields.keys())[0] if input_fields else "query"
        primary_output = list(output_fields.keys())[0] if output_fields else "response"

        # Generate namespace-specific scenarios
        scenarios = self._generate_namespace_scenarios(
            namespace, role, primary_input, primary_output
        )

        # Add tier-specific scenarios
        if tier == "genies":
            scenarios.extend(
                self._generate_genies_scenarios(
                    namespace, role, primary_input, primary_output
                )
            )

        # Ensure we have at least 3 scenarios for optimization
        while len(scenarios) < 3:
            scenarios.append(
                self._generate_generic_scenario(
                    role, primary_input, primary_output, len(scenarios) + 1
                )
            )

        # Limit to max 8 scenarios to keep it manageable
        scenarios = scenarios[:8]

        return {"scenarios": scenarios}

    def _generate_namespace_scenarios(
        self, namespace: str, role: str, input_field: str, output_field: str
    ) -> List[Dict]:
        """Generate namespace-specific BDD scenarios."""
        scenarios = []

        if namespace == "software":
            scenarios = [
                {
                    "name": f"{role.lower()}_comprehensive_task",
                    "description": "Given a complex software requirement, the agent should provide detailed analysis and recommendations",
                    "input": {
                        input_field: "Complex software scenario requiring comprehensive analysis"
                    },
                    "expected_output": {
                        output_field: "Detailed step-by-step analysis with software-specific recommendations"
                    },
                },
                {
                    "name": f"{role.lower()}_problem_solving",
                    "description": "When facing software challenges, the agent should demonstrate systematic problem-solving approach",
                    "input": {
                        input_field: "Challenging software problem requiring creative solutions"
                    },
                    "expected_output": {
                        output_field: "Structured problem-solving approach with multiple solution options"
                    },
                },
                {
                    "name": f"{role.lower()}_best_practices",
                    "description": "When asked about software best practices, the agent should provide current industry standards and guidelines",
                    "input": {
                        input_field: "Industry best practices for software operations"
                    },
                    "expected_output": {
                        output_field: "Comprehensive best practices guide with implementation steps"
                    },
                },
            ]
        elif namespace == "healthcare":
            scenarios = [
                {
                    "name": f"{role.lower()}_patient_care",
                    "description": "Given patient information, the agent should provide appropriate healthcare guidance",
                    "input": {
                        input_field: "Patient symptoms and medical history requiring assessment"
                    },
                    "expected_output": {
                        output_field: "Professional healthcare recommendations with safety considerations"
                    },
                },
                {
                    "name": f"{role.lower()}_emergency_protocols",
                    "description": "When handling medical emergencies, the agent should follow proper protocols",
                    "input": {
                        input_field: "Emergency medical situation requiring immediate response"
                    },
                    "expected_output": {
                        output_field: "Step-by-step emergency protocol with safety guidelines"
                    },
                },
            ]
        elif namespace == "education":
            scenarios = [
                {
                    "name": f"{role.lower()}_learning_assessment",
                    "description": "Given student learning needs, the agent should provide personalized educational guidance",
                    "input": {
                        input_field: "Student learning challenge requiring educational strategy"
                    },
                    "expected_output": {
                        output_field: "Personalized learning plan with educational milestones"
                    },
                },
                {
                    "name": f"{role.lower()}_curriculum_design",
                    "description": "When designing educational content, the agent should follow pedagogical principles",
                    "input": {
                        input_field: "Educational objectives requiring curriculum development"
                    },
                    "expected_output": {
                        output_field: "Structured curriculum with learning objectives and assessments"
                    },
                },
            ]
        elif namespace == "finance":
            scenarios = [
                {
                    "name": f"{role.lower()}_financial_analysis",
                    "description": "Given financial data, the agent should provide accurate analysis and recommendations",
                    "input": {
                        input_field: "Financial situation requiring analysis and planning"
                    },
                    "expected_output": {
                        output_field: "Comprehensive financial analysis with actionable recommendations"
                    },
                },
                {
                    "name": f"{role.lower()}_risk_assessment",
                    "description": "When evaluating financial risks, the agent should provide thorough risk analysis",
                    "input": {
                        input_field: "Investment opportunity requiring risk evaluation"
                    },
                    "expected_output": {
                        output_field: "Detailed risk assessment with mitigation strategies"
                    },
                },
            ]
        else:
            # Generic scenarios for other namespaces
            scenarios = [
                {
                    "name": f"{role.lower()}_comprehensive_task",
                    "description": f"Given a complex {namespace} requirement, the agent should provide detailed analysis and recommendations",
                    "input": {
                        input_field: f"Complex {namespace} scenario requiring comprehensive analysis"
                    },
                    "expected_output": {
                        output_field: f"Detailed step-by-step analysis with {namespace}-specific recommendations"
                    },
                },
                {
                    "name": f"{role.lower()}_problem_solving",
                    "description": f"When facing {namespace} challenges, the agent should demonstrate systematic problem-solving approach",
                    "input": {
                        input_field: f"Challenging {namespace} problem requiring creative solutions"
                    },
                    "expected_output": {
                        output_field: "Structured problem-solving approach with multiple solution options"
                    },
                },
            ]

        return scenarios

    def _generate_genies_scenarios(
        self, namespace: str, role: str, input_field: str, output_field: str
    ) -> List[Dict]:
        """Generate additional scenarios for Genies-tier agents with advanced capabilities."""
        return [
            {
                "name": f"{role.lower()}_tool_integration",
                "description": "When using tools, the agent should demonstrate effective tool selection and usage",
                "input": {
                    input_field: f"Complex {namespace} task requiring multiple tool interactions"
                },
                "expected_output": {
                    output_field: "Tool-assisted solution with clear reasoning for tool selection"
                },
            },
            {
                "name": f"{role.lower()}_memory_utilization",
                "description": "When leveraging memory, the agent should reference relevant past interactions",
                "input": {
                    input_field: f"Follow-up {namespace} question building on previous conversation"
                },
                "expected_output": {
                    output_field: "Response that incorporates relevant context from memory"
                },
            },
        ]

    def _generate_generic_scenario(
        self, role: str, input_field: str, output_field: str, index: int
    ) -> Dict:
        """Generate a generic scenario when we need more scenarios."""
        return {
            "name": f"{role.lower()}_scenario_{index}",
            "description": f"The agent should handle general {role.lower()} requests effectively",
            "input": {
                input_field: f"General {role.lower()} task requiring professional response"
            },
            "expected_output": {
                output_field: f"Professional {role.lower()} response with clear guidance"
            },
        }

    def _generate_evaluation_config(self, tier: str) -> Dict:
        """Generate evaluation configuration based on tier."""
        base_metrics = [
            {
                "name": "answer_exact_match"
                if tier == "oracles"
                else "answer_correctness",
                "threshold": 1.0 if tier == "oracles" else 0.8,
            }
        ]

        return {"builtin_metrics": base_metrics}

    def _generate_optimization_config(self, tier: str) -> Dict:
        """Generate optimization configuration based on tier.

        Uses GEPA (Genetic-Pareto) for genies tier,
        few-shot bootstrapping for oracles tier.
        """
        if tier == "genies":
            # Genies use GEPA optimization
            return {
                "strategy": "gepa",  # Use GEPA for advanced agents
                "metric": "answer_correctness",
                "metric_threshold": 0.7,
                "gepa_config": {
                    "num_candidates": 10,
                    "breadth": 3,
                    "depth": 2,
                    "init_temperature": 1.4,
                },
            }
        else:
            # Oracles use basic few-shot bootstrapping
            return {
                "strategy": "few_shot_bootstrapping",
                "metric": "answer_exact_match",
                "metric_threshold": 0.9,
                "few_shot_bootstrapping_config": {
                    "max_bootstrapped_demos": 4,
                    "max_rounds": 1,
                },
            }

    def _generate_role_config(self, role: str, namespace: str) -> Dict:
        """Generate role-specific configuration including persona and agentflow."""
        agent_name = role.title()
        agent_id = role.lower().replace(" ", "_")

        # Generate persona based on role and namespace
        persona_config = {
            "name": f"{agent_name}",
            "role": role.title(),
            "goal": self._generate_goal(role, namespace),
            "traits": self._generate_traits(role, namespace),
        }

        # Generate agentflow based on role type
        agentflow_config = self._generate_agentflow(role, namespace)

        return {
            "agent_name": agent_name,
            "agent_id": agent_id,
            "persona": persona_config,
            "agentflow": agentflow_config,
        }

    def _generate_goal(self, role: str, namespace: str) -> str:
        """Generate goal statement based on role and namespace."""
        role_goals = {
            "developer": f"Write high-quality code and solve {namespace} development challenges",
            "analyst": f"Analyze data and provide insights for {namespace} decision-making",
            "assistant": f"Provide helpful support and guidance for {namespace} tasks",
            "manager": f"Coordinate and optimize {namespace} operations and workflows",
            "consultant": f"Provide expert advice and recommendations for {namespace} improvements",
        }

        return role_goals.get(
            role.lower(),
            f"Provide expert {role.lower()} services in {namespace} domain",
        )

    def _generate_traits(self, role: str, namespace: str) -> List[str]:
        """Generate personality traits based on role and namespace."""
        base_traits = ["helpful", "professional", "knowledgeable"]

        role_specific_traits = {
            "developer": ["analytical", "detail-oriented", "problem-solving"],
            "analyst": ["analytical", "data-driven", "thorough"],
            "assistant": ["supportive", "responsive", "adaptable"],
            "manager": ["organized", "strategic", "decisive"],
            "consultant": ["experienced", "strategic", "insightful"],
        }

        return base_traits + role_specific_traits.get(
            role.lower(), ["focused", "reliable"]
        )

    def _generate_agentflow(self, role: str, namespace: str) -> List[Dict]:
        """Generate agentflow configuration based on role."""
        # Basic agentflow for most roles
        return [
            {
                "name": "process_request",
                "type": "Generate",
                "task": self._get_main_task_name(role),
            }
        ]

    def _generate_tasks(self, role: str, namespace: str) -> List[Dict]:
        """Generate task configuration based on role and namespace."""
        main_task_name = self._get_main_task_name(role)

        # Generate role-specific inputs and outputs
        inputs, outputs = self._generate_task_io(role, namespace)

        task = {
            "name": main_task_name,
            "instruction": self._generate_instruction(role, namespace),
            "inputs": inputs,
            "outputs": outputs,
        }

        return [task]

    def _get_main_task_name(self, role: str) -> str:
        """Get the main task name for a role."""
        role_tasks = {
            "developer": "develop_solution",
            "analyst": "analyze_data",
            "assistant": "provide_assistance",
            "manager": "manage_workflow",
            "consultant": "provide_consultation",
        }

        return role_tasks.get(role.lower(), f"{role.lower()}_task")

    def _generate_instruction(self, role: str, namespace: str) -> str:
        """Generate task instruction based on role and namespace."""
        instructions = {
            "developer": f"You are a {namespace} developer. Analyze requirements and provide code solutions with best practices.",
            "analyst": f"You are a {namespace} analyst. Examine data and provide insights with recommendations.",
            "assistant": f"You are a {namespace} assistant. Help users with their questions and tasks professionally.",
            "manager": f"You are a {namespace} manager. Coordinate tasks and optimize workflows efficiently.",
            "consultant": f"You are a {namespace} consultant. Provide expert advice and strategic recommendations.",
        }

        return instructions.get(
            role.lower(),
            f"You are a {role.lower()} specializing in {namespace}. Provide professional assistance.",
        )

    def _generate_task_io(self, role: str, namespace: str) -> tuple:
        """Generate task inputs and outputs based on role and namespace."""

        # Common input patterns by role
        role_inputs = {
            "developer": [
                {
                    "name": "feature_requirement",
                    "type": "str",
                    "description": "Feature specification or coding task",
                    "required": True,
                }
            ],
            "analyst": [
                {
                    "name": "data_query",
                    "type": "str",
                    "description": "Data analysis request or question",
                    "required": True,
                }
            ],
            "assistant": [
                {
                    "name": "user_query",
                    "type": "str",
                    "description": "User question or request for assistance",
                    "required": True,
                }
            ],
            "manager": [
                {
                    "name": "workflow_request",
                    "type": "str",
                    "description": "Workflow or management task",
                    "required": True,
                }
            ],
            "consultant": [
                {
                    "name": "consultation_request",
                    "type": "str",
                    "description": "Business or strategic consultation request",
                    "required": True,
                }
            ],
        }

        # Common output patterns by role
        role_outputs = {
            "developer": [
                {
                    "name": "implementation",
                    "type": "str",
                    "description": "Code implementation or technical solution",
                }
            ],
            "analyst": [
                {
                    "name": "analysis_report",
                    "type": "str",
                    "description": "Data analysis results and insights",
                }
            ],
            "assistant": [
                {
                    "name": "assistance_response",
                    "type": "str",
                    "description": "Helpful response to user query",
                }
            ],
            "manager": [
                {
                    "name": "workflow_plan",
                    "type": "str",
                    "description": "Organized workflow or management plan",
                }
            ],
            "consultant": [
                {
                    "name": "consultation_advice",
                    "type": "str",
                    "description": "Expert advice and recommendations",
                }
            ],
        }

        # Default fallback
        default_inputs = [
            {
                "name": "query",
                "type": "str",
                "description": "User request or question",
                "required": True,
            }
        ]
        default_outputs = [
            {"name": "response", "type": "str", "description": "Professional response"}
        ]

        inputs = role_inputs.get(role.lower(), default_inputs)
        outputs = role_outputs.get(role.lower(), default_outputs)

        return inputs, outputs

    def generate_playbook(
        self, tier: str, role: str, namespace: str = "software"
    ) -> Dict:
        """Generate a complete agent playbook using SuperSpec DSL."""

        # Generate role-specific configuration
        role_config = self._generate_role_config(role, namespace)

        # Generate tasks
        tasks = self._generate_tasks(role, namespace)

        # Generate feature specifications with BDD scenarios
        feature_specs = self._generate_feature_specifications(
            namespace,
            role,
            tier,
            tasks[0].get("inputs", []),
            tasks[0].get("outputs", []),
        )

        # Generate evaluation and optimization configs
        evaluation_config = self._generate_evaluation_config(tier)
        optimization_config = self._generate_optimization_config(tier)

        # Build spec section
        spec = {
            # Model configuration (required for explicit DSPy template)
            "model": {
                "provider": "ollama",  # Default to ollama for local development
                "model": "llama3.2:1b",  # Fast, lightweight model (changed from model_name to model)
                "temperature": 0.7,  # Balanced creativity
                "max_tokens": 4000,  # Standard context
                "api_base": "http://localhost:11434",  # Ollama default
            },
            "persona": role_config["persona"],
            "tasks": tasks,
            "agentflow": role_config["agentflow"],
            "feature_specifications": feature_specs,
            "evaluation": evaluation_config,
            "optimization": optimization_config,
        }

        # Add tier-specific features
        if tier == "genies":
            # Add tool calling for Genies tier
            spec["tool_calling"] = {
                "enabled": True,
                "available_tools": ["web_search", "calculator", "file_operations"],
                "max_iterations": 5,
                "tool_selection_strategy": "auto",
            }

            # Add memory for Genies tier
            spec["memory"] = {
                "enabled": True,
                "short_term": {"max_tokens": 4000},
                "episodic": {"enabled": True, "max_episodes": 100},
            }

            # Add RAG if namespace supports it
            if namespace in ["software", "education", "healthcare", "legal"]:
                spec["rag"] = {
                    "vector_database": "chroma",
                    "collection_name": f"{role.lower()}_knowledge",
                    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                    "chunk_size": 512,
                    "overlap": 50,
                }

        # Complete playbook structure
        playbook = {
            "apiVersion": "superspec.dev/v1",
            "kind": "Agent",
            "metadata": {
                "name": role_config["agent_name"],
                "id": role_config["agent_id"],
                "namespace": namespace,
                "level": tier,
                "description": f"AI {role} specialized in {namespace} domain",
                "version": "1.0.0",
                "author": "SuperOptiX SuperSpec",
                "tags": [namespace, role.lower(), tier],
            },
            "spec": spec,
        }

        return playbook
