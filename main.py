from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from backend.database import Database
from backend.search_engine import SearchEngine
from backend.crawler import get_sample_data
from backend.indexer import PageRankCalculator


app = FastAPI(
    title="Search Engine",
    description="A Google-like search engine built with FastAPI",
    version="1.0.0"
)

# Initialize database and search engine
db = Database()
search_engine = SearchEngine(db)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")


# Pydantic models
class SearchQuery(BaseModel):
    q: str
    limit: Optional[int] = 10


class IndexRequest(BaseModel):
    urls: Optional[List[str]] = None


class SearchResult(BaseModel):
    url: str
    title: str
    snippet: str
    score: float


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page."""
    stats = search_engine.get_stats()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "stats": stats}
    )


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: str = ""):
    """Render the search results page."""
    results = []
    query = q.strip()

    if query:
        results = search_engine.search(query, limit=20)

    stats = search_engine.get_stats()

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "query": query,
            "results": results,
            "result_count": len(results),
            "stats": stats
        }
    )


@app.get("/api/search")
async def api_search(q: str, limit: int = 10):
    """
    Search API endpoint.

    Args:
        q: Search query
        limit: Maximum number of results

    Returns:
        List of search results
    """
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")

    results = search_engine.search(q.strip(), limit=limit)

    return {
        "query": q,
        "count": len(results),
        "results": results
    }


@app.get("/api/suggestions")
async def get_suggestions(q: str, limit: int = 5):
    """
    Get search suggestions.

    Args:
        q: Partial query
        limit: Maximum number of suggestions

    Returns:
        List of suggested queries
    """
    if not q:
        return {"suggestions": []}

    suggestions = search_engine.get_suggestions(q, limit=limit)

    return {"suggestions": suggestions}


@app.post("/api/index")
async def index_pages(request: IndexRequest):
    """
    Index web pages.

    Args:
        request: IndexRequest with optional URLs to crawl

    Returns:
        Indexing status
    """
    try:
        # For demo, use sample data
        # In production, you would crawl the provided URLs
        pages = get_sample_data()

        search_engine.index_pages(pages)

        # Calculate PageRank
        all_pages = db.get_all_pages()
        links = db.get_links()

        if all_pages:
            pr_calculator = PageRankCalculator()
            page_ranks = pr_calculator.calculate(all_pages, links)

            # Update PageRank scores in database
            for page_id, score in page_ranks.items():
                db.update_page_rank(page_id, score)

        stats = search_engine.get_stats()

        return {
            "status": "success",
            "pages_indexed": len(pages),
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """Get search engine statistics."""
    stats = search_engine.get_stats()
    pages = db.get_all_pages()

    return {
        "total_pages": stats['total_pages'],
        "total_links": stats['total_links'],
        "indexed_pages": len(pages)
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    # Index sample data on startup
    print("Initializing search engine...")
    pages = get_sample_data()
    search_engine.index_pages(pages)

    print("\nStarting server...")
    print("Open http://localhost:8000 in your browser")

    uvicorn.run(app, host="0.0.0.0", port=8000)
