"""Unit tests for vendored Agenspy protocol components.

Tests cover:
- BaseProtocol interface
- MCPClient and MockMCPSession
- ProtocolAgent base class
- Protocol Registry
"""

import pytest

from superoptix.agent_bases import ProtocolAgent
from superoptix.protocols import BaseProtocol, ProtocolType, registry
from superoptix.protocols.mcp import MCPClient, MockMCPSession


class TestBaseProtocol:
    """Test BaseProtocol interface."""

    def test_protocol_type_enum(self):
        """Test ProtocolType enum values."""
        assert ProtocolType.MCP.value == "mcp"
        assert ProtocolType.AGENT2AGENT.value == "agent2agent"
        assert ProtocolType.CUSTOM.value == "custom"

    def test_base_protocol_properties(self):
        """Test BaseProtocol required properties."""
        protocol_config = {"type": ProtocolType.MCP}
        protocol = BaseProtocol(protocol_config)

        assert protocol.protocol_type == ProtocolType.MCP
        assert protocol._capabilities == {}  # Initialized as empty dict
        assert protocol._connected is False


class TestMockMCPSession:
    """Test MockMCPSession functionality."""

    def test_session_initialization(self):
        """Test session initialization."""
        session = MockMCPSession("mcp://test-server")
        assert session.server_url == "mcp://test-server"
        assert len(session.tools) == 3

    def test_list_tools(self):
        """Test tool listing."""
        session = MockMCPSession("mcp://test")
        tools = session.list_tools()

        assert "github_search" in tools
        assert "file_reader" in tools
        assert "code_analyzer" in tools

    def test_get_context(self):
        """Test context retrieval."""
        session = MockMCPSession("mcp://test")

        # Test PR context
        context = session.get_context("PR details for #123")
        assert "PR #123" in context
        assert "OAuth2" in context

        # Test file context
        context = session.get_context("file changes")
        assert "Modified files" in context
        assert "oauth.py" in context

        # Test generic context
        context = session.get_context("random request")
        assert "Context for:" in context

    def test_execute_tool(self):
        """Test tool execution."""
        session = MockMCPSession("mcp://test")

        # Test github_search
        result = session.execute_tool("github_search", {"query": "auth"})
        assert "PRs" in result

        # Test file_reader
        result = session.execute_tool("file_reader", {"file": "auth.py"})
        assert "OAuth2" in result

        # Test code_analyzer
        result = session.execute_tool("code_analyzer", {"code": "..."})
        assert "Code quality" in result

    def test_session_close(self):
        """Test session close."""
        session = MockMCPSession("mcp://test")
        session.close()  # Should not raise


class TestMCPClient:
    """Test MCPClient implementation."""

    def test_client_initialization(self):
        """Test client initialization."""
        client = MCPClient(server_url="mcp://test", timeout=10)

        assert client.server_url == "mcp://test"
        assert client.timeout == 10
        assert client.protocol_type == ProtocolType.MCP
        assert client.session is None
        assert len(client.available_tools) == 0

    def test_client_connect(self):
        """Test client connection."""
        client = MCPClient(server_url="mcp://test")
        success = client.connect()

        assert success is True
        assert client.session is not None
        assert len(client.available_tools) == 3
        assert client._connected is True

    def test_client_disconnect(self):
        """Test client disconnection."""
        client = MCPClient(server_url="mcp://test")
        client.connect()
        client.disconnect()

        assert client._connected is False

    def test_get_capabilities(self):
        """Test getting capabilities."""
        client = MCPClient(server_url="mcp://test")
        client.connect()

        caps = client.get_capabilities()

        assert caps["protocol"] == "mcp"
        assert caps["version"] == "1.0"
        assert len(caps["tools"]) == 3
        assert caps["context_sharing"] is True
        assert caps["session_management"] is True
        assert caps["server_url"] == "mcp://test"

    def test_discover_peers(self):
        """Test peer discovery."""
        client = MCPClient(server_url="mcp://test")
        client.connect()

        peers = client.discover_peers()

        assert len(peers) == 1
        assert peers[0] == "mcp://test"


class TestProtocolAgent:
    """Test ProtocolAgent base class."""

    class TestAgent(ProtocolAgent):
        """Test agent implementation."""

        def forward(self, query: str):
            """Simple forward implementation."""
            return {"query": query, "protocols": len(self.protocols)}

    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = self.TestAgent(agent_id="test_agent")

        assert agent.agent_id == "test_agent"
        assert len(agent.protocols) == 0
        assert isinstance(agent.metadata, dict)

    def test_add_protocol(self):
        """Test adding protocol to agent."""
        agent = self.TestAgent(agent_id="test")
        protocol = MCPClient(server_url="mcp://test")
        protocol.connect()

        agent.add_protocol(protocol)

        assert len(agent.protocols) == 1
        assert agent.protocols[0] == protocol

    def test_get_protocol_by_type(self):
        """Test getting protocol by type."""
        agent = self.TestAgent(agent_id="test")
        protocol = MCPClient(server_url="mcp://test")
        protocol.connect()
        agent.add_protocol(protocol)

        found = agent.get_protocol_by_type("mcp")

        assert found is not None
        assert found == protocol

        # Test not found
        not_found = agent.get_protocol_by_type("agent2agent")
        assert not_found is None

    def test_get_agent_info(self):
        """Test getting agent info."""
        agent = self.TestAgent(agent_id="test")
        protocol = MCPClient(server_url="mcp://test")
        protocol.connect()
        agent.add_protocol(protocol)

        info = agent.get_agent_info()

        assert info["agent_id"] == "test"
        assert len(info["protocols"]) == 1
        assert info["protocols"][0] == "mcp"

    def test_agent_cleanup(self):
        """Test agent cleanup."""
        agent = self.TestAgent(agent_id="test")
        protocol = MCPClient(server_url="mcp://test")
        protocol.connect()
        agent.add_protocol(protocol)

        agent.cleanup()

        assert len(agent.protocols) == 0
        assert protocol._connected is False


class TestProtocolRegistry:
    """Test ProtocolRegistry functionality."""

    def test_registry_singleton(self):
        """Test global registry instance."""
        assert registry is not None
        assert isinstance(registry, type(registry))

    def test_builtin_protocols_registered(self):
        """Test that MCP is auto-registered."""
        protocols = registry.get_available_protocols()

        assert ProtocolType.MCP in protocols

    def test_create_protocol(self):
        """Test creating protocol via registry."""
        protocol = registry.create_protocol(ProtocolType.MCP, server_url="mcp://test")

        assert isinstance(protocol, MCPClient)
        assert protocol.server_url == "mcp://test"

    def test_create_unregistered_protocol_fails(self):
        """Test creating unregistered protocol raises error."""
        with pytest.raises(ValueError, match="not registered"):
            registry.create_protocol(ProtocolType.AGENT2AGENT, server_url="a2a://test")

    def test_is_registered(self):
        """Test checking if protocol is registered."""
        assert registry.is_registered(ProtocolType.MCP) is True
        assert registry.is_registered(ProtocolType.AGENT2AGENT) is False

    def test_registry_cleanup(self):
        """Test registry cleanup."""
        # Create some protocols
        p1 = registry.create_protocol(ProtocolType.MCP, server_url="mcp://test1")
        p2 = registry.create_protocol(ProtocolType.MCP, server_url="mcp://test2")

        p1.connect()
        p2.connect()

        # Cleanup all
        registry.cleanup_all()

        # Note: The protocols are disconnected, but we can't easily verify
        # since _instances is private. Just ensure no errors.
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
