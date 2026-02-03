"""Playbook registry for conversational CLI.

Scans and catalogs all available playbooks (library + user project).
"""

import warnings
from pathlib import Path
from typing import List, Dict, Optional
import yaml

# Suppress warnings
warnings.filterwarnings("ignore")


class PlaybookRegistry:
    """Registry of all available playbooks."""

    def __init__(self):
        self.registry = {}
        self._build_registry()

    def _build_registry(self):
        """Build registry from all playbooks."""
        # Scan library playbooks
        try:
            import superoptix

            lib_path = Path(superoptix.__file__).parent
            lib_playbooks_dir = lib_path / "agents"

            if lib_playbooks_dir.exists():
                for yaml_file in lib_playbooks_dir.glob("*.yaml"):
                    self._add_playbook(yaml_file, source="library")
        except Exception:
            pass

        # Scan user project playbooks
        user_playbooks_dir = Path.cwd() / "agents"
        if user_playbooks_dir.exists():
            for yaml_file in user_playbooks_dir.glob("*_playbook.yaml"):
                self._add_playbook(yaml_file, source="user_project")

    def _add_playbook(self, yaml_file: Path, source: str):
        """Add playbook to registry."""
        try:
            with open(yaml_file) as f:
                playbook = yaml.safe_load(f)

            if not playbook:
                return

            name = playbook.get("name", yaml_file.stem)

            self.registry[name] = {
                "path": str(yaml_file),
                "name": name,
                "description": playbook.get("description", "No description"),
                "features": self._extract_features(playbook),
                "tier": playbook.get("tier", "unknown"),
                "namespace": playbook.get("namespace", "software"),
                "source": source,
            }
        except Exception as e:
            # Skip invalid playbooks
            pass

    def _extract_features(self, playbook: dict) -> List[str]:
        """Extract features from playbook."""
        features = []

        spec = playbook.get("spec", {})

        if spec.get("memory", {}).get("enabled"):
            features.append("memory")

        if spec.get("tools", {}).get("enabled"):
            features.append("tools")

        if spec.get("rag", {}).get("enabled"):
            features.append("rag")

        if spec.get("protocols"):
            features.append("protocols")

        return features

    def list_all(self) -> List[Dict]:
        """List all playbooks."""
        return list(self.registry.values())

    def search(self, query: str) -> List[Dict]:
        """Search playbooks by query."""
        results = []
        query_lower = query.lower()

        for name, data in self.registry.items():
            score = 0

            # Match name
            if query_lower in name.lower():
                score += 10

            # Match description
            if query_lower in data["description"].lower():
                score += 5

            # Match features
            for feature in data["features"]:
                if query_lower in feature.lower():
                    score += 3

            # Match namespace
            if query_lower in data["namespace"].lower():
                score += 2

            if score > 0:
                results.append({**data, "score": score})

        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def get_by_name(self, name: str) -> Optional[Dict]:
        """Get playbook by name."""
        return self.registry.get(name)

    def list_by_source(self, source: str) -> List[Dict]:
        """List playbooks by source (library or user_project)."""
        return [
            data for name, data in self.registry.items() if data["source"] == source
        ]

    def list_by_tier(self, tier: str) -> List[Dict]:
        """List playbooks by tier."""
        return [data for name, data in self.registry.items() if data["tier"] == tier]

    def get_count(self) -> dict:
        """Get playbook counts."""
        library_count = len(
            [d for d in self.registry.values() if d["source"] == "library"]
        )
        user_count = len(
            [d for d in self.registry.values() if d["source"] == "user_project"]
        )

        return {
            "total": len(self.registry),
            "library": library_count,
            "user_project": user_count,
        }
