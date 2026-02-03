import os
from datetime import datetime
from typing import Any, Dict, Optional

import dspy

from ..memory import AgentMemory


class DSPyAdapter:
    """DSPy 3.0 compatible implementation adapter with enhanced memory integration."""

    def __init__(self, config: Dict[str, Any], agent_id: Optional[str] = None):
        self.config = config
        self.dspy = dspy
        self.agent_id = (
            agent_id or f"agent_{config.get('persona', {}).get('name', 'default')}"
        )
        self.usage_stats = {}

        # Initialize memory system
        self.memory = AgentMemory(
            agent_id=self.agent_id,
            enable_embeddings=config.get("memory", {}).get("enable_embeddings", True),
        )

        # Set default values if not provided
        if "provider" not in self.config["llm"]:
            self.config["llm"]["provider"] = "ollama"
        if "model" not in self.config["llm"]:
            self.config["llm"]["model"] = "llama3.2:1b"
        if "api_base" not in self.config["llm"]:
            self.config["llm"]["api_base"] = "http://localhost:11434"
        self._setup_lm()

    def _setup_lm(self):
        """Set up DSPy 3.0 language model with proper configuration."""
        provider = self.config["llm"]["provider"].lower()

        if provider == "ollama":
            lm = self.dspy.LM(
                f"ollama_chat/{self.config['llm']['model']}",
                api_base=self.config["llm"]["api_base"],
                api_key="",
            )
        elif provider == "openai":
            if "OPENAI_API_KEY" not in os.environ:
                raise ValueError("OpenAI API key not found in environment variables")
            lm = self.dspy.LM(
                model=self.config["llm"]["model"],
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=self.config["llm"].get("temperature", 0.7),
            )
        elif provider == "anthropic":
            if "ANTHROPIC_API_KEY" not in os.environ:
                raise ValueError("Anthropic API key not found in environment variables")
            lm = self.dspy.LM(
                model=self.config["llm"]["model"],
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                temperature=self.config["llm"].get("temperature", 0.7),
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        # Store LM for DSPy 3.0 context usage
        self.lm = lm

    def setup_agent(self) -> Any:
        """Set up DSPy 3.0 agent with signature and module."""

        # Define signature for input/output with DSPy 3.0 syntax
        class AgentSignature(self.dspy.Signature):
            """Signature defining input/output interface with memory context."""

            context: str = self.dspy.InputField(desc="Relevant context and memory")
            query: str = self.dspy.InputField(desc="The user's input query")
            result: str = self.dspy.OutputField(desc="The agent's response")

        # Create agent module with memory integration and DSPy 3.0 patterns
        class MemoryEnhancedAgentModule(self.dspy.Module):
            def __init__(self, config, dspy_instance, memory_system, lm):
                super().__init__()
                self.config = config
                self.dspy = dspy_instance
                self.memory = memory_system
                self.lm = lm
                # Use ChainOfThought for better reasoning
                self.predictor = self.dspy.ChainOfThought(AgentSignature)

            def forward(self, query: str, user_context: Optional[Dict] = None) -> dict:
                # Start interaction tracking
                episode_id = self.memory.start_interaction(user_context or {})

                try:
                    # Get relevant context from memory
                    conversation_context = self.memory.get_conversation_context()
                    relevant_memories = self.memory.recall(query, limit=3)

                    # Build context string
                    context_parts = []

                    # Add persona information
                    persona = self.config.get("persona", {})
                    context_parts.append(f"You are {persona.get('name', 'Assistant')}.")
                    context_parts.append(
                        f"Description: {persona.get('description', '')}"
                    )
                    if persona.get("traits"):
                        context_parts.append(f"Traits: {', '.join(persona['traits'])}")

                    # Add relevant memories
                    if relevant_memories:
                        context_parts.append("\nRelevant past knowledge:")
                        for memory in relevant_memories:
                            context_parts.append(f"- {memory['content'][:100]}...")

                    # Add recent conversation
                    recent_conversation = conversation_context.get(
                        "recent_conversation", []
                    )
                    if recent_conversation:
                        context_parts.append("\nRecent conversation:")
                        for msg in recent_conversation[-3:]:  # Last 3 messages
                            context_parts.append(
                                f"- {msg.get('role', 'unknown')}: {msg.get('content', '')[:50]}..."
                            )

                    context_string = "\n".join(context_parts)

                    # Log the interaction
                    self.memory.add_interaction_event(
                        event_type="user_query",
                        description="User submitted query",
                        data={"query": query, "context_length": len(context_string)},
                    )

                    # Generate response using DSPy 3.0 context management
                    with self.dspy.context(lm=self.lm):
                        response = self.predictor(context=context_string, query=query)

                    result = response.result

                    # Store the interaction in memory
                    self.memory.remember(
                        content=f"Q: {query}\nA: {result}",
                        memory_type="short",
                        importance=0.7,
                        ttl=3600,  # 1 hour
                    )

                    # Add conversation to short-term memory
                    self.memory.short_term.add_to_conversation("user", query)
                    self.memory.short_term.add_to_conversation("assistant", result)

                    # Log the response
                    self.memory.add_interaction_event(
                        event_type="agent_response",
                        description="Agent provided response",
                        data={
                            "response_length": len(result),
                            "query_length": len(query),
                        },
                    )

                    # End interaction successfully
                    self.memory.end_interaction(
                        {
                            "success": True,
                            "response_generated": True,
                            "query_type": "general",
                        }
                    )

                    return {"result": result, "episode_id": episode_id}

                except Exception as e:
                    # End interaction with error
                    self.memory.end_interaction(
                        {"success": False, "error": str(e), "query": query}
                    )
                    raise e

        # Pass memory system and LM to AgentModule
        return MemoryEnhancedAgentModule(self.config, self.dspy, self.memory, self.lm)

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the DSPy pipeline with DSPy 3.0 usage tracking and memory integration."""
        try:
            agent = self.setup_agent()
            query = inputs.get("query", "")
            user_context = inputs.get("context", {})
            current_usage = {}

            # Use DSPy 3.0 usage tracking with fallback
            try:
                with self.dspy.track_usage() as tracker:
                    result = agent(query, user_context)

                    # Capture usage statistics
                    current_usage = tracker.get_total_tokens() or {}
            except Exception as usage_error:
                # Fallback to basic execution without usage tracking
                print(
                    f"Warning: Usage tracking failed in adapter ({usage_error}), falling back to basic execution"
                )
                result = agent(query, user_context)
                current_usage = {}

            # Update cumulative usage stats with null safety
            for model, stats in current_usage.items():
                if model not in self.usage_stats:
                    self.usage_stats[model] = {}
                if isinstance(stats, dict):
                    for key, value in stats.items():
                        # Handle None values from models that don't report usage
                        if value is not None:
                            current_value = self.usage_stats[model].get(key, 0)
                            if current_value is not None:
                                self.usage_stats[model][key] = current_value + value
                            else:
                                self.usage_stats[model][key] = value
                        else:
                            # If model doesn't report this metric, initialize to 0
                            if key not in self.usage_stats[model]:
                                self.usage_stats[model][key] = 0

            # Add memory statistics to response
            memory_summary = self.memory.get_memory_summary()

            return {
                "result": result["result"],
                "episode_id": result.get("episode_id"),
                "memory_stats": {
                    "interactions": memory_summary["interaction_count"],
                    "short_term_items": memory_summary["short_term_memory"]["size"],
                    "long_term_items": memory_summary["long_term_memory"][
                        "total_items"
                    ],
                    "active_episodes": memory_summary["episodic_memory"][
                        "active_episodes"
                    ],
                },
                "usage_stats": {
                    "current_call": current_usage,
                    "cumulative": self.usage_stats,
                },
                "execution_timestamp": datetime.now().isoformat(),
                "adapter_version": "dspy_3.0_compatible",
            }

        except Exception as e:
            raise RuntimeError(f"DSPy 3.0 pipeline execution failed: {str(e)}") from e

    def learn_from_feedback(self, feedback: Dict[str, Any]) -> bool:
        """Learn from user feedback and update memory."""
        try:
            # Extract insights from feedback
            insights = []

            if feedback.get("helpful", False):
                insights.append("User found the response helpful")

            if feedback.get("accuracy") == "high":
                insights.append("Response was accurate")

            if feedback.get("clarity") == "high":
                insights.append("Response was clear and well-explained")

            # Store feedback patterns
            patterns = {
                "feedback_type": feedback.get("type", "general"),
                "satisfaction_level": feedback.get("satisfaction", "unknown"),
                "improvement_areas": feedback.get("improvements", []),
            }

            return self.memory.learn_from_interaction(insights, patterns)

        except Exception as e:
            print(f"Error learning from feedback: {e}")
            return False

    def get_memory_insights(self) -> Dict[str, Any]:
        """Get insights from the agent's memory."""
        try:
            # Get memory summary
            summary = self.memory.get_memory_summary()

            # Get recent patterns
            global_context = self.memory.context.get_context("global")
            learned_patterns = (
                global_context.get("learned_patterns", {}) if global_context else {}
            )

            # Get recent episodes
            recent_episodes = self.memory.episodic.get_recent_episodes(days=7, limit=10)

            return {
                "memory_summary": summary,
                "learned_patterns": learned_patterns,
                "recent_episodes": [
                    {
                        "title": ep.title,
                        "status": ep.status,
                        "importance": ep.importance_score,
                        "events_count": len(ep.events),
                    }
                    for ep in recent_episodes
                ],
                "top_memories": self.memory.recall("", memory_type="long", limit=5),
            }

        except Exception as e:
            print(f"Error getting memory insights: {e}")
            return {}

    def get_usage_summary(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics for DSPy 3.0."""
        return {
            "cumulative_usage": self.usage_stats,
            "agent_id": self.agent_id,
            "memory_enabled": True,
            "adapter_info": {
                "type": "dspy_adapter",
                "dspy_version": "3.0.0b1",
                "features": [
                    "usage_tracking",
                    "memory_integration",
                    "context_management",
                ],
            },
        }

    def clear_session_memory(self):
        """Clear session-based memory while preserving long-term memories."""
        try:
            self.memory.short_term.clear()
            self.memory.context.clear_context("session")
            print("Session memory cleared successfully")
        except Exception as e:
            print(f"Error clearing session memory: {e}")

    def save_memory_state(self) -> bool:
        """Save current memory state to persistent storage."""
        try:
            return self.memory.save_state()
        except Exception as e:
            print(f"Error saving memory state: {e}")
            return False

    def cleanup_memory(self) -> Dict[str, int]:
        """Clean up old memories and return cleanup statistics."""
        try:
            return self.memory.cleanup_old_memories()
        except Exception as e:
            print(f"Error during memory cleanup: {e}")
            return {"error": 1}
