from app.domain.interfaces import ILlmProvider
from app.core.config import PROVIDERS, USER_DATA_DIR
from app.infrastructure.browser.manager import PlaywrightBrowserSession
from app.infrastructure.providers.chatgpt import ChatGPTProvider
from app.infrastructure.providers.claude import ClaudeProvider
from app.infrastructure.providers.gemini import GeminiProvider

def create_provider(name: str) -> ILlmProvider:
    name = name.lower()
    if name not in PROVIDERS:
        raise ValueError(f"Unknown provider '{name}'. Available: {list(PROVIDERS.keys())}")
        
    config = PROVIDERS[name]
    session_dir = USER_DATA_DIR.format(provider=name)
    session = PlaywrightBrowserSession(session_dir)

    if name == "chatgpt":
        return ChatGPTProvider(name, config, session)
    elif name == "claude":
        return ClaudeProvider(name, config, session)
    elif name == "gemini":
        return GeminiProvider(name, config, session)
    
    raise ValueError(f"Provider class for {name} is not implemented.")

def available_providers() -> list[str]:
    return list(PROVIDERS.keys())
