import asyncio
import aiohttp
from typing import Sequence, Optional, Union
from playwright.async_api import async_playwright

from llama_search.core.fetchers import (
    fetch_content_static,
    async_fetch_dynamic,
    _sync_scrape_link,
)
from llama_search.core.cleaners import get_html_content
from llama_search.agents.analysis_agent import summarize_agent
from llama_search.utils.logger import log_print


async def _scrape_task_static(
    url: str,
    session: aiohttp.ClientSession,
    remove_tags: Sequence[str] = ("script", "style"),
    remove_comments: Optional[bool] = False,
    remove_lines: Optional[bool] = True,
    remove_spaces: Optional[bool] = True,
    ssl_flag: Optional[bool] = True,
    retries: Optional[int] = 2,
    user_query: str = "",
    index: int = 0,
    queue: list = None,
    max_queue: list = None,
):
    if queue is None:
        queue = []
    if max_queue is None:
        max_queue = [0]

    html_content = await fetch_content_static(url, retries=retries, queue=queue)
    if html_content is None:
        return url, None

    scrapped = get_html_content(
        html_content, remove_tags, remove_comments, remove_lines, remove_spaces
    )

    if scrapped and any(
        keyword in scrapped
        for keyword in ["<?php", "{%", "data.qryEvento", "<%=", "{{get_"]
    ):
        log_print(
            "ERROR", "Dynamic placeholders or server-side code detected in content."
        )
        return url, None

    return url, await summarize_agent.summarize(scrapped, user_query, index, max_queue)


async def async_scrape_transform_links_static(
    urls: Sequence[str],
    remove_tags=("script", "style", "header", "footer"),
    remove_comments=False,
    remove_lines=True,
    remove_spaces=True,
    ssl_flag=True,
    timeout=7,
    retries=1,
    user_query: str = "",
    queue: list = None,
):
    if queue is None:
        queue = []
    max_queue = [0]
    timeout_obj = aiohttp.ClientTimeout(total=timeout)

    async with aiohttp.ClientSession(timeout=timeout_obj) as session:

        async def wrapper(url, index):
            try:
                return await asyncio.wait_for(
                    _scrape_task_static(
                        url,
                        session,
                        remove_tags,
                        remove_comments,
                        remove_lines,
                        remove_spaces,
                        ssl_flag,
                        retries=retries,
                        user_query=user_query,
                        index=index,
                        queue=queue,
                        max_queue=max_queue,
                    ),
                    timeout=timeout,
                )
            except Exception:
                return ("", "")

        scraping_tasks = [
            asyncio.create_task(wrapper(url, index)) for index, url in enumerate(urls)
        ]
        return await asyncio.gather(*scraping_tasks)


async def async_scrape_transform_links_dynamic(
    urls: Sequence[str],
    remove_tags=("script", "style", "header", "footer"),
    remove_comments=False,
    remove_lines=True,
    remove_spaces=True,
    timeout=50,
    max_num_urls=3,
):
    async with async_playwright() as p:
        semaphore = asyncio.Semaphore(max_num_urls)
        browser = await p.chromium.launch(headless=True)
        tasks = [
            asyncio.create_task(
                async_fetch_dynamic(
                    browser,
                    url,
                    semaphore,
                    remove_tags,
                    remove_comments,
                    remove_lines,
                    remove_spaces,
                    timeout=timeout,
                )
            )
            for url in urls
        ]
        contents = await asyncio.gather(*tasks)
        await browser.close()

    return contents


def scrape_links(
    urls: Union[str, Sequence[str]],
    remove_tags=(
        "script",
        "style",
        "header",
        "footer",
        "nav",
        "noscript",
        "iframe",
        "form",
        "input",
        "button",
        "aside",
        "svg",
        "canvas",
        "object",
        "embed",
        "picture",
        "figure",
        "figcaption",
        "video",
        "audio",
        "meta",
        "navbar",
        "menu",
        "sidebar",
        "ads",
        "ad",
        "cookie",
        "popup",
        "modal",
        "banner",
        "subscribe",
        "newsletter",
        "tracking",
        "sponsor",
        "share",
        "comment",
        "breadcrumb",
        "template",
        "datalist",
        "dialog",
        "source",
    ),
    remove_comments=False,
    remove_lines=True,
    remove_spaces=True,
    ssl_flag=True,
    retries=1,
    timeout=6,
    is_async=True,
    static_scrape=True,
    user_query: str = "",
    queue: list = None,
):
    if queue is None:
        queue = []

    if isinstance(urls, str):
        urls = [urls]

    if is_async:
        if static_scrape:
            return asyncio.run(
                async_scrape_transform_links_static(
                    urls,
                    remove_tags,
                    remove_comments,
                    remove_lines,
                    remove_spaces,
                    ssl_flag,
                    timeout=timeout,
                    retries=retries,
                    user_query=user_query,
                    queue=queue,
                )
            )
        else:
            return asyncio.run(
                async_scrape_transform_links_dynamic(
                    urls,
                    remove_tags,
                    remove_comments,
                    remove_lines,
                    remove_spaces,
                    timeout=timeout,
                )
            )

    contents = []
    for url in urls:
        contents.append(
            (
                url,
                _sync_scrape_link(
                    url,
                    remove_tags,
                    remove_comments,
                    remove_lines,
                    remove_spaces,
                    timeout=timeout,
                ),
            )
        )
    return contents
