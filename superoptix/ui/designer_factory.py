from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path


class AgentLevel(Enum):
    INTERN = "intern"
    ORACLES = "oracles"
    GENIES = "genies"
    SAGE = "sage"
    SUPERAGENTS = "superagents"
    SOVEREIGNS = "sovereigns"


class BaseDesigner(ABC):
    @abstractmethod
    def get_ui_path(self) -> Path:
        pass

    @property
    def base_path(self) -> Path:
        return Path(__file__).parent


class DesignerFactory:
    @classmethod
    def get_designer(cls, level: str) -> Path:
        """Get the UI path for the specified level."""
        base_path = Path(__file__).parent
        level_map = {
            "intern": base_path / "intern_designer.py",
            "oracles": base_path / "oracles_designer.py",
            "genies": base_path / "genies_designer.py",
            "sage": base_path / "senior_designer.py",
            "superagents": base_path / "architect_designer.py",
            "sovereigns": base_path / "lead_designer.py",
        }

        if level not in level_map:
            raise ValueError(f"Unsupported level: {level}")

        designer_path = level_map[level]

        # Check if the designer file exists
        if not designer_path.exists():
            if level == "genies":
                raise ValueError(
                    "Genies designer not yet implemented. Please use 'oracles' tier for now: super agent design --tier oracles"
                )
            else:
                raise ValueError(f"Designer file not found: {designer_path}")

        return designer_path
