import abc
from typing import List, Dict, Any
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from llama_search.utils.logger import logger
from llama_search.utils.config import settings


class BaseSearchProvider(abc.ABC):
    @abc.abstractmethod
    def search(
        self, query: str, num_results: int = 10, lang: str = "lang_it"
    ) -> List[Dict[str, Any]]:
        pass

    @abc.abstractmethod
    def extract_urls(
        self, results: List[Dict[str, Any]], filters: List[str]
    ) -> List[str]:
        pass


class GoogleSearchProvider(BaseSearchProvider):
    def __init__(self):
        self.cse_key = settings.get("CSE_KEY", "")
        self.cse_id = settings.get("CSE_ID", "")

    def search(
        self, query: str, num_results: int = 10, lang: str = "lang_it"
    ) -> List[Dict[str, Any]]:
        if not self.cse_key or not self.cse_id:
            logger.error("Google CSE_KEY or CSE_ID missing in config.")
            return []

        try:
            service = build("customsearch", "v1", developerKey=self.cse_key)
            res = (
                service.cse()
                .list(q=query, cx=self.cse_id, num=num_results, lr=lang)
                .execute()
            )
            return res.get("items", [])
        except HttpError as e:
            logger.error(f"Google API error: {e}")
            return []

    def extract_urls(
        self, results: List[Dict[str, Any]], filters: List[str]
    ) -> List[str]:
        urls = []
        for result in results:
            if all(f_domain not in result.get("link", "") for f_domain in filters):
                urls.append(result["link"])
        return urls


