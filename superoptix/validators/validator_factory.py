"""Validator factory for different tier validators"""

from .oracles_playbook_validator import OraclesPlaybookValidator


def get_validator(tier: str):
    """Get the appropriate validator for a tier"""

    validators = {
        "oracles": OraclesPlaybookValidator,
        "genies": OraclesPlaybookValidator,  # Genies uses same basic validation as Oracles
    }

    if tier not in validators:
        raise ValueError(
            f"No validator found for tier '{tier}'. Supported tiers: {list(validators.keys())}"
        )

    return validators[tier]()
