"""Protocol registry for SuperOptiX.

This module provides a central registry for managing protocol implementations.
Users can register custom protocols or use built-in protocols (MCP).

Vendored from Agenspy project and adapted for SuperOptiX architecture.
"""

import logging
from typing import Dict, List, Type

from superoptix.protocols.base import BaseProtocol, ProtocolType

logger = logging.getLogger(__name__)


class ProtocolRegistry:
    """Registry for managing protocol implementations.

    This class provides a central registry for protocol implementations,
    allowing agents to discover and use different protocols (MCP, etc.).

    Examples:
            >>> from superoptix.protocols.registry import registry
            >>> from superoptix.protocols.base import ProtocolType
            >>>
            >>> # Create an MCP protocol instance
            >>> protocol = registry.create_protocol(
            ...     ProtocolType.MCP,
            ...     server_uri="mcp://math-server"
            ... )
            >>>
            >>> # Get available protocols
            >>> protocols = registry.get_available_protocols()
            >>> print(protocols)  # [ProtocolType.MCP]
    """

    def __init__(self):
        """Initialize the protocol registry."""
        self._protocols: Dict[ProtocolType, Type[BaseProtocol]] = {}
        self._instances: Dict[str, BaseProtocol] = {}
        logger.debug("Protocol registry initialized")

    def register_protocol(
        self, protocol_type: ProtocolType, protocol_class: Type[BaseProtocol]
    ) -> None:
        """Register a protocol implementation.

        Args:
                protocol_type: The type of protocol to register
                protocol_class: The protocol class implementation

        Examples:
                >>> from superoptix.protocols.mcp.client import MCPClient
                >>> registry.register_protocol(ProtocolType.MCP, MCPClient)
        """
        self._protocols[protocol_type] = protocol_class
        logger.info(f"Registered protocol: {protocol_type.value}")

    def create_protocol(self, protocol_type: ProtocolType, **kwargs) -> BaseProtocol:
        """Create a protocol instance.

        Args:
                protocol_type: The type of protocol to create
                **kwargs: Arguments to pass to the protocol constructor

        Returns:
                A protocol instance

        Raises:
                ValueError: If the protocol type is not registered

        Examples:
                >>> protocol = registry.create_protocol(
                ...     ProtocolType.MCP,
                ...     server_uri="mcp://github"
                ... )
        """
        if protocol_type not in self._protocols:
            available = [p.value for p in self._protocols.keys()]
            raise ValueError(
                f"Protocol '{protocol_type.value}' not registered. "
                f"Available protocols: {available}"
            )

        protocol_class = self._protocols[protocol_type]
        logger.debug(f"Creating protocol instance: {protocol_type.value}")

        instance = protocol_class(**kwargs)

        # Track instance for cleanup
        instance_id = f"{protocol_type.value}_{id(instance)}"
        self._instances[instance_id] = instance

        return instance

    def get_available_protocols(self) -> List[ProtocolType]:
        """Get list of available protocol types.

        Returns:
                List of registered protocol types

        Examples:
                >>> protocols = registry.get_available_protocols()
                >>> print([p.value for p in protocols])
                ['mcp']
        """
        return list(self._protocols.keys())

    def is_registered(self, protocol_type: ProtocolType) -> bool:
        """Check if a protocol type is registered.

        Args:
                protocol_type: The protocol type to check

        Returns:
                True if the protocol is registered, False otherwise
        """
        return protocol_type in self._protocols

    def cleanup_all(self) -> None:
        """Cleanup all protocol instances.

        This method disconnects and cleans up all active protocol instances.
        Should be called when shutting down or resetting the registry.
        """
        logger.debug(f"Cleaning up {len(self._instances)} protocol instances")
        for instance_id, instance in self._instances.items():
            try:
                instance.disconnect()
                logger.debug(f"Disconnected protocol instance: {instance_id}")
            except Exception as e:
                logger.error(f"Error disconnecting {instance_id}: {e}")

        self._instances.clear()
        logger.info("All protocol instances cleaned up")


# Global registry instance
registry = ProtocolRegistry()


def register_builtin_protocols() -> None:
    """Register built-in protocol implementations.

    This function is called automatically on import to register
    all built-in protocols (currently only MCP).
    """
    try:
        from superoptix.protocols.mcp.client import MCPClient

        registry.register_protocol(ProtocolType.MCP, MCPClient)
        logger.debug("Built-in protocols registered successfully")
    except ImportError as e:
        logger.warning(f"Failed to register built-in protocols: {e}")


# Auto-register on import
register_builtin_protocols()
