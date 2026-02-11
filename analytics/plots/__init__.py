# Plot specifications
import xml.etree.ElementTree as ET
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional

def plot_jurisdiction_distribution(distribution_df: pd.DataFrame, 
                                  output_path: Optional[str] = None,
                                  top_n: int = 10) -> plt.Figure:
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
    _top_jurisdictions_processed['Nom_Juridiction'] = _top_jurisdictions_processed['Nom_Juridiction'].str.replace('Cour administrative d\'appel de ', 'CAA ')
    _top_jurisdictions_processed['Nom_Juridiction'] = _top_jurisdictions_processed['Nom_Juridiction'].str.replace('Cour Administrative d\'Appel de ', 'CAA ')
    _top_jurisdictions_processed['Nom_Juridiction'] = _top_jurisdictions_processed['Nom_Juridiction'].str.replace('COUR ADMINISTRATIVE D\'APPEL DE ', 'CAA ')
    _top_jurisdictions_processed['Nom_Juridiction'] = _top_jurisdictions_processed['Nom_Juridiction'].str[:22]  # Truncate long names for better display
    _top_jurisdictions_processed['count'] /= distribution_df['count'].sum()
    
    # Create bar plot
    ax = sns.barplot(data=_top_jurisdictions_processed, x='count', y='Nom_Juridiction', palette='viridis', hue='Nom_Juridiction', legend=False)
    sns.despine(left=True, bottom=True)
    
    # Customize plot
    # plt.title(f'Top {top_n} Jurisdictions by Number of Decisions', fontsize=16)
    ax.set(xlabel=None, ylabel=None)
    ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tight_layout()
    
    # Add value labels
    for i, v in enumerate(_top_jurisdictions_processed['count']):
        ax.text(v + 0.001, i, f'{v:.2%}', color='black', fontsize=10)
    
    # Save if output path provided
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight', transparent=True)
        plt.close()
    
    return plt.gcf()

def plot_solution_distribution(distribution_df: pd.DataFrame, 
                              output_path: Optional[str] = None,
                              top_n: int = 10) -> plt.Figure:
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
    _top_distribution_processed['count'] /= distribution_df['count'].sum()
    
    # Create horizontal bar plot
    ax = sns.barplot(data=_top_distribution_processed, x='count', y='Solution', palette='coolwarm', hue='Solution', legend=False)
    sns.despine(left=True, bottom=True)
    
    # Customize plot
    # plt.title('Decision Distribution by Solution Type', fontsize=16)
    ax.set(xlabel=None, ylabel=None)
    ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tight_layout()
    
    # Add value labels
    for i, v in enumerate(_top_distribution_processed['count']):
        ax.text(v + 0.001, i, f'{v:.2%}', color='black', fontsize=10)
    
    # Save if output path provided
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight', transparent=True)
        plt.close()
    
    return plt.gcf()

def plot_recours_type_distribution(distribution_df: pd.DataFrame, output_path: Optional[str] = None, top_n: int = 10) -> plt.Figure:
    """
    Create a bar plot chart of recours types.
    
    Args:
        df: DataFrame with recours type distribution
        output_path: Optional path to save the plot
        
    Returns:
        Matplotlib Figure object
    """
    plt.figure(figsize=(12, 8))

    top_distribution = distribution_df.head(top_n)
    _top_distribution_processed = top_distribution.copy()
    _top_distribution_processed['Type_Recours'] = _top_distribution_processed['Type_Recours'].str[:22]  # Truncate long names for better display
    _top_distribution_processed['count'] /= distribution_df['count'].sum()
    
    # Create bar plot
    ax = sns.barplot(data=_top_distribution_processed, x='count', y='Type_Recours', palette='coolwarm', hue='Type_Recours', legend=False)
    sns.despine(left=True, bottom=True)
    
    # plt.title('Distribution of Recours Types', fontsize=16)
    ax.set(xlabel=None, ylabel=None)
    ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tight_layout()
    
    for i, v in enumerate(_top_distribution_processed['count']):
        ax.text(v + 0.001, i, f'{v:.2%}', color='black', fontsize=10)
    # Save if output path provided
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight', transparent=True)
        plt.close()
    
    return plt.gcf()

