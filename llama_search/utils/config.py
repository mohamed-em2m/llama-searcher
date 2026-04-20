from dynaconf import Dynaconf
import openai
from llama_search.utils.logger import log_print

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["settings.toml", ".secrets.toml"],
)

GOOGLE_API_KEY = settings.get("GOOGLE_API_KEY", "")
GEMINI_API_KEY = settings.get("Gemini_API_KEY", "")
GEMINI_API_KEY_2 = settings.get("Gemini_API_KEY_2", "")
CSE_KEY = settings.get("CSE_KEY", "")
CSE_ID = settings.get("CSE_ID", "")
BING_API_KEY = settings.get("BING_API_KEY", "")
FIRECRAWL_API_KEY = settings.get("FIRECRAWL_API_KEY", "")
EXA_API_KEY = settings.get("EXA_API_KEY", "")
TAVILY_API_KEY = settings.get("TAVILY_API_KEY", "")
PERPLEXITY_API_KEY = settings.get("PERPLEXITY_API_KEY", "")
SERPAPI_API_KEY = settings.get("SERPAPI_API_KEY", "")
SERPER_API_KEY = settings.get("SERPER_API_KEY", "")
BRAVE_API_KEY = settings.get("BRAVE_API_KEY", "")
ZENSERP_API_KEY = settings.get("ZENSERP_API_KEY", "")

OPENAI_SYNC_BASE_URL_GEMINI = settings.get(
    "OPENAI_SYNC_BASE_URL_GEMINI",
    "https://generativelanguage.googleapis.com/v1beta/models",
)
OPENAI_ASYNC_BASE_URL_GEMINI = settings.get(
    "OPENAI_ASYNC_BASE_URL_GEMINI",
    "https://generativelanguage.googleapis.com/v1beta/openai/",
)


def configure_apis():
    if GOOGLE_API_KEY:
        openai.api_key = GOOGLE_API_KEY
        openai.base_url = OPENAI_SYNC_BASE_URL_GEMINI
        log_print("INFO", "Configured OpenAI-compatible Gemini API.")
    else:
        log_print("ERROR", "GOOGLE_API_KEY not set. API calls will fail.")


configure_apis()
