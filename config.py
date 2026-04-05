import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class ProviderConfig:
    url: str
    input_selector: str
    submit_selector: str
    response_selector: str
    done_selector: str
    system_prompt: str


PROVIDERS: dict[str, ProviderConfig] = {
    "chatgpt": ProviderConfig(
    url="https://chat.openai.com",
    input_selector="#prompt-textarea",
    submit_selector="#prompt-textarea",  # Changed to input for Enter key press
    response_selector="[data-message-author-role='assistant'] .markdown.prose",  # More specific selector
    done_selector="#prompt-textarea",  # Changed to input element
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

# ── App-level settings ────────────────────────────────────────────────────────
DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "chatgpt")
PORT: int = int(os.getenv("PORT", 5000))
HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"
LOGIN_TIMEOUT: int = int(os.getenv("LOGIN_TIMEOUT", 120_000))
RESPONSE_TIMEOUT: int = int(os.getenv("RESPONSE_TIMEOUT", 60_000))
USER_DATA_DIR: str = ".chrome_profiles/{provider}"