def stacked_plot_by_month(proportions_df: pd.DataFrame, output_path: Optional[str] = None) -> plt.Figure:
    """
    Create a stacked line plot of proportions by month.
    
    Args:
        proportions_df: DataFrame with proportions by month
        output_path: Optional path to save the plot
    Returns:
        Matplotlib Figure object
    """
    # plt.figure(figsize=(14, 8))

    proportions_df = proportions_df.sort_values('month')
    proportions_df = proportions_df.rename(columns=lambda c: c.replace('tribunal administratif', 'TA').replace('cour d\'appel', 'CA').replace('conseil de prud\'hommes', 'CPH').replace('tribunal de commerce', 'TC').replace('cour de cassation', 'Cass').replace('cour d\'assises', 'Assises').replace('tribunal des conflits', 'TCF').replace('cour administrative d\'appel', 'CAA'))
    top_columns = proportions_df.drop(columns='month').sum().sort_values(ascending=False).head(5).index
    columns_to_plot = top_columns.tolist()
    other_cols = [
        c for c in proportions_df.columns
        if c not in columns_to_plot and c != "month"
    ]
    proportions_df["other"] = proportions_df[other_cols].sum(axis=1)
    columns_to_plot.append("other")

    pfig = px.area(proportions_df, x='month', y=columns_to_plot,
                   labels={'value': 'Value', 'month': 'Month'},
                   color_discrete_sequence=px.colors.cyclical.Twilight)
    pfig.update_layout(showlegend=True, legend_title_text='',
                       xaxis_title=None, yaxis_title=None,
                       xaxis_tickformat='%Y-%m', xaxis_tickangle=45,
                       plot_bgcolor='white', margin=dict(l=40, r=40, t=40, b=40))
    pfig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))
    pfig.update_xaxes(showgrid=False)
    pfig.update_yaxes(showgrid=False)

    # fig, ax = plt.subplots(figsize=(14, 8))
    
    # stacks = ax.stackplot(proportions_df['month'], 
    #               proportions_df[columns_to_plot].T,
    #               labels=[col if col != '' else '<empty>' for col in columns_to_plot],
    #               colors=['white', 'white', 'white', 'white', 'white', 'white'],
    #               edgecolor='black',
    #               hatch='///',
    #               alpha=0.8)
    
    # hatches = ["o|", "o-", "o+", "o/", "o\\", "o*"]

    # for poly, hatch in zip(stacks, hatches):
    #     poly.set_hatch(hatch)
    # ax.legend(loc='upper left', bbox_to_anchor=(1, 1)) 

    # # Customize plot
    # # plt.title('Proportion of Solutions by Month', fontsize=16)
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # ax.spines['left'].set_visible(False)
    # ax.spines['bottom'].set_visible(False)
    # ax.tick_params(left=False, bottom=False)
    # plt.xlabel(None)
    # plt.ylabel(None)
    # plt.xticks(rotation=45)
    # plt.tight_layout()
    
    # Save if output path provided
    if output_path:
        # plt.savefig(output_path, dpi=300, bbox_inches='tight', transparent=True)
        # plt.close()
        pfig.write_html(
            output_path.replace('.svg', '.html'),
            include_plotlyjs="cdn",   # or True for fully self-contained
            full_html=False           # important for embedding
        )

    return pfig

def scatter_hist_by_jurisdiction(df: pd.DataFrame, query: str, output_path: Optional[str] = None) -> plt.Figure:
    """
    Create a scatter plot of decisions by jurisdiction.
    
    Args:
        df: DataFrame with court decisions
        output_path: Optional path to save the plot
        
    Returns:
        Matplotlib Figure object
    """
    df['Nom_Juridiction'] = df['Nom_Juridiction'].str.replace('Cour d\'appel de ', 'CA ')
    df['Nom_Juridiction'] = df['Nom_Juridiction'].str.replace('Tribunal de grande instance de ', 'TGI ') 
    df['Nom_Juridiction'] = df['Nom_Juridiction'].str.replace('Tribunal de commerce de ', 'TC ') 
    df['Nom_Juridiction'] = df['Nom_Juridiction'].str.replace('Conseil de prud\'hommes de ', 'CPH ') 
    df['Nom_Juridiction'] = df['Nom_Juridiction'].str.replace('Tribunal Administratif de ', 'TA ') 
    df['Nom_Juridiction'] = df['Nom_Juridiction'].str.replace('Tribunal Administratif d ', 'TA ') 
    df['Nom_Juridiction'] = df['Nom_Juridiction'].str.replace('Tribunal Administratif d\'', 'TA ') 
    df['Nom_Juridiction'] = df['Nom_Juridiction'].str.replace('Tribunal Administratif', 'TA ') 
    df['Nom_Juridiction'] = df['Nom_Juridiction'].str.replace('Cour de cassation', 'Cass')
    df['Nom_Juridiction'] = df['Nom_Juridiction'].str.replace('Cour d\'assises', 'Assises ')
    df['Nom_Juridiction'] = df['Nom_Juridiction'].str.replace('Tribunal des conflits', 'TCF ')
    df['Nom_Juridiction'] = df['Nom_Juridiction'].str.replace('Cour administrative d\'appel de ', 'CAA ')
    df['Nom_Juridiction'] = df['Nom_Juridiction'].str.replace('Cour Administrative d\'Appel de ', 'CAA ')
    df['Nom_Juridiction'] = df['Nom_Juridiction'].str.replace('COUR ADMINISTRATIVE D\'APPEL DE ', 'CAA ')
    df['Nom_Juridiction'] = df['Nom_Juridiction'].str.replace('Cour d\'appel administrative de ', 'CAA ')

    bins = pd.cut(df[query], bins=30)

    agg = (
        df.groupby(bins)
        .agg(
            count=(query, "size"),
            names=("Nom_Juridiction", lambda x: "<br>".join(
                ", ".join(x[i:i+3]) for i in range(0, len(x), 3)
            ))
        )
        .reset_index()
    )
    agg["bin_center"] = agg[query].apply(lambda x: x.mid)
    agg["bin_interval"] = agg[query].apply(lambda x: f"[{x.left:.2f}, {x.right:.2f})")
    pfig = go.Figure()
    print(agg['bin_interval'])

    #Set twighlight color scale
    tcolors = px.colors.cyclical.Twilight
    pfig.add_bar(
        x=agg["bin_center"],
        y=agg["count"],
        customdata= agg[["bin_interval", "names"]],
        hovertemplate=(
            "Interval: %{customdata[0]}<br>"
            "Count: %{y}<br>"
            "Names:<br>%{customdata[1]}"
            "<extra></extra>"
        )
        ).update_traces(marker_color=tcolors[3])

    pfig.update_layout(showlegend=False, legend_title_text='',
                       xaxis_title=None, yaxis_title=None,
                       xaxis_tickangle=45,
                       plot_bgcolor='white', margin=dict(l=40, r=40, t=40, b=40))

    pfig.update_xaxes(showgrid=False)
    pfig.update_yaxes(showgrid=False)

    if output_path:
        pfig.write_html(
            output_path.replace('.svg', '.html'),
            include_plotlyjs="cdn",   # or True for fully self-contained
            full_html=False           # important for embedding
        )

    return pfig

    