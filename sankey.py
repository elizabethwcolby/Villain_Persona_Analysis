"""
File: sankey.py
Author: Elizabeth Colby
Description: A reusable function to build a sankey
"""
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
pio.renderers.default = 'browser'


def _code_mapping(df, *cols, vals=None):
    """
    Map labels in *cols to integers

    df - DataFrame
    cols - column names for Sankey
    vals - values column

    return new_df, labels, lc_map
    """
    if vals is None:
        vals = df.columns[-1]

    # Create links between sources and targets
    data = []
    for i in range(len(cols) - 1):
        order = df[[cols[i], cols[i + 1], vals]].copy()
        order.columns = ['source', 'target', 'value']
        data.append(order)

    new_df = pd.concat(data)

    # Assign codes to labels
    labels = pd.Series(pd.concat([new_df['source'], new_df['target']])).unique()
    lc_map = {label: i for i, label in enumerate(labels)}

    new_df['source_idx'] = new_df['source'].map(lc_map)
    new_df['target_idx'] = new_df['target'].map(lc_map)

    return new_df, labels, lc_map


def make_sankey(df, *cols, vals=None, **kwargs):
    """
    Generate a sankey diagram

    df - DataFrame
    cols - column names for Sankey stages
    vals - values column (optional)
    **kwargs - optional customization

    return fig
    """
    sankey_df, all_labels, label_to_index = _code_mapping(df, *cols, vals=vals)

    # Create sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_labels
        ),
        link=dict(
            source=sankey_df['source_idx'],
            target=sankey_df['target_idx'],
            value=sankey_df['value']
        )
    )])

    return fig


def show_sankey(df, *cols, vals=None, png=None, **kwargs):
    """
    Show the sankey diagram

    df - DataFrame
    cols - column names for Sankey stages
    vals - values column (optional)
    **kwargs - optional customization
    """
    fig = make_sankey(df, *cols, vals=vals, **kwargs)
    fig.show()

    # Optionally create a png of the sankey diagram
    if png:
        fig.write_image(png)

    return fig