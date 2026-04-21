import asyncio
from typing import Optional
import httpx
import requests
from llama_searcher.utils.logger import logger, log_print
from llama_searcher.core.cleaners import get_html_content


async def fetch_content_static(
    url: str,
    retries: int = 3,
    timeout: float = 2.0,
    backoff_factor: float = 0.5,
    headers: Optional[dict] = None,
    queue: list = None,
) -> Optional[str]:
    """Fetch a URL's text content with retries and optional queue."""
    if queue is None:
        queue = []

    headers = headers or {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(timeout), headers=headers, cookies=httpx.Cookies()
        ) as client:
            try:
                resp = await asyncio.wait_for(client.get(url), timeout=timeout)
                resp.raise_for_status()
                return resp.text
            except asyncio.TimeoutError:
                log_print("WARNING", f"Request timed out after {timeout}s for {url}")
            except Exception as e:
                log_print("WARNING", f"Retry {e!r} for {url}")

            while queue:
                next_url = queue.pop(0)
                try:
                    resp = await asyncio.wait_for(client.get(next_url), timeout=timeout)
                    resp.raise_for_status()
                    log_print("INFO", f"Complete scraping website {next_url}")
                    return resp.text
                except (httpx.HTTPError, httpx.TransportError) as e:
                    log_print("ERROR", f"Failed to fetch {next_url} attempts: {e}")

        return None
    except Exception as e:
        log_print("ERROR", f"Error {e} in scraping website {url}")
        return None


async def async_fetch_dynamic(
    browser,
    url: str,
    semaphore: asyncio.Semaphore,
    remove_tags: tuple = ("script", "style"),
    remove_comments: bool = False,
    remove_lines: bool = False,
    remove_spaces: bool = True,
    timeout: int = 50,
    async_sleep: float = 2,
    max_retries: int = 2,
) -> tuple[str, Optional[str]]:
    page = None
    timeout_ms = int(timeout * 1000)

    async with semaphore:
        try:
            page = await browser.new_page()
            logger.info(f"Navigating to {url}...")
            try:
                await page.goto(url, wait_until="load", timeout=timeout_ms)
            except Exception as e:
                logger.warning(f"Failed to fully load {url}: {e}")

            try:
                await page.wait_for_selector("body", timeout=timeout_ms)
                logger.info(f"'body' tag found on {url}")
            except Exception as e:
                logger.warning(f"No 'body' tag found on {url}: {e}")

            await asyncio.sleep(async_sleep)

            html_content = ""
            for attempt in range(1, max_retries + 1):
                html_content = await page.content()
                if html_content.strip():
                    break
                logger.warning(
                    f"Empty HTML on attempt {attempt} for {url}, retrying..."
                )
                await asyncio.sleep(async_sleep)

            if not html_content.strip():
                logger.error(
                    f"Failed to retrieve content after {max_retries} retries for {url}"
                )
                return url, None

            scrapped = get_html_content(
                html_content, remove_tags, remove_comments, remove_lines, remove_spaces
            )

            logger.info(f"Successfully fetched and cleaned content for {url}.")
            return url, scrapped

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return url, None

        finally:
            if page:
                await page.close()


def _sync_scrape_link(
    url: str,
    remove_tags: tuple = ("script", "style"),
    remove_comments: bool = False,
    remove_lines: bool = True,
    remove_spaces: bool = True,
    timeout: int = 12,
):
    try:
        response = requests.get(
            url, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout
        )
        if response.status_code != 200:
            raise ValueError(
                f"Failed to fetch {url}, Status code: {response.status_code}"
            )

        html_content = response.text

        return get_html_content(
            html_content,
            remove_tags=remove_tags,
            remove_comments=remove_comments,
            remove_lines=remove_lines,
            remove_spaces=remove_spaces,
        )
    except Exception as e:
        log_print("ERROR", f"Failed to fetch {url}: {str(e)}")
        return None
