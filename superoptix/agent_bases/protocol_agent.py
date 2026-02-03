"""Protocol-first agent base class for SuperOptiX.

This module provides the foundation for building protocol-first agents that
treat communication protocols (like MCP) as first-class primitives.

Vendored from Agenspy project and adapted for SuperOptiX architecture.
"""

import logging
from abc import abstractmethod
from typing import Any, Dict, List, Optional

import dspy

from superoptix.protocols.base import BaseProtocol

logger = logging.getLogger(__name__)


class ProtocolAgent(dspy.Module):
    """Base class for protocol-first agents in SuperOptiX.

    Protocol-first agents build on communication protocols rather than tools,
    enabling automatic tool discovery, session management, and protocol-level
    optimization. This is a key differentiator of SuperOptiX from pure DSPy.

    Unlike tool-first agents that manually configure tools, protocol-first
    agents connect to protocol servers (like MCP) and automatically discover
    available capabilities.

    Attributes:
        agent_id: Unique identifier for the agent
        protocols: List of active protocol connections
        metadata: Additional agent metadata

    Example:
        ```python
        from superoptix.agent_bases.protocol_agent import ProtocolAgent
        from superoptix.protocols.mcp.client import MCPClient
        import dspy

        class MyAgent(ProtocolAgent):
            def __init__(self, mcp_servers: List[str]):
                super().__init__(agent_id="my_agent")

                # Connect to MCP servers
                for server in mcp_servers:
                    client = MCPClient(server)
                    if client.connect():
                        self.add_protocol(client)

                # Create ReAct with protocol tools
                self.react = dspy.ReAct(
                    signature=MySignature,
                    tools=self._get_protocol_tools(),
                    max_iters=5
                )

            def _get_protocol_tools(self):
                tools = []
                for protocol in self.protocols:
                    if hasattr(protocol, 'available_tools'):
                        tools.extend(protocol.available_tools.values())
                return tools

            def forward(self, query: str):
                return self.react(query=query)
        ```
    """

    def __init__(self, agent_id: str, **kwargs):
        """Initialize protocol-first agent.

        Args:
            agent_id: Unique identifier for the agent
            **kwargs: Additional arguments passed to dspy.Module
        """
        super().__init__(**kwargs)
        self.agent_id = agent_id
        self.protocols: List[BaseProtocol] = []
        self.metadata: Dict[str, Any] = {}
        logger.info(f"Initialized protocol agent: {agent_id}")

    def add_protocol(self, protocol: BaseProtocol):
        """Add a protocol to the agent.

        The protocol should already be connected before adding.
        Multiple protocols can be added for multi-protocol agents.

        Args:
            protocol: Connected protocol instance to add
        """
        self.protocols.append(protocol)
        protocol_type = protocol.protocol_type.value
        logger.info(f"Added {protocol_type} protocol to agent {self.agent_id}")

    def get_protocol_by_type(self, protocol_type: str) -> Optional[BaseProtocol]:
        """Get protocol by type.

        Useful for multi-protocol agents that need to access specific
        protocol instances.

        Args:
            protocol_type: Protocol type string (e.g., "mcp", "agent2agent")

        Returns:
            Protocol instance if found, None otherwise
        """
        for protocol in self.protocols:
            if protocol.protocol_type.value == protocol_type:
                return protocol
        return None

    @abstractmethod
    def forward(self, **kwargs) -> dspy.Prediction:
        """Process agent request.

        Implementations should use protocol capabilities to handle requests.

        Args:
            **kwargs: Agent-specific request parameters

        Returns:
            dspy.Prediction with agent response
        """
        pass

    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information.

        Returns:
            Dictionary containing:
            - agent_id: Agent identifier
            - protocols: List of active protocol types
            - metadata: Agent metadata
        """
        return {
            "agent_id": self.agent_id,
            "protocols": [p.protocol_type.value for p in self.protocols],
            "metadata": self.metadata,
        }

    def cleanup(self):
        """Clean up agent resources.

        Disconnects all protocols and releases resources.
        Should be called when agent is no longer needed.
        """
        logger.info(f"Cleaning up agent: {self.agent_id}")
        for protocol in self.protocols:
            try:
                protocol.disconnect()
            except Exception as e:
                logger.warning(
                    f"Error disconnecting {protocol.protocol_type.value}: {e}"
                )
        self.protocols.clear()
