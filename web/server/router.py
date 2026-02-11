import traceback
from urllib.parse import urlparse
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import polars as pl
from analytics.metrics import (compute_summary, compute_jurisdiction_distribution,
                               compute_solution_distribution, compute_recours_type_distribution,
                               aggregate_entry_by_month, aggregate_entry_by_jurisdiction)
from analytics.plots import ( plot_jurisdiction_distribution, plot_solution_distribution,
                             plot_recours_type_distribution, stacked_plot_by_month, scatter_hist_by_jurisdiction)
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
        recours_types_dist = compute_recours_type_distribution(df)
        recours_by_month = aggregate_entry_by_month(df, entry_name="Type_Recours", prop=True)
        solution_by_month = aggregate_entry_by_month(df, entry_name="Solution", prop=True)
        jurisdiction_by_month = aggregate_entry_by_month(df, entry_name="Nom_Juridiction", prop=True)
        recours_by_juri = aggregate_entry_by_jurisdiction(df, entry_name="Type_Recours", prop=True)
        solution_by_juri = aggregate_entry_by_jurisdiction(df, entry_name="Solution", prop=True)
        
        # Generate plots
        plot_jurisdiction_distribution(jurisdiction_dist, f'analytics/{prefix}jurisdiction_distribution.svg')
        plot_solution_distribution(solution_dist, f'analytics/{prefix}solution_distribution.svg')
        plot_recours_type_distribution(recours_types_dist, f'analytics/{prefix}recours_type_distribution.svg')
        stacked_plot_by_month(recours_by_month, f'analytics/{prefix}recours_by_month.svg')  
        stacked_plot_by_month(solution_by_month, f'analytics/{prefix}solution_by_month.svg')
        stacked_plot_by_month(jurisdiction_by_month, f'analytics/{prefix}jurisdiction_by_month.svg')
        scatter_hist_by_jurisdiction(recours_by_juri, query="excès de pouvoir", output_path=f'analytics/{prefix}recours_by_jurisdiction.svg')
        scatter_hist_by_jurisdiction(solution_by_juri, query="rejet", output_path=f'analytics/{prefix}solution_by_jurisdiction.svg')
        
        print("✅ Plots generated successfully")
        
    except Exception as e:
        print(f"❌ Error generating plots: {e}")
        print(traceback.format_exc())

def apply_filters(df: pl.DataFrame, decision_type: str = None, recours_type: str = None,
                  solution: str = None, jurisdiction: str = None, source: str = None,
                  start_date: str = None, end_date: str = None) -> pl.DataFrame:
    """
    Apply filters to the dataframe based on selected criteria
    """
    filtered_df = df
    
    if decision_type and decision_type != "all":
        filtered_df = filtered_df.filter(pl.col('Type_Decision').str.to_lowercase() == decision_type.lower())
    
    if recours_type and recours_type != "all":
        print(f"Filtering by recours type: {recours_type}")
        filtered_df = filtered_df.filter(pl.col('Type_Recours').str.to_lowercase() == recours_type.lower())
    
    if solution and solution != "all":
        print(f"Filtering by solution: {solution}")
        filtered_df = filtered_df.filter(pl.col('Solution').str.to_lowercase() == solution.lower())
    
    if jurisdiction and jurisdiction != "all":
        print(f"Filtering by jurisdiction: {jurisdiction}")
        filtered_df = filtered_df.filter(pl.col('Nom_Juridiction').str.to_lowercase() == jurisdiction.lower())
    
    if start_date:
        filtered_df = filtered_df.filter(pl.col('Date_Lecture') >= start_date)

    if end_date:
        filtered_df = filtered_df.filter(pl.col('Date_Lecture') <= end_date)
    
    if source and source != "all":
        print(f"Filtering by source: {source}")
        filtered_df = filtered_df.filter(pl.col('Source').str.to_lowercase() == source.lower())
    
    return filtered_df

def get_filter_options(df: pl.DataFrame) -> dict:
    """
    Get available options for all filters
    """
    return {
        'decision_types': ['all'] + sorted(df['Type_Decision'].str.to_lowercase().unique().to_list()),
        'recours_types': ['all'] + sorted(df['Type_Recours'].str.to_lowercase().unique().to_list()),
        'solutions': ['all'] + sorted(df['Solution'].str.to_lowercase().unique().to_list()),
        'jurisdictions': ['all'] + sorted(df['Nom_Juridiction'].str.to_lowercase().unique().to_list()),
        'sources': ['all'] + sorted(df['Source'].str.to_lowercase().unique().to_list())
    }

def get_svg_content(svg_path: str) -> str:
    """
    Read SVG file content and return as string
    """
    try:
        with open(f"analytics/{svg_path}", "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading SVG file {svg_path}: {e}")
        return ""

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
            "jurisdiction_plot": "/plots/jurisdiction_distribution.svg",
            "solution_plot": "/plots/solution_distribution.svg",
            "type_plot": "/plots/recours_type_distribution.svg",
            "recours_by_month_html": get_svg_content("recours_by_month.html"),
            "solution_by_month_html": get_svg_content("solution_by_month.html"),
            "jurisdiction_by_month_html": get_svg_content("jurisdiction_by_month.html"),
            "recours_by_jurisdiction_html": get_svg_content("recours_by_jurisdiction.html"),
            "solution_by_jurisdiction_html": get_svg_content("solution_by_jurisdiction.html")
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
    form_data = await request.form()
    decision_type = form_data.get("decision_type", "all")
    recours_type = form_data.get("recours_type", "all")
    solution = form_data.get("solution", "all")
    jurisdiction = form_data.get("jurisdiction", "all")
    source = form_data.get("source", "all")
    start_date = form_data.get("start_date", None)
    end_date = form_data.get("end_date", None)
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
        filtered_df = apply_filters(df, decision_type, recours_type, solution, jurisdiction, source, start_date, end_date)
        generate_plots(filtered_df, prefix=f"{decision_type}_{recours_type}_{solution}_{jurisdiction}_{start_date}_{end_date}_{source}_")
        
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
                "jurisdiction_plot": f"/plots/{decision_type}_{recours_type}_{solution}_{jurisdiction}_{start_date}_{end_date}_{source}_jurisdiction_distribution.svg",
                "solution_plot": f"/plots/{decision_type}_{recours_type}_{solution}_{jurisdiction}_{start_date}_{end_date}_{source}_solution_distribution.svg",
                "type_plot": f"/plots/{decision_type}_{recours_type}_{solution}_{jurisdiction}_{start_date}_{end_date}_{source}_recours_type_distribution.svg",
                "recours_by_month_html": get_svg_content(f"{decision_type}_{recours_type}_{solution}_{jurisdiction}_{start_date}_{end_date}_{source}_recours_by_month.html"),
                "solution_by_month_html": get_svg_content(f"{decision_type}_{recours_type}_{solution}_{jurisdiction}_{start_date}_{end_date}_{source}_solution_by_month.html"),
                "jurisdiction_by_month_html": get_svg_content(f"{decision_type}_{recours_type}_{solution}_{jurisdiction}_{start_date}_{end_date}_{source}_jurisdiction_by_month.html") ,
                "recours_by_jurisdiction_html": get_svg_content(f"{decision_type}_{recours_type}_{solution}_{jurisdiction}_{start_date}_{end_date}_{source}_recours_by_jurisdiction.html"),
                "solution_by_jurisdiction_html": get_svg_content(f"{decision_type}_{recours_type}_{solution}_{jurisdiction}_{start_date}_{end_date}_{source}_solution_by_jurisdiction.html"),
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
