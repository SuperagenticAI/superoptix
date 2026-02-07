"""
StackOne Bridge Adapter
======================

Universal adapter to bridge StackOne tools to various agentic frameworks.
Supported: DSPy, Pydantic AI, CrewAI, Claude Agent SDK, Google ADK, Semantic Kernel, OpenAI, LangChain.
"""

import logging
from typing import Any, Dict, List, Optional, Type, cast

from pydantic import BaseModel, Field, create_model
from superoptix.core.base_component import BaseComponent

logger = logging.getLogger(__name__)

# Optional imports for framework support
try:
    import dspy
    from dspy.adapters.types.tool import Tool as DSPyTool
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False

try:
    from pydantic_ai import Tool as PydanticAITool, RunContext
    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    PYDANTIC_AI_AVAILABLE = False

try:
    from stackone_ai.models import StackOneTool, Tools as StackOneTools
    STACKONE_AVAILABLE = True
except ImportError:
    STACKONE_AVAILABLE = False

try:
    from crewai.tools.base_tool import BaseTool as CrewAIBaseTool, Tool as CrewAITool
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False


class StackOneOptimizableComponent(BaseComponent):
    """
    Component wrapper for StackOne tools to enable GEPA optimization.
    
    This component treats the tool description as the optimizable variable.
    GEPA will mutate the description to help the LLM better understand when 
    and how to use the tool.
    """

    def __init__(self, stackone_tool: Any):
        super().__init__(
            name=stackone_tool.name,
            description=stackone_tool.description,
            input_fields=list(stackone_tool.parameters.properties.keys()),
            output_fields=["result"],
            variable=stackone_tool.description,
            framework="stackone",
        )
        self.tool = stackone_tool

    def forward(self, **inputs: Any) -> Dict[str, Any]:
        """Execute the tool with the current (potentially optimized) description."""
        # Note: In a real optimization run, 'forward' might be used to test 
        # if the LLM picks the tool correctly based on its description.
        result = self.tool.execute(inputs)
        return {"result": result}


