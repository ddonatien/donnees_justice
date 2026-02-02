import traceback
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import polars as pl
from analytics.metrics import compute_summary, compute_jurisdiction_distribution, compute_solution_distribution
from analytics.plots import plot_jurisdiction_distribution, plot_solution_distribution
import os

# Setup templates
templates = Jinja2Templates(directory="web/templates")

router = APIRouter()

def generate_plots():
    """
    Generate fresh plots when server starts or reloads
    """
    try:
        print("📊 Generating fresh plots...")
        
        # Load data with configurable sample size
        # DATA_SAMPLE_SIZE=0 uses all data, any positive number uses that many rows
        sample_size = os.environ.get('DATA_SAMPLE_SIZE')
        
        if sample_size and int(sample_size) > 0:
            df = pl.read_parquet('data/clean/court_decisions.parquet', n_rows=int(sample_size))
            print(f"📊 Using sample of {sample_size} rows")
        else:
            df = pl.read_parquet('data/clean/court_decisions.parquet')
            print(f"📊 Using full dataset")
        
        # Compute distributions
        jurisdiction_dist = compute_jurisdiction_distribution(df)
        solution_dist = compute_solution_distribution(df)
        
        # Generate plots
        plot_jurisdiction_distribution(jurisdiction_dist, 'analytics/jurisdiction_distribution.png')
        plot_solution_distribution(solution_dist, 'analytics/solution_distribution.png')
        
        print("✅ Plots generated successfully")
        
    except Exception as e:
        print(f"❌ Error generating plots: {e}")
        print(traceback.format_exc())

# Generate plots when module is loaded (on server start/reload)
if not os.environ.get('TESTING'):
    generate_plots()

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Main dashboard showing court decisions analytics
    """
    try:
        # Load data with configurable sample size
        sample_size = os.environ.get('DATA_SAMPLE_SIZE')
        
        if sample_size and int(sample_size) > 0:
            df = pl.read_parquet('data/clean/court_decisions.parquet', n_rows=int(sample_size))
        else:
            df = pl.read_parquet('data/clean/court_decisions.parquet')
        
        # Compute statistics
        summary = compute_summary(df)
        jurisdiction_dist = compute_jurisdiction_distribution(df)
        solution_dist = compute_solution_distribution(df)
        
        # Prepare data for template
        context = {
            "request": request,
            "title": "French Court Decisions Analytics",
            "summary": summary,
            "jurisdiction_dist": jurisdiction_dist,
            "solution_dist": solution_dist,
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
        # Load data with configurable sample size
        sample_size = os.environ.get('DATA_SAMPLE_SIZE')
        
        if sample_size and int(sample_size) > 0:
            df = pl.read_parquet('data/clean/court_decisions.parquet', n_rows=int(sample_size))
        else:
            df = pl.read_parquet('data/clean/court_decisions.parquet')
        
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
