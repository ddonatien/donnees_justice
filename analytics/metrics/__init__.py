# Metrics calculations
import polars as pl
from typing import Dict, Any
import pandas as pd

def collate_counts(series: pl.Series) -> Dict[str, int]:
    """
    Collate counts from a Polars DataFrame into a dictionary.
    
    Args:
        series: Polars Series with values to count

    Returns:
        Dictionary mapping values to their counts
    """
    _cols = series.columns
    assert len(_cols) == 2
    return dict(zip(*[series[c].to_list() for c in _cols]))

def compute_summary(df: pl.DataFrame) -> Dict[str, Any]:
    """
    Compute summary statistics for court decisions data.
    
    Args:
        df: Polars DataFrame containing court decisions
        
    Returns:
        Dictionary with summary statistics
    """
    summary = {
        'total_decisions': len(df),
        'jurisdictions': df['Nom_Juridiction'].n_unique(),
        'date_range': {
            'min_date': df['Date_Lecture'].min(),
            'max_date': df['Date_Lecture'].max()
        },
        'decision_types': collate_counts(df['Type_Decision'].value_counts()), 
        'solution_types': collate_counts(df['Solution'].value_counts()),
        'publication_codes': collate_counts(df['Code_Publication'].value_counts())
    }
    
    return summary

def compute_jurisdiction_distribution(df: pl.DataFrame) -> pd.DataFrame:
    """
    Compute distribution of decisions by jurisdiction.
    
    Args:
        df: Polars DataFrame containing court decisions
        
    Returns:
        Pandas DataFrame with jurisdiction distribution
    """
    return df.group_by('Nom_Juridiction').count().sort('count', descending=True).to_pandas()

def compute_solution_distribution(df: pl.DataFrame) -> pd.DataFrame:
    """
    Compute distribution of decisions by solution type.
    
    Args:
        df: Polars DataFrame containing court decisions
        
    Returns:
        Pandas DataFrame with solution distribution
    """
    return df.group_by('Solution').count().sort('count', descending=True).to_pandas()

def compute_recours_type_distribution(df: pl.DataFrame) -> pd.DataFrame:
    """
    Compute distribution of decisions by recours type.
    
    Args:
        df: Polars DataFrame containing court decisions
        
    Returns:
        Pandas DataFrame with recours type distribution
    """
    return df.group_by('Type_Recours').count().sort('count', descending=True).to_pandas()   

def aggregate_entry_by_month(df: pl.DataFrame, entry_name: str, prop: bool) -> pd.DataFrame:
    """
    Compute proportions of decisions by month.
    
    Args:
        df: Polars DataFrame containing court decisions
        
    Returns:
        Pandas DataFrame with proportions by month
    """
    _processed_df = df.with_columns(
        pl.col("Date_Lecture").str.to_date().alias("date")
    ).sort("date")
    _processed_df = _processed_df.with_columns(
        pl.col(entry_name).str.to_lowercase().alias(entry_name)
    )
    counts = (
        _processed_df.with_columns(month=pl.col("date").dt.truncate("1mo"))
        .group_by(["month", entry_name])
        .agg(pl.count().alias("count"))
    )
    wide = (
        counts
        .pivot(
            index="month",
            columns=entry_name,
            values="count",
            aggregate_function="sum"
        )
        .fill_null(0)
    )
    if prop:
        proportions = wide.with_columns(
            pl.exclude("month") /
            pl.sum_horizontal(pl.exclude("month"))
        )
        return proportions.to_pandas()
    else:
        return wide.to_pandas()

def aggregate_entry_by_jurisdiction(df: pl.DataFrame, entry_name: str, prop: bool) -> pd.DataFrame:
    """
    Compute proportions of decisions by jurisdiction.
    
    Args:
        df: Polars DataFrame containing court decisions
        
    Returns:
        Pandas DataFrame with proportions by jurisdiction
    """
    _processed_df = df.with_columns(
        pl.col("Date_Lecture").str.to_date().alias("date")
    ).sort("date")
    _processed_df = _processed_df.with_columns(
        pl.col(entry_name).str.to_lowercase().alias(entry_name)
    )
    _processed_df = _processed_df.group_by(["Nom_Juridiction", entry_name]).agg(pl.count().alias("count"))
    wide = (
        _processed_df
        .pivot(
            index="Nom_Juridiction",
            columns=entry_name,
            values="count",
            aggregate_function="sum"
        )
        .fill_null(0)
    )
    if prop:
        proportions = wide.with_columns(
            pl.exclude("Nom_Juridiction") /
            pl.sum_horizontal(pl.exclude("Nom_Juridiction"))
        )
        return proportions.to_pandas()
    else:
        return wide.to_pandas()