class BingSearchProvider(BaseSearchProvider):
    def __init__(self):
        self.bing_key = settings.get("BING_API_KEY", "")
        self.endpoint = settings.get(
            "BING_SEARCH_ENDPOINT", "https://api.bing.microsoft.com/v7.0/search"
        )

    def search(
        self, query: str, num_results: int = 10, lang: str = "lang_it"
    ) -> List[Dict[str, Any]]:
        if not self.bing_key:
            logger.error("BING_API_KEY missing in config.")
            return []

        mkt = "it-IT"
        if lang == "lang_en":
            mkt = "en-US"
        elif lang == "lang_es":
            mkt = "es-ES"
        elif lang == "lang_fr":
            mkt = "fr-FR"
        elif lang == "lang_de":
            mkt = "de-DE"

        headers = {"Ocp-Apim-Subscription-Key": self.bing_key}
        params = {"q": query, "count": num_results, "mkt": mkt}

        try:
            resp = requests.get(self.endpoint, headers=headers, params=params)
            resp.raise_for_status()
            return resp.json().get("webPages", {}).get("value", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Bing API request error: {e}")
            return []

    def extract_urls(
        self, results: List[Dict[str, Any]], filters: List[str]
    ) -> List[str]:
        urls = []
        for result in results:
            if all(f_domain not in result.get("url", "") for f_domain in filters):
                urls.append(result["url"])
        return urls


class FirecrawlSearchProvider(BaseSearchProvider):
    def __init__(self):
        self.api_key = settings.get("FIRECRAWL_API_KEY", "")
        self.endpoint = settings.get(
            "FIRECRAWL_ENDPOINT", "https://api.firecrawl.dev/v1/search"
        )

    def search(
        self, query: str, num_results: int = 10, lang: str = "lang_it"
    ) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.error("FIRECRAWL_API_KEY missing in config.")
            return []

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"query": query, "pageOptions": {"fetchPageContent": True}}

        try:
            resp = requests.post(self.endpoint, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json().get("data", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Firecrawl API request error: {e}")
            return []

    def extract_urls(
        self, results: List[Dict[str, Any]], filters: List[str]
    ) -> List[str]:
        urls = []
        for result in results:
            url = result.get("url")
            if url and all(f_domain not in url for f_domain in filters):
                urls.append(url)
        return urls


class ExaSearchProvider(BaseSearchProvider):
    def __init__(self):
        self.api_key = settings.get("EXA_API_KEY", "")
        self.endpoint = settings.get("EXA_ENDPOINT", "https://api.exa.ai/search")

    def search(
        self, query: str, num_results: int = 10, lang: str = "lang_it"
    ) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.error("EXA_API_KEY missing in config.")
            return []

        headers = {
            "x-api-key": self.api_key,
            "accept": "application/json",
            "content-type": "application/json",
        }
        payload = {"query": query, "numResults": num_results}

        try:
            resp = requests.post(self.endpoint, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json().get("results", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Exa API request error: {e}")
            return []

    def extract_urls(
        self, results: List[Dict[str, Any]], filters: List[str]
    ) -> List[str]:
        urls = []
        for result in results:
            url = result.get("url")
            if url and all(f_domain not in url for f_domain in filters):
                urls.append(url)
        return urls


class TavilySearchProvider(BaseSearchProvider):
    def __init__(self):
        self.api_key = settings.get("TAVILY_API_KEY", "")
        self.endpoint = settings.get("TAVILY_ENDPOINT", "https://api.tavily.com/search")

    def search(
        self, query: str, num_results: int = 10, lang: str = "lang_it"
    ) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.error("TAVILY_API_KEY missing in config.")
            return []

        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": num_results,
        }

        try:
            resp = requests.post(self.endpoint, json=payload)
            resp.raise_for_status()
            return resp.json().get("results", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Tavily API request error: {e}")
            return []

    def extract_urls(
        self, results: List[Dict[str, Any]], filters: List[str]
    ) -> List[str]:
        urls = []
        for result in results:
            url = result.get("url")
            if url and all(f_domain not in url for f_domain in filters):
                urls.append(url)
        return urls


class PerplexitySearchProvider(BaseSearchProvider):
    def __init__(self):
        self.api_key = settings.get("PERPLEXITY_API_KEY", "")
        self.endpoint = settings.get(
            "PERPLEXITY_ENDPOINT", "https://api.perplexity.ai/chat/completions"
        )

    def search(
        self, query: str, num_results: int = 10, lang: str = "lang_it"
    ) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.error("PERPLEXITY_API_KEY missing in config.")
            return []

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "accept": "application/json",
            "content-type": "application/json",
        }
        payload = {"model": "sonar", "messages": [{"role": "user", "content": query}]}

        try:
            resp = requests.post(self.endpoint, headers=headers, json=payload)
            resp.raise_for_status()
            return [resp.json()]  # Return the single response object
        except requests.exceptions.RequestException as e:
            logger.error(f"Perplexity API request error: {e}")
            return []

    def extract_urls(
        self, results: List[Dict[str, Any]], filters: List[str]
    ) -> List[str]:
        urls = []
        for result in results:
            citations = result.get("citations", [])
            for url in citations:
                if url and all(f_domain not in url for f_domain in filters):
                    urls.append(url)
        return urls


class SerpApiSearchProvider(BaseSearchProvider):
    def __init__(self):
        self.api_key = settings.get("SERPAPI_API_KEY", "")
        self.endpoint = settings.get("SERPAPI_ENDPOINT", "https://serpapi.com/search")

    def search(
        self, query: str, num_results: int = 10, lang: str = "lang_it"
    ) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.error("SERPAPI_API_KEY missing in config.")
            return []

        gl = lang.split("_")[-1] if "lang_" in lang else "us"
        params = {"q": query, "api_key": self.api_key, "gl": gl, "num": num_results}

        try:
            resp = requests.get(self.endpoint, params=params)
            resp.raise_for_status()
            return resp.json().get("organic_results", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"SerpApi API request error: {e}")
            return []

    def extract_urls(
        self, results: List[Dict[str, Any]], filters: List[str]
    ) -> List[str]:
        urls = []
        for result in results:
            url = result.get("link")
            if url and all(f_domain not in url for f_domain in filters):
                urls.append(url)
        return urls


class SerperDevSearchProvider(BaseSearchProvider):
    def __init__(self):
        self.api_key = settings.get("SERPER_API_KEY", "")
        self.endpoint = settings.get(
            "SERPER_ENDPOINT", "https://google.serper.dev/search"
        )

    def search(
        self, query: str, num_results: int = 10, lang: str = "lang_it"
    ) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.error("SERPER_API_KEY missing in config.")
            return []

        headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
        gl = lang.split("_")[-1] if "lang_" in lang else "us"
        payload = {"q": query, "num": num_results, "gl": gl}

        try:
            resp = requests.post(self.endpoint, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json().get("organic", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"SerperDev API request error: {e}")
            return []

    def extract_urls(
        self, results: List[Dict[str, Any]], filters: List[str]
    ) -> List[str]:
        urls = []
        for result in results:
            url = result.get("link")
            if url and all(f_domain not in url for f_domain in filters):
                urls.append(url)
        return urls


class BraveSearchProvider(BaseSearchProvider):
    def __init__(self):
        self.api_key = settings.get("BRAVE_API_KEY", "")
        self.endpoint = settings.get(
            "BRAVE_ENDPOINT", "https://api.search.brave.com/res/v1/web/search"
        )

    def search(
        self, query: str, num_results: int = 10, lang: str = "lang_it"
    ) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.error("BRAVE_API_KEY missing in config.")
            return []

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
        }
        params = {"q": query, "count": num_results}

        try:
            resp = requests.get(self.endpoint, headers=headers, params=params)
            resp.raise_for_status()
            return resp.json().get("web", {}).get("results", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"BraveSearch API request error: {e}")
            return []

    def extract_urls(
        self, results: List[Dict[str, Any]], filters: List[str]
    ) -> List[str]:
        urls = []
        for result in results:
            url = result.get("url")
            if url and all(f_domain not in url for f_domain in filters):
                urls.append(url)
        return urls


class ZenserpSearchProvider(BaseSearchProvider):
    def __init__(self):
        self.api_key = settings.get("ZENSERP_API_KEY", "")
        self.endpoint = settings.get(
            "ZENSERP_ENDPOINT", "https://app.zenserp.com/api/v2/search"
        )

    def search(
        self, query: str, num_results: int = 10, lang: str = "lang_it"
    ) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.error("ZENSERP_API_KEY missing in config.")
            return []

        gl = lang.split("_")[-1] if "lang_" in lang else "us"
        params = {"apikey": self.api_key, "q": query, "num": num_results, "gl": gl}

        try:
            resp = requests.get(self.endpoint, params=params)
            resp.raise_for_status()
            return resp.json().get("organic", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Zenserp API request error: {e}")
            return []

    def extract_urls(
        self, results: List[Dict[str, Any]], filters: List[str]
    ) -> List[str]:
        urls = []
        for result in results:
            url = result.get("url")
            if url and all(f_domain not in url for f_domain in filters):
                urls.append(url)
        return urls
