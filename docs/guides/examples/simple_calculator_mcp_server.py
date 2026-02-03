#!/usr/bin/env python3
"""
Simple Calculator MCP Server Example

This is a minimal MCP server that provides calculator tools.
Use this as a reference for creating your own MCP servers.

Run with: python3 simple_calculator_mcp_server.py

Then configure in playbook:
  mcp:
    enabled: true
    servers:
      - name: calculator
        type: stdio
        config:
          command: "python3"
          args: ["simple_calculator_mcp_server.py"]
        tool_prefix: "calc_"
"""
from mcp.server.fastmcp import FastMCP

# Create MCP server instance
mcp = FastMCP("Calculator")

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        Sum of a and b
    """
    return a + b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        Product of a and b
    """
    return a * b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract b from a.
    
    Args:
        a: Number to subtract from
        b: Number to subtract
    
    Returns:
        Difference (a - b)
    """
    return a - b

@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b.
    
    Args:
        a: Dividend
        b: Divisor (must not be zero)
    
    Returns:
        Quotient (a / b)
    
    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

if __name__ == "__main__":
    # Run the server (stdio transport)
    mcp.run()
