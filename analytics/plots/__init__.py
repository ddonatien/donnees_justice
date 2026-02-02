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
    
    # Create bar plot
    ax = sns.barplot(data=top_jurisdictions, x='count', y='Nom_Juridiction', palette='viridis', hue='Nom_Juridiction', legend=False)
    
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
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
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
    plt.figure(figsize=(12, 6))

    top_distribution = distribution_df.head(top_n)
    
    # Create horizontal bar plot
    ax = sns.barplot(data=top_distribution, x='count', y='Solution', palette='coolwarm', hue='Solution', legend=False)
    
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
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    return plt.gcf()

def plot_decision_type_pie(df: pd.DataFrame, output_path: Optional[str] = None) -> plt.Figure:
    """
    Create a pie chart of decision types.
    
    Args:
        df: DataFrame with decision type distribution
        output_path: Optional path to save the plot
        
    Returns:
        Matplotlib Figure object
    """
    plt.figure(figsize=(10, 8))
    
    # Create pie chart
    plt.pie(df['count'], labels=df['Type_Decision'], autopct='%1.1f%%', 
            startangle=90, colors=sns.color_palette('pastel'))
    
    plt.title('Distribution of Decision Types', fontsize=16)
    plt.tight_layout()
    
    # Save if output path provided
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    return plt.gcf()
