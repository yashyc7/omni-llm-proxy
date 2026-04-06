import os
from dotenv import load_dotenv
from app.domain.schemas import ProviderConfig

load_dotenv()

PROVIDERS: dict[str, ProviderConfig] = {
    "chatgpt": ProviderConfig(
        url="https://chat.openai.com",
        input_selector="#prompt-textarea",
        submit_selector="#prompt-textarea",
        response_selector="[data-message-author-role='assistant'] .markdown.prose",
        done_selector="#prompt-textarea",
        system_prompt=(
            "You are a concise assistant. "
            "Reply with only the direct answer. "
            "No filler, no buffer text, no markdown unless necessary."
        ),
    ),
    "gemini": ProviderConfig(
        url="https://gemini.google.com",
        input_selector="rich-textarea",
        submit_selector="[aria-label='Send message']",
        response_selector=".response-content",
        done_selector="[aria-label='Send message']:not([disabled])",
        system_prompt=("Be concise. Answer directly. No preamble."),
    ),
    "claude": ProviderConfig(
        url="https://claude.ai",
        input_selector='[contenteditable="true"]',
        submit_selector="[aria-label='Send Message']",
        response_selector=".prose",
        done_selector="[aria-label='Send Message']:not([disabled])",
        system_prompt=("Be concise. Answer directly. No preamble."),
    ),
}

DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "chatgpt")
PORT: int = int(os.getenv("PORT", 5000))
HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"
LOGIN_TIMEOUT: int = int(os.getenv("LOGIN_TIMEOUT", 120_000))
RESPONSE_TIMEOUT: int = int(os.getenv("RESPONSE_TIMEOUT", 60_000))
USER_DATA_DIR: str = ".chrome_profiles/{provider}"
