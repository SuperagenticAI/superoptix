"""
SuperSpec - Agent Playbook Definition Language

A comprehensive DSL for defining Oracles and Genies tier agent playbooks.
"""

from .parser import SuperSpecXParser
from .validator import SuperSpecXValidator
from .schema import SuperSpecXSchema
from .generator import SuperSpecXGenerator

__version__ = "1.0.0"
__all__ = [
    "SuperSpecXParser",
    "SuperSpecXValidator",
    "SuperSpecXSchema",
    "SuperSpecXGenerator",
]
