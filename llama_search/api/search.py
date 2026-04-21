import traceback

import tiktoken
from langchain_core.tools import tool

from llama_search.core.search_providers import (
    BingSearchProvider,
    BraveSearchProvider,
    ExaSearchProvider,
    FirecrawlSearchProvider,
    GoogleSearchProvider,
    PerplexitySearchProvider,
    SerpApiSearchProvider,
    SerperDevSearchProvider,
    TavilySearchProvider,
    ZenserpSearchProvider,
)
from llama_search.services.scraper_service import scrape_links
from llama_search.services.search_service import (
    extract_events,
    extract_events_all,
    extract_events_from_search,
    format_extracted_events,
)
from llama_search.utils.config import settings
from llama_search.utils.logger import log_print, logger


def get_token_length(text: str) -> int:
    try:
        return len(tiktoken.get_encoding("cl100k_base").encode(text))
    except Exception:
        return len(text) // 4


class _DummyCache:
    def set_auto(self, key, value):
        pass


cache_register = _DummyCache()


@tool
def get_events(
    search_qeury: str,
    country: str = "it",
    lang: str = "lang_it",
    engine: str = "google",
) -> str:
    """
    Performs a web search for the given query using one or many AI/SERP search engines and extracts events via RAG.

    Args:
        search_qeury: Query to find events.
        country: Two-letter country code.
        lang: Language format "lang_{code}".
        engine: "google", "bing", "firecrawl", "exa", "tavily", "perplexity", "serpapi", "serper", "brave", "zenserp", or "multi". (Can be comma separated).
    """

    try:
        filters = settings.get(
            "filters",
            [
                "facebook.com",
                "instagram.com",
                "twitter.com",
                "x.com",
                "linkedin.com",
                "tiktok.com",
                "reddit.com",
                "quora.com",
                "amazon.com",
                "ebay.com",
                "walmart.com",
                "aliexpress.com",
                "booking.com",
                "airbnb.com",
                "expedia.com",
                "netflix.com",
                "spotify.com",
                "youtube.com",
                "nytimes.com",
                "bloomberg.com",
                "forbes.com",
                "washingtonpost.com",
                "morningstar.com",
                "yahoo.com",
            ],
        )

        logger.info(f"Starting search for: {search_qeury}, engine: {engine}")
        key = {
            "search_qeury": search_qeury,
            "country": country,
            "lang": lang,
            "engine": engine,
        }
        num = 10

        providers = []
        engines = [e.strip().lower() for e in engine.split(",")]
        is_multi = "multi" in engines

        if is_multi or "google" in engines:
            providers.append(("google", GoogleSearchProvider()))
        if is_multi or "bing" in engines:
            providers.append(("bing", BingSearchProvider()))
        if is_multi or "firecrawl" in engines:
            providers.append(("firecrawl", FirecrawlSearchProvider()))
        if is_multi or "exa" in engines:
            providers.append(("exa", ExaSearchProvider()))
        if is_multi or "tavily" in engines:
            providers.append(("tavily", TavilySearchProvider()))
        if is_multi or "perplexity" in engines:
            providers.append(("perplexity", PerplexitySearchProvider()))
        if is_multi or "serpapi" in engines:
            providers.append(("serpapi", SerpApiSearchProvider()))
        if is_multi or "serper" in engines:
            providers.append(("serper", SerperDevSearchProvider()))
        if is_multi or "brave" in engines:
            providers.append(("brave", BraveSearchProvider()))
        if is_multi or "zenserp" in engines:
            providers.append(("zenserp", ZenserpSearchProvider()))

        all_urls = []
        google_results = []
        direct_contents = []

        for name, provider in providers:
            log_print("INFO", f"Starting {name} search")
            raw_res = provider.search(search_qeury, num_results=num, lang=lang)
            if name == "google":
                google_results = raw_res
            elif name == "perplexity" and raw_res:
                try:
                    ans = (
                        raw_res[0]
                        .get("choices", [])[0]
                        .get("message", {})
                        .get("content", "")
                    )
                    if ans:
                        direct_contents.append(f"Perplexity Sonar:\n{ans}")
                except Exception:
                    pass
            elif name == "firecrawl":
                for rr in raw_res:
                    if isinstance(rr, dict) and rr.get("content"):
                        direct_contents.append(
                            f"Firecrawl Context from ({rr.get('url')}):\n{rr['content'][:800]}"
                        )

            urls = provider.extract_urls(raw_res, filters)
            all_urls.extend(urls)
            log_print("INFO", f"Completed {name} search. Found {len(urls)} valid urls.")

        # Deduplicate
        all_urls = list(dict.fromkeys(all_urls))

        events_str_group = ""
        if google_results:
            try:
                events_extracted = extract_events(google_results)
                all_events_data = extract_events_from_search(google_results)
                all_events = format_extracted_events(all_events_data)
                events_all = extract_events_all(google_results)
                events_str_group = "\n".join([events_extracted, all_events, events_all])
            except Exception as e:
                logger.error(f"Error extracting events from google payload: {e}")

        contents_results = []
        if events_str_group.strip():
            contents_results.append(events_str_group)

        contents_results.extend(direct_contents)

        if all_urls:
            log_print("INFO", "Starting scraping and cleaning")
            scraped_data = scrape_links(all_urls, user_query=search_qeury, queue=[])
            for item in scraped_data:
                if item[1] not in [None, ""]:
                    contents_results.append(f"Source: {item[0]} \n{item[1]}")
            log_print("INFO", "Completed scraping and cleaning")

        if not contents_results:
            return "No search results or contents found."

        combined_results = [
            "=" * 50,
            "SEARCH RESULTS AND Scraped Data",
            "=" * 50,
            "\n".join(contents_results),
        ]

        str_combined_results = "\n".join(combined_results)
        token_count = get_token_length(str_combined_results)
        print(
            f"Tokens after preprocessing: {token_count} (Sources: {len(contents_results)})"
        )

        try:
            cache_register.set_auto(key, str_combined_results)
        except Exception:
            pass

        return str_combined_results

    except Exception as e:
        error_message = f"Critical error: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_message)
        return error_message
