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
        
    Raises:
        ValueError: If the series doesn't have exactly 2 columns
    """
    _cols = series.columns
    
    # Validate column count with descriptive error
    if len(_cols) != 2:
        raise ValueError(f"Expected 2 columns in value_counts result, got {len(_cols)}: {_cols}")
    
    # Convert to lists and ensure proper types
    keys = series[_cols[0]].to_list()
    values = series[_cols[1]].to_list()
    
    # Convert values to integers and validate
    try:
        int_values = [int(v) for v in values]
    except (ValueError, TypeError) as e:
        raise ValueError(f"Count values must be integers, got: {values}") from e
    
    # Convert keys to strings for consistency
    str_keys = [str(k) for k in keys]
    
    return dict(zip(str_keys, int_values))

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
