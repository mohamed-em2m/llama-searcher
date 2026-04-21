from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

from llama_searcher.api.search import get_events
from llama_searcher.utils.logger import logger

app = FastAPI(
    title="llama-searcher API",
    description="Professional Search Orchestration API for AI Agents and RAG pipelines.",
    version="0.1.0",
)


class SearchRequest(BaseModel):
    query: str
    country: Optional[str] = "it"
    lang: Optional[str] = "lang_it"
    engine: Optional[str] = "google"


class SearchResponse(BaseModel):
    query: str
    engine: str
    results: str
    token_count: Optional[int] = None


@app.get("/search", response_model=SearchResponse)
async def search_get(
    q: str = Query(..., description="The search query"),
    country: str = "it",
    lang: str = "lang_it",
    engine: str = "google",
):
    """
    Search endpoint via GET request.
    """
    logger.info(f"API Search request: q={q}, engine={engine}")
    try:
        results = get_events(search_qeury=q, country=country, lang=lang, engine=engine)
        return SearchResponse(query=q, engine=engine, results=results)
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=SearchResponse)
async def search_post(request: SearchRequest):
    """
    Search endpoint via POST request.
    """
    logger.info(f"API Search request: {request}")
    try:
        results = get_events(
            search_qeury=request.query,
            country=request.country,
            lang=request.lang,
            engine=request.engine,
        )
        return SearchResponse(
            query=request.query, engine=request.engine, results=results
        )
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
