import traceback
from urllib.parse import urlparse
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import polars as pl
from analytics.metrics import compute_summary, compute_jurisdiction_distribution, compute_solution_distribution
from analytics.plots import plot_jurisdiction_distribution, plot_solution_distribution, plot_decision_type_pie
import os
import json

# Setup templates
templates = Jinja2Templates(directory="web/templates")

router = APIRouter()

def generate_plots(df: pl.DataFrame = None, prefix: str = ""):
    """
    Generate fresh plots when server starts or reloads
    """
    try:
        print("📊 Generating fresh plots...")
        
        if df is None:
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
        plot_jurisdiction_distribution(jurisdiction_dist, f'analytics/{prefix}jurisdiction_distribution.png')
        plot_solution_distribution(solution_dist, f'analytics/{prefix}solution_distribution.png')
        
        # Generate decision type pie chart
        decision_types_df = df['Type_Decision'].value_counts().to_pandas()
        plot_decision_type_pie(decision_types_df, f'analytics/{prefix}decision_type_pie.png')
        
        print("✅ Plots generated successfully")
        
    except Exception as e:
        print(f"❌ Error generating plots: {e}")
        print(traceback.format_exc())

def apply_filters(df: pl.DataFrame, decision_type: str = None, solution: str = None, jurisdiction: str = None) -> pl.DataFrame:
    """
    Apply filters to the dataframe based on selected criteria
    """
    filtered_df = df
    
    if decision_type and decision_type != "all":
        filtered_df = filtered_df.filter(pl.col('Type_Decision') == decision_type)
    
    if solution and solution != "all":
        filtered_df = filtered_df.filter(pl.col('Solution') == solution)
    
    if jurisdiction and jurisdiction != "all":
        filtered_df = filtered_df.filter(pl.col('Nom_Juridiction') == jurisdiction)
    
    return filtered_df

def get_filter_options(df: pl.DataFrame) -> dict:
    """
    Get available options for all filters
    """
    return {
        'decision_types': ['all'] + df['Type_Decision'].unique().to_list(),
        'solutions': ['all'] + df['Solution'].unique().to_list(),
        'jurisdictions': ['all'] + df['Nom_Juridiction'].unique().to_list()
    }

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
            "jurisdiction_dist": jurisdiction_dist.head(10),
            "solution_dist": solution_dist.head(10),
            "jurisdiction_plot": "/plots/jurisdiction_distribution.png",
            "solution_plot": "/plots/solution_distribution.png",
            "type_pie": "/plots/decision_type_pie.png"
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

@router.get("/filter-options", response_class=HTMLResponse)
async def get_filter_options_endpoint(request: Request):
    """
    Get available filter options
    """
    try:
        # Load data
        sample_size = os.environ.get('DATA_SAMPLE_SIZE')
        
        if sample_size and int(sample_size) > 0:
            df = pl.read_parquet('data/clean/court_decisions.parquet', n_rows=int(sample_size))
        else:
            df = pl.read_parquet('data/clean/court_decisions.parquet')
        
        # Get filter options
        options = get_filter_options(df)
        
        # return JSONResponse(content=options)
        return templates.TemplateResponse(
            "options.html",
            {"request": request, "values": options},
        )
        
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/filter")
async def apply_filters_endpoint(
    request: Request,
):
    url_path = urlparse(request.headers['hx-current-url']).path
    print(f"Filtering request from {url_path}")
    form_data = await request.form()
    decision_type = form_data.get("decision_type", "all")
    solution = form_data.get("solution", "all")
    jurisdiction = form_data.get("jurisdiction", "all")
    """
    Apply filters and return filtered data
    """
    try:
        # Load data
        sample_size = os.environ.get('DATA_SAMPLE_SIZE')
        
        if sample_size and int(sample_size) > 0:
            df = pl.read_parquet('data/clean/court_decisions.parquet', n_rows=int(sample_size))
        else:
            df = pl.read_parquet('data/clean/court_decisions.parquet')
        
        # Apply filters
        filtered_df = apply_filters(df, decision_type, solution, jurisdiction)

        generate_plots(filtered_df, prefix="filtered_")
        
        # Compute statistics
        summary = compute_summary(filtered_df)
        if url_path == "/stats":
            context = {
                "request": request,
                "title": "Detailed Statistics",
                "summary": summary
            }
            
            return templates.TemplateResponse("stats_content.html", context)
        elif url_path == "/":
            jurisdiction_dist = compute_jurisdiction_distribution(filtered_df)
            solution_dist = compute_solution_distribution(filtered_df)
            
            # Prepare data for template
            context = {
                "request": request,
                "title": "French Court Decisions Analytics",
                "summary": summary,
                "jurisdiction_dist": jurisdiction_dist.head(10),
                "solution_dist": solution_dist.head(10),
                "jurisdiction_plot": f"/plots/filtered_jurisdiction_distribution.png",
                "solution_plot": f"/plots/filtered_solution_distribution.png",
                "type_pie": f"/plots/filtered_decision_type_pie.png"
            }
            
            return templates.TemplateResponse("dashboard_content.html", context)
        else:
            return JSONResponse(content={"error": "Unknown URL path"}, status_code=400)
        
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "court-decisions-analytics"}
