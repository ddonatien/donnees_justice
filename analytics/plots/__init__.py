# Plot specifications
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Optional

def plot_jurisdiction_distribution(distribution_df: pd.DataFrame, 
                                  output_path: Optional[str] = None,
                                  top_n: int = 20) -> plt.Figure:
    """
    Create a bar plot of decision distribution by jurisdiction.
    
    Args:
        distribution_df: DataFrame with jurisdiction distribution
        output_path: Optional path to save the plot
        top_n: Number of top jurisdictions to show
        
    Returns:
        Matplotlib Figure object
    """
    plt.figure(figsize=(12, 8))
    
    # Get top N jurisdictions
    top_jurisdictions = distribution_df.head(top_n)
    _top_jurisdictions_processed = top_jurisdictions.copy()
    _top_jurisdictions_processed['Nom_Juridiction'] = _top_jurisdictions_processed['Nom_Juridiction'].str.replace('Cour d\'appel de ', 'CA ')
    _top_jurisdictions_processed['Nom_Juridiction'] = _top_jurisdictions_processed['Nom_Juridiction'].str.replace('Tribunal de grande instance de ', 'TGI ') 
    _top_jurisdictions_processed['Nom_Juridiction'] = _top_jurisdictions_processed['Nom_Juridiction'].str.replace('Tribunal de commerce de ', 'TC ') 
    _top_jurisdictions_processed['Nom_Juridiction'] = _top_jurisdictions_processed['Nom_Juridiction'].str.replace('Conseil de prud\'hommes de ', 'CPH ') 
    _top_jurisdictions_processed['Nom_Juridiction'] = _top_jurisdictions_processed['Nom_Juridiction'].str.replace('Tribunal Administratif de ', 'TA ') 
    _top_jurisdictions_processed['Nom_Juridiction'] = _top_jurisdictions_processed['Nom_Juridiction'].str.replace('Tribunal Administratif d\'', 'TA ') 
    _top_jurisdictions_processed['Nom_Juridiction'] = _top_jurisdictions_processed['Nom_Juridiction'].str.replace('Cour de cassation', 'Cass')
    _top_jurisdictions_processed['Nom_Juridiction'] = _top_jurisdictions_processed['Nom_Juridiction'].str.replace('Cour d\'assises', 'Assises ')
    _top_jurisdictions_processed['Nom_Juridiction'] = _top_jurisdictions_processed['Nom_Juridiction'].str.replace('Tribunal des conflits', 'TCF ')
    _top_jurisdictions_processed['Nom_Juridiction'] = _top_jurisdictions_processed['Nom_Juridiction'].str.replace('Cour administrative d\'appel de ', 'CAA ')
    _top_jurisdictions_processed['Nom_Juridiction'] = _top_jurisdictions_processed['Nom_Juridiction'].str.replace('Cour d\'appel administrative de ', 'CAA ')
    _top_jurisdictions_processed['Nom_Juridiction'] = _top_jurisdictions_processed['Nom_Juridiction'].str[:22]  # Truncate long names for better display
    
    # Create bar plot
    ax = sns.barplot(data=_top_jurisdictions_processed, x='count', y='Nom_Juridiction', palette='viridis', hue='Nom_Juridiction', legend=False)
    sns.despine(left=True, bottom=True)
    
    # Customize plot
    plt.title(f'Top {top_n} Jurisdictions by Number of Decisions', fontsize=16)
    plt.xlabel('Number of Decisions', fontsize=12)
    plt.ylabel('Jurisdiction Name', fontsize=12)
    plt.tight_layout()
    
    # Add value labels
    for i, v in enumerate(top_jurisdictions['count']):
        ax.text(v + 5, i, str(v), color='black', fontsize=10)
    
    # Save if output path provided
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight', transparent=True)
        plt.close()
    
    return plt.gcf()

def plot_solution_distribution(distribution_df: pd.DataFrame, 
                              output_path: Optional[str] = None,
                              top_n: int = 20) -> plt.Figure:
    """
    Create a bar plot of decision distribution by solution type.
    
    Args:
        distribution_df: DataFrame with solution distribution
        output_path: Optional path to save the plot
        top_n: Number of top solution types to show
    Returns:
        Matplotlib Figure object
    """
    plt.figure(figsize=(12, 8))

    top_distribution = distribution_df.head(top_n)
    _top_distribution_processed = top_distribution.copy()
    _top_distribution_processed['Solution'] = _top_distribution_processed['Solution'].str[:22]  # Truncate long names for better display
    
    # Create horizontal bar plot
    ax = sns.barplot(data=_top_distribution_processed, x='count', y='Solution', palette='coolwarm', hue='Solution', legend=False)
    sns.despine(left=True, bottom=True)
    
    # Customize plot
    plt.title('Decision Distribution by Solution Type', fontsize=16)
    plt.xlabel('Number of Decisions', fontsize=12)
    plt.ylabel('Solution Type', fontsize=12)
    plt.tight_layout()
    
    # Add value labels
    for i, v in enumerate(top_distribution['count']):
        ax.text(v + 5, i, str(v), color='black', fontsize=10)
    
    # Save if output path provided
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight', transparent=True)
        plt.close()
    
    return plt.gcf()

def plot_recours_type_distribution(distribution_df: pd.DataFrame, output_path: Optional[str] = None) -> plt.Figure:
    """
    Create a bar plot chart of recours types.
    
    Args:
        df: DataFrame with recours type distribution
        output_path: Optional path to save the plot
        
    Returns:
        Matplotlib Figure object
    """
    plt.figure(figsize=(12, 8))

    top_distribution = distribution_df.head(20)
    _top_distribution_processed = top_distribution.copy()
    _top_distribution_processed['Type_Recours'] = _top_distribution_processed['Type_Recours'].str[:22]  # Truncate long names for better display
    
    # Create bar plot
    ax = sns.barplot(data=_top_distribution_processed, x='count', y='Type_Recours', palette='coolwarm', hue='Type_Recours', legend=False)
    sns.despine(left=True, bottom=True)
    
    plt.title('Distribution of Recours Types', fontsize=16)
    plt.xlabel('Number of Recours', fontsize=12)
    plt.ylabel('Recours Type', fontsize=12)
    plt.tight_layout()
    
    for i, v in enumerate(_top_distribution_processed['count']):
        ax.text(v + 5, i, str(v), color='black', fontsize=10)
    # Save if output path provided
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight', transparent=True)
        plt.close()
    
    return plt.gcf()
