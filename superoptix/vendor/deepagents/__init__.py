"""DeepAgents package."""

from superoptix.vendor.deepagents.graph import create_deep_agent
from superoptix.vendor.deepagents.middleware.filesystem import FilesystemMiddleware
from superoptix.vendor.deepagents.middleware.subagents import (
    CompiledSubAgent,
    SubAgent,
    SubAgentMiddleware,
)

__all__ = [
    "CompiledSubAgent",
    "FilesystemMiddleware",
    "SubAgent",
    "SubAgentMiddleware",
    "create_deep_agent",
]
