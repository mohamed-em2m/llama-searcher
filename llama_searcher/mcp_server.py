from mcp.server.fastmcp import FastMCP
from llama_searcher.api.search import get_events
from llama_searcher.utils.logger import logger

# Create an MCP server
mcp = FastMCP("llama-searcher")


@mcp.tool()
def search_web(
    query: str, engine: str = "multi", country: str = "it", lang: str = "lang_it"
) -> str:
    """
    Search the web using 10+ AI and SERP search engines (Google, Bing, Exa, Tavily, etc.).
    Returns clean, LLM-ready markdown content optimized for RAG.

    Args:
        query: The search query to find information or events.
        engine: Comma-separated list of engines (e.g., 'google,exa') or 'multi' for all.
        country: Two-letter country code (e.g., 'it', 'us').
        lang: Language filter (e.g., 'lang_it', 'lang_en').
    """
    logger.info(f"MCP Search Tool invoked: query='{query}', engine='{engine}'")
    try:
        # get_events is sync by design because it handles its own internal async loops for some providers
        # but we call it here. FastMCP handles sync tools fine.
        result = get_events(
            search_qeury=query, country=country, lang=lang, engine=engine
        )
        return result
    except Exception as e:
        logger.error(f"MCP Error: {str(e)}")
        return f"Error performing search: {str(e)}"


if __name__ == "__main__":
    mcp.run()
