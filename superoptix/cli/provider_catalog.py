"""Provider catalog loader with SuperQode-compatible fallbacks.

Loads provider metadata from a local SuperQode checkout when available.
Falls back to a bundled minimal catalog when SuperQode sources are missing.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class ProviderEntry:
    provider_id: str
    name: str
    mode: str  # "byok" or "local"
    env_vars: List[str]
    example_models: List[str]
    default_base_url: str | None = None


def _fallback_catalog() -> Dict[str, Dict[str, ProviderEntry]]:
    byok = {
        "openai": ProviderEntry(
            provider_id="openai",
            name="OpenAI",
            mode="byok",
            env_vars=["OPENAI_API_KEY"],
            example_models=["gpt-4o", "gpt-4o-mini", "o1-mini"],
            default_base_url="https://api.openai.com/v1/chat/completions",
        ),
        "anthropic": ProviderEntry(
            provider_id="anthropic",
            name="Anthropic",
            mode="byok",
            env_vars=["ANTHROPIC_API_KEY"],
            example_models=["claude-sonnet-4", "claude-3-5-sonnet"],
            default_base_url="https://api.anthropic.com/v1/messages",
        ),
        "google": ProviderEntry(
            provider_id="google",
            name="Google Gemini",
            mode="byok",
            env_vars=["GEMINI_API_KEY", "GOOGLE_API_KEY"],
            example_models=["gemini-2.5-pro", "gemini-2.5-flash"],
            default_base_url=None,
        ),
        "groq": ProviderEntry(
            provider_id="groq",
            name="Groq",
            mode="byok",
            env_vars=["GROQ_API_KEY"],
            example_models=["llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
            default_base_url="https://api.groq.com/openai/v1/chat/completions",
        ),
        "deepseek": ProviderEntry(
            provider_id="deepseek",
            name="DeepSeek",
            mode="byok",
            env_vars=["DEEPSEEK_API_KEY"],
            example_models=["deepseek-chat", "deepseek-reasoner"],
            default_base_url="https://api.deepseek.com/chat/completions",
        ),
        "openrouter": ProviderEntry(
            provider_id="openrouter",
            name="OpenRouter",
            mode="byok",
            env_vars=["OPENROUTER_API_KEY"],
            example_models=["openai/gpt-4o", "anthropic/claude-sonnet-4"],
            default_base_url="https://openrouter.ai/api/v1/chat/completions",
        ),
    }
    local = {
        "ollama": ProviderEntry(
            provider_id="ollama",
            name="Ollama",
            mode="local",
            env_vars=[],
            example_models=["llama3.2:3b", "qwen2.5-coder:7b"],
            default_base_url="http://localhost:11434/api/chat",
        ),
        "lmstudio": ProviderEntry(
            provider_id="lmstudio",
            name="LM Studio",
            mode="local",
            env_vars=[],
            example_models=["local-model"],
            default_base_url="http://localhost:1234/v1/chat/completions",
        ),
        "vllm": ProviderEntry(
            provider_id="vllm",
            name="vLLM",
            mode="local",
            env_vars=[],
            example_models=["Qwen/Qwen2.5-Coder-7B-Instruct"],
            default_base_url="http://localhost:8000/v1/chat/completions",
        ),
        "sglang": ProviderEntry(
            provider_id="sglang",
            name="SGLang",
            mode="local",
            env_vars=[],
            example_models=["Qwen/Qwen2.5-Coder-7B-Instruct"],
            default_base_url="http://localhost:30000/v1/chat/completions",
        ),
        "mlx": ProviderEntry(
            provider_id="mlx",
            name="MLX",
            mode="local",
            env_vars=[],
            example_models=["mlx-community/Qwen2.5-Coder-3B-4bit"],
            default_base_url="http://localhost:8080/v1/chat/completions",
        ),
    }
    return {"byok": byok, "local": local}


def _candidate_superqode_registry_paths() -> List[Path]:
    here = Path(__file__).resolve()
    repo_root = here.parents[2]  # superoptix/
    return [
        Path("/Users/shashi/oss/superqode/src/superqode/providers/registry.py"),
        repo_root.parent / "superqode" / "src" / "superqode" / "providers" / "registry.py",
    ]


def _load_from_superqode_registry(path: Path) -> Dict[str, Dict[str, ProviderEntry]] | None:
    if not path.exists():
        return None
    spec = spec_from_file_location("superqode_provider_registry", str(path))
    if not spec or not spec.loader:
        return None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[assignment]
    providers = getattr(module, "PROVIDERS", None)
    if not providers or not isinstance(providers, dict):
        return None

    byok: Dict[str, ProviderEntry] = {}
    local: Dict[str, ProviderEntry] = {}
    for pid, definition in providers.items():
        category = getattr(definition, "category", None)
        category_name = str(getattr(category, "name", "")).upper()
        mode = "local" if "LOCAL" in category_name else "byok"
        entry = ProviderEntry(
            provider_id=str(getattr(definition, "id", pid)),
            name=str(getattr(definition, "name", pid)),
            mode=mode,
            env_vars=list(getattr(definition, "env_vars", []) or []),
            example_models=list(getattr(definition, "example_models", []) or []),
            default_base_url=getattr(definition, "default_base_url", None),
        )
        if mode == "local":
            local[entry.provider_id] = entry
        else:
            byok[entry.provider_id] = entry

    if not byok and not local:
        return None
    return {"byok": byok, "local": local}


def load_provider_catalog() -> Dict[str, Dict[str, ProviderEntry]]:
    for path in _candidate_superqode_registry_paths():
        loaded = _load_from_superqode_registry(path)
        if loaded:
            return loaded
    return _fallback_catalog()

