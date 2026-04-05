from providers.base import BaseProvider
from providers.chatgpt import ChatGPTProvider
from providers.claude import ClaudeProvider
from providers.gemini import GeminiProvider

_REGISTRY: dict[str, type[BaseProvider]] = {
    "chatgpt": ChatGPTProvider,
    "gemini":  GeminiProvider,
    "claude":  ClaudeProvider,
}


def get_provider(name: str) -> BaseProvider:
    cls = _REGISTRY.get(name.lower())
    if not cls:
        raise ValueError(
            f"Unknown provider '{name}'. "
            f"Available: {list(_REGISTRY.keys())}"
        )
    return cls()


def available_providers() -> list[str]:
    return list(_REGISTRY.keys())
