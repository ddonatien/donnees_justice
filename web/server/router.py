from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import polars as pl
from analytics.metrics import compute_summary, compute_jurisdiction_distribution, compute_solution_distribution

# Setup templates
templates = Jinja2Templates(directory="web/templates")

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Main dashboard showing court decisions analytics
    """
    try:
        # Load data
        df = pl.read_parquet('data/clean/court_decisions.parquet', n_rows=1000)
        
        # Compute statistics
        summary = compute_summary(df)
        jurisdiction_dist = compute_jurisdiction_distribution(df)
        solution_dist = compute_solution_distribution(df)
        
        # Prepare data for template
        context = {
            "request": request,
            "title": "French Court Decisions Analytics",
            "summary": summary,
            "jurisdiction_dist": jurisdiction_dist.head(10).to_dicts(),
            "solution_dist": solution_dist.head(10).to_dicts(),
            "jurisdiction_plot": "/plots/jurisdiction_distribution.png",
            "solution_plot": "/plots/solution_distribution.png"
        }
        
        return templates.TemplateResponse("dashboard.html", context)
        
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>", status_code=500)

@router.get("/stats", response_class=HTMLResponse)
async def get_stats(request: Request):
    """
    Detailed statistics page
    """
    try:
        # Load data
        df = pl.read_parquet('data/clean/court_decisions.parquet', n_rows=1000)
        
        # Compute statistics
        summary = compute_summary(df)
        
        context = {
            "request": request,
            "title": "Detailed Statistics",
            "summary": summary
        }
        
        return templates.TemplateResponse("stats.html", context)
        
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>", status_code=500)

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "court-decisions-analytics"}
