# Metrics calculations
import polars as pl
from typing import Dict, Any
import pandas as pd

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
        'decision_types': df['Type_Decision'].value_counts().to_dict(),
        'solution_types': df['Solution'].value_counts().to_dict(),
        'publication_codes': df['Code_Publication'].value_counts().to_dict()
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
