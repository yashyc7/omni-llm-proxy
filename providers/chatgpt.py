import logging
from config import RESPONSE_TIMEOUT
from providers._base_playwright import PlaywrightProvider

logger = logging.getLogger(__name__)


class ChatGPTProvider(PlaywrightProvider):
    _provider_name = "chatgpt"

    