class StackOneBridge:
    """Bridge for converting StackOne tools to other frameworks."""

    def __init__(self, stackone_tools: Any):
        """
        Initialize the bridge with StackOne tools.

        Args:
            stackone_tools: Either a StackOne Tools object or a list of StackOneTool instances.
        """
        if not STACKONE_AVAILABLE:
            raise ImportError(
                "stackone-ai is not installed. Please install it with `pip install stackone-ai`."
            )

        if hasattr(stackone_tools, "to_list"):
            self.tools = stackone_tools.to_list()
        elif isinstance(stackone_tools, list):
            self.tools = stackone_tools
        else:
            raise ValueError("Invalid stackone_tools format. Expected Tools object or list.")

    def optimize(
        self, 
        dataset: List[Dict[str, Any]], 
        metric: Any,
        reflection_lm: str = "gpt-4o-mini",
        max_iterations: int = 5
    ) -> List[Any]:
        """
        Optimize StackOne tool descriptions using GEPA.

        Args:
            dataset: List of examples [{"inputs": {...}, "outputs": {...}}]
            metric: Metric function to evaluate performance
            reflection_lm: LM to use for generating description improvements
            max_iterations: Number of GEPA iterations

        Returns:
            List of optimized StackOneTool instances.
        """
        from superoptix.optimizers.universal_gepa import UniversalGEPA

        optimized_tools = []
        for tool in self.tools:
            logger.info(f"🧬 Optimizing description for tool: {tool.name}")
            
            # Wrap tool in optimizable component
            component = StackOneOptimizableComponent(tool)
            
            # Setup Universal GEPA
            optimizer = UniversalGEPA(
                metric=metric,
                reflection_lm=reflection_lm,
                max_iterations=max_iterations
            )
            
            # Run optimization
            result = optimizer.optimize(component, dataset)
            
            # Update tool description with optimized version
            tool.description = result.optimized_variable
            optimized_tools.append(tool)
            
            logger.info(f"✅ Optimized description for {tool.name}: {tool.description[:50]}...")

        return optimized_tools

    def to_dspy(self) -> List[Any]:
        """
        Convert StackOne tools to DSPy Tool objects.

        Returns:
            List of dspy.Tool objects.
        """
        if not DSPY_AVAILABLE:
            logger.warning("DSPy not installed. to_dspy() will fail if called.")
            raise ImportError("dspy is not installed.")

        dspy_tools = []
        for tool in self.tools:
            # DSPy Tool expects a function, name, and desc
            # We use the tool.execute method as the function
            d_tool = DSPyTool(
                func=tool.execute,
                name=tool.name,
                desc=tool.description
            )
            dspy_tools.append(d_tool)
        
        return dspy_tools

    def _create_pydantic_model_from_schema(self, tool_name: str, schema: Dict[str, Any]) -> Type[BaseModel]:
        """
        Dynamically create a Pydantic model from StackOne's JSON schema.
        """
        fields: Dict[str, Any] = {}
        
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict
        }

        for field_name, field_info in properties.items():
            field_type_str = field_info.get("type", "string")
            python_type = type_mapping.get(field_type_str, str)
            
            description = field_info.get("description", "")
            
            if field_name in required:
                fields[field_name] = (python_type, Field(description=description))
            else:
                fields[field_name] = (Optional[python_type], Field(default=None, description=description))
        
        # Create dynamic model
        model_name = f"{tool_name}Args"
        return create_model(model_name, **fields) # type: ignore

    def to_pydantic_ai(self) -> List[Any]:
        """
        Convert StackOne tools to Pydantic AI Tool objects.
        
        This generates fully typed Pydantic tools, enabling the agent to see
        the exact schema and validate arguments before execution.

        Returns:
            List of pydantic_ai.Tool objects.
        """
        if not PYDANTIC_AI_AVAILABLE:
            logger.warning("Pydantic AI not installed. to_pydantic_ai() will fail if called.")
            raise ImportError("pydantic-ai is not installed.")

        pai_tools = []
        for tool in self.tools:
            # 1. Create a dynamic Pydantic model for the arguments
            # We access the raw schema dict from the StackOne tool
            raw_schema = tool.parameters.model_dump()
            ArgsModel = self._create_pydantic_model_from_schema(tool.name, raw_schema)

            # 2. Create a wrapper function that accepts this typed model
            # Pydantic AI will introspect 'args: ArgsModel' to build the tool schema
            async def tool_wrapper(ctx: RunContext, args: ArgsModel) -> str:
                # Convert Pydantic model back to dict for StackOne
                return str(tool.execute(args.model_dump(exclude_none=True)))

            # 3. Create the Pydantic AI Tool
            p_tool = PydanticAITool(
                tool_wrapper,
                name=tool.name,
                description=tool.description,
            )
            pai_tools.append(p_tool)

        return pai_tools

    def to_openai(self) -> List[Dict[str, Any]]:
        """
        Delegate to native StackOne OpenAI conversion.
        """
        # StackOne has native support for this, we just provide the bridge pass-through
        return [t.to_openai_function() for t in self.tools]

    def to_langchain(self) -> List[Any]:
        """
        Delegate to native StackOne LangChain conversion.
        """
        # StackOne has native support for this
        return [t.to_langchain() for t in self.tools]

    def to_crewai(self) -> List[Any]:
        """
        Convert StackOne tools to CrewAI Tool objects.

        CrewAI tools use:
        - BaseTool class with _run() method for custom tools
        - Tool class that wraps a callable function
        - args_schema for Pydantic-based argument validation
        - Async support via _arun() method
        - Optional max_usage_count for limiting tool usage

        Returns:
            List of CrewAI Tool objects ready for use with CrewAI agents.

        Example:
            >>> bridge = StackOneBridge(stackone_tools)
            >>> crewai_tools = bridge.to_crewai()
            >>> agent = Agent(
            ...     role="HR Assistant",
            ...     goal="Help with HR queries",
            ...     tools=crewai_tools
            ... )
        """
        if not CREWAI_AVAILABLE:
            logger.warning("CrewAI not installed. to_crewai() will fail if called.")
            raise ImportError(
                "crewai is not installed. Please install it with `pip install crewai`."
            )

        crewai_tools = []
        for tool in self.tools:
            # 1. Create a dynamic Pydantic model for the arguments (args_schema)
            raw_schema = tool.parameters.model_dump()
            ArgsModel = self._create_pydantic_model_from_schema(tool.name, raw_schema)

            # 2. Create a wrapper function for the StackOne tool
            # We need to use a closure to properly capture the current tool
            def make_tool_func(current_tool):
                def tool_func(**kwargs) -> str:
                    """Execute the StackOne tool with validated arguments."""
                    try:
                        result = current_tool.execute(kwargs)
                        return str(result) if result is not None else "Tool executed successfully"
                    except Exception as e:
                        return f"Error executing tool {current_tool.name}: {str(e)}"

                # Set docstring for CrewAI to use
                tool_func.__doc__ = current_tool.description
                return tool_func

            # 3. Create CrewAI Tool instance
            # CrewAI's Tool class wraps a callable and handles schema generation
            crew_tool = CrewAITool(
                name=tool.name,
                description=tool.description,
                func=make_tool_func(tool),
                args_schema=ArgsModel,
            )
            crewai_tools.append(crew_tool)

            logger.debug(f"Converted StackOne tool '{tool.name}' to CrewAI Tool")

        logger.info(f"✅ Converted {len(crewai_tools)} StackOne tools to CrewAI format")
        return crewai_tools

    def to_crewai_async(self) -> List[Any]:
        """
        Convert StackOne tools to CrewAI Tool objects with async support.

        This version creates tools that support both sync (_run) and async (_arun)
        execution methods for use with async CrewAI workflows.

        Returns:
            List of CrewAI Tool objects with async support.
        """
        if not CREWAI_AVAILABLE:
            logger.warning("CrewAI not installed. to_crewai_async() will fail if called.")
            raise ImportError(
                "crewai is not installed. Please install it with `pip install crewai`."
            )

        import asyncio

        crewai_tools = []
        for tool in self.tools:
            # 1. Create args_schema from StackOne tool schema
            raw_schema = tool.parameters.model_dump()
            ArgsModel = self._create_pydantic_model_from_schema(tool.name, raw_schema)

            # 2. Create a custom BaseTool subclass with both sync and async methods
            # We need to create a class dynamically to support _arun
            def make_tool_class(current_tool, args_model):
                class StackOneCrewAITool(CrewAIBaseTool):
                    name: str = current_tool.name
                    description: str = current_tool.description
                    args_schema: type = args_model

                    def _run(self, **kwargs) -> str:
                        """Synchronous execution of the StackOne tool."""
                        try:
                            result = current_tool.execute(kwargs)
                            return str(result) if result is not None else "Tool executed successfully"
                        except Exception as e:
                            return f"Error executing tool {current_tool.name}: {str(e)}"

                    async def _arun(self, **kwargs) -> str:
                        """Asynchronous execution of the StackOne tool."""
                        # Run sync execution in thread pool for non-blocking async
                        loop = asyncio.get_event_loop()
                        return await loop.run_in_executor(None, lambda: self._run(**kwargs))

                return StackOneCrewAITool

            # 3. Instantiate the custom tool class
            ToolClass = make_tool_class(tool, ArgsModel)
            crew_tool = ToolClass()
            crewai_tools.append(crew_tool)

            logger.debug(f"Converted StackOne tool '{tool.name}' to async CrewAI Tool")

        logger.info(f"✅ Converted {len(crewai_tools)} StackOne tools to async CrewAI format")
        return crewai_tools

    def to_claude_sdk(self) -> tuple:
        """
        Convert StackOne tools to Claude Agent SDK in-process MCP server.

        Creates an MCP server that can be used directly with ClaudeAgentOptions.
        Uses Claude SDK's SdkMcpTool and create_sdk_mcp_server() for in-process
        tool execution (no subprocess overhead).

        Returns:
            Tuple of (McpSdkServerConfig, list of allowed_tool_names)

        Example:
            >>> bridge = StackOneBridge(stackone_tools)
            >>> mcp_server, tool_names = bridge.to_claude_sdk()
            >>> options = ClaudeAgentOptions(
            ...     mcp_servers={"stackone": mcp_server},
            ...     allowed_tools=tool_names
            ... )
            >>> async with ClaudeSDKClient(options=options) as client:
            ...     await client.query("Use HR tools to find employee")
        """
        try:
            from claude_agent_sdk import SdkMcpTool, create_sdk_mcp_server
        except ImportError:
            logger.warning("Claude Agent SDK not installed. to_claude_sdk() will fail.")
            raise ImportError(
                "claude-agent-sdk is not installed. "
                "Install with: pip install claude-agent-sdk "
                "or pip install -e '.[frameworks-claude-sdk]'"
            )

        sdk_tools = []
        tool_names = []

        for tool in self.tools:
            # 1. Create input schema from StackOne parameters
            # Claude SDK accepts simple type mapping: {"param": type}
            raw_schema = tool.parameters.model_dump()
            input_schema = self._convert_to_claude_sdk_schema(raw_schema)

            # 2. Create async handler with proper closure
            def make_handler(current_tool):
                async def handler(args: Dict[str, Any]) -> Dict[str, Any]:
                    """Execute StackOne tool and return Claude SDK response format."""
                    try:
                        result = current_tool.execute(args)
                        return {
                            "content": [{"type": "text", "text": str(result)}]
                        }
                    except Exception as e:
                        return {
                            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                            "is_error": True
                        }
                return handler

            # 3. Create SdkMcpTool
            sdk_tool = SdkMcpTool(
                name=tool.name,
                description=tool.description,
                input_schema=input_schema,
                handler=make_handler(tool)
            )
            sdk_tools.append(sdk_tool)

            # Tool naming follows Claude SDK convention: mcp__{server}__{tool}
            tool_names.append(f"mcp__stackone__{tool.name}")

            logger.debug(f"Converted StackOne tool '{tool.name}' to Claude SDK MCP tool")

        # 4. Bundle tools into MCP server
        mcp_server = create_sdk_mcp_server(
            name="stackone",
            version="1.0.0",
            tools=sdk_tools
        )

        logger.info(f"✅ Converted {len(sdk_tools)} StackOne tools to Claude SDK MCP format")
        return mcp_server, tool_names

    def _convert_to_claude_sdk_schema(self, stackone_schema: Dict[str, Any]) -> Dict[str, type]:
        """
        Convert StackOne JSON Schema to Claude SDK simple schema format.

        Claude SDK accepts simple type mapping: {"param_name": python_type}

        Args:
            stackone_schema: StackOne tool parameter schema

        Returns:
            Dict mapping parameter names to Python types
        """
        properties = stackone_schema.get("properties", {})

        type_map = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        simple_schema = {}
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get("type", "string")
            simple_schema[prop_name] = type_map.get(prop_type, str)

        return simple_schema

    def _to_google_function_declaration(self, tool: Any) -> Dict[str, Any]:
        """
        Convert a StackOne tool to Google Vertex AI FunctionDeclaration format.
        """
        # Google's format is similar to OpenAI but stricter on types
        # Ref: https://cloud.google.com/vertex-ai/docs/reference/rest/v1beta1/Tool
        
        schema = tool.parameters.model_dump()
        
        # Ensure strict compatibility with Google's Schema format
        # This is a simplified mapping; complex nested types might need recursion
        parameters = {
            "type": "OBJECT",
            "properties": {},
            "required": schema.get("required", [])
        }

        type_map = {
            "string": "STRING",
            "integer": "INTEGER",
            "number": "NUMBER",
            "boolean": "BOOLEAN",
            "array": "ARRAY",
            "object": "OBJECT"
        }

        for prop_name, prop_info in schema.get("properties", {}).items():
            prop_type = type_map.get(prop_info.get("type", "string"), "STRING")
            parameters["properties"][prop_name] = {
                "type": prop_type,
                "description": prop_info.get("description", "")
            }

        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": parameters
        }

    def to_google_adk(self) -> List[Dict[str, Any]]:
        """
        Convert StackOne tools to Google ADK / Vertex AI Tool objects.

        Returns:
            List of Tool dictionaries compatible with Google Generative AI SDK.
        """
        # In Google's SDK, a Tool is a collection of FunctionDeclarations
        # We return a list of FunctionDeclarations which can be passed to
        # genai.GenerativeModel(tools=[...])
        
        return [self._to_google_function_declaration(t) for t in self.tools]

    def to_semantic_kernel(self) -> List[Any]:
        """
        Convert StackOne tools to Microsoft Semantic Kernel Functions.

        Returns:
            List of KernelFunction objects.
        """
        try:
            from semantic_kernel.functions import kernel_function
            from semantic_kernel.functions.kernel_function_from_method import KernelFunctionFromMethod
        except ImportError:
            logger.warning("Semantic Kernel not installed. to_semantic_kernel() will fail.")
            raise ImportError("semantic-kernel is not installed.")

        sk_functions = []

        for tool in self.tools:
            # 1. Create a dynamic Pydantic model for arguments (reuse existing logic)
            raw_schema = tool.parameters.model_dump()
            ArgsModel = self._create_pydantic_model_from_schema(tool.name, raw_schema)

            # 2. Define the method to be wrapped
            # Semantic Kernel expects methods to have typed arguments for automatic schema generation
            # We use a closure to capture the specific tool instance
            def make_sk_method(current_tool, args_model):
                # The method name and docstring are critical for SK
                @kernel_function(
                    name=current_tool.name,
                    description=current_tool.description
                )
                def execute_tool(**kwargs) -> str:
                    # Validate against our dynamic model
                    try:
                        validated_args = args_model(**kwargs)
                        return str(current_tool.execute(validated_args.model_dump(exclude_none=True)))
                    except Exception as e:
                        return f"Error executing tool {current_tool.name}: {str(e)}"
                
                return execute_tool

            # 3. Create Kernel Function
            # We use KernelFunctionFromMethod to create the function object
            method = make_sk_method(tool, ArgsModel)
            
            # Note: In newer SK versions, the decorator handles creation, 
            # but we explicitly wrap it to ensure metadata is correct
            func = KernelFunctionFromMethod(
                method=method,
                plugin_name="StackOnePlugin"
            )
            sk_functions.append(func)

        return sk_functions

    def to_discovery_tools(self, framework: str = "dspy") -> List[Any]:
        """
        Create "Meta Tools" (search/execute) for dynamic tool discovery.

        Instead of loading all tools, this returns just 'tool_search' and 'tool_execute'.
        The agent can then search for the right tool at runtime and execute it.

        Args:
            framework: Target framework ('dspy', 'pydantic_ai', 'google', 'semantic_kernel', 'crewai', 'claude_sdk')

        Returns:
            List of converted meta-tools (or tuple for claude_sdk).
        """
        try:
            from stackone_ai.models import Tools
            from stackone_ai.utility_tools import ToolIndex, create_tool_search, create_tool_execute
        except ImportError:
            raise ImportError("stackone-ai >= 2.0 required for discovery tools.")

        # 1. Create the ToolIndex and Meta Tools using StackOne SDK
        # We need a Tools collection object for create_tool_execute
        tools_collection = Tools(self.tools)
        index = ToolIndex(self.tools)

        search_tool = create_tool_search(index)
        execute_tool = create_tool_execute(tools_collection)

        meta_tools = [search_tool, execute_tool]

        # 2. Convert these meta-tools to the requested framework using our existing logic
        # We create a temporary bridge just for these 2 tools
        temp_bridge = StackOneBridge(meta_tools)

        if framework == "dspy":
            return temp_bridge.to_dspy()
        elif framework == "pydantic_ai":
            return temp_bridge.to_pydantic_ai()
        elif framework == "google":
            return temp_bridge.to_google_adk()
        elif framework == "semantic_kernel":
            return temp_bridge.to_semantic_kernel()
        elif framework == "crewai":
            return temp_bridge.to_crewai()
        elif framework == "claude_sdk":
            return temp_bridge.to_claude_sdk()
        else:
            raise ValueError(f"Unknown framework: {framework}. Supported: dspy, pydantic_ai, google, semantic_kernel, crewai, claude_sdk")
