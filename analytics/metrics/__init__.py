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

def compute_jurisdiction_distribution(df: pl.DataFrame) -> Dict[str, int]:
    """
    Compute distribution of decisions by jurisdiction.
    
    Args:
        df: Polars DataFrame containing court decisions
        
    Returns:
        Pandas DataFrame with jurisdiction distribution
    """
    return collate_counts(df.group_by('Nom_Juridiction').count().sort('count', descending=True))

def compute_solution_distribution(df: pl.DataFrame) -> Dict[str, int]:
    """
    Compute distribution of decisions by solution type.
    
    Args:
        df: Polars DataFrame containing court decisions
        
    Returns:
        Pandas DataFrame with solution distribution
    """
    return collate_counts(df.group_by('Solution').count().sort('count', descending=True))
