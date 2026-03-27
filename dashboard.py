"""
File: dashboard.py
Author: Elizabeth Colby
Description: Creates a dashboard that allows a user to interact with data from villain_api.py
"""
import panel as pn
from villain_api import VillainAPI


pn.extension('plotly')

# Initialize API
api = VillainAPI()
api.load_script('villain_dialogues.csv')

# WIDGET DECLARATIONS

# Villain selection
villain_select = pn.widgets.MultiChoice(
    name="Select Villains",
    options=api.get_villain(),
    value=api.get_villain()[:2]  # Default to first 2 villains
)

chunk_size = pn.widgets.IntSlider(
    name="Lines per Sentiment Point",
    start=5,
    end=200,
    step=5,
    value=10
)

top_k_words = pn.widgets.IntSlider(
    name="(Sankey) Top K Words per Villain",
    start=5,
    end=20,
    step=1,
    value=10
)


# Plot dimensions
width = pn.widgets.IntSlider(name="Width", start=400, end=1600, step=100, value=1000)
height = pn.widgets.IntSlider(name="Height", start=300, end=1200, step=100, value=600)



# CALLBACK FUNCTIONS

def get_data_table(villain_select):
    """Create data table"""

    villains = villain_select if villain_select else None
    filtered_df = api.filter_data(villains, None)
    table = pn.widgets.Tabulator(
        filtered_df[['villain', 'movie', 'line_number', 'dialogue']],
        selectable=False,
        pagination='local',
        page_size=15
    )
    return table


def get_sentiment_plot(villain_select, chunk_size, width, height):
    """Create sentiment score progression scatterplot """

    villains = villain_select if villain_select else None
    fig = api.create_sentiment_plot(villains, chunk_size=chunk_size)

    if fig:
        fig.update_layout(
            width=width,
            height=height,
            title="Villain Sentiment Progression Throughout Movie"
        )
        return fig
    else:
        return "No data available for selected villains"


def get_sankey_plot(villain_select, top_k_words, width, height):
    """Create Sankey"""
    villains = villain_select if villain_select else None
    fig = api.create_sankey(villains, k=top_k_words)

    if fig:
        fig.update_layout(
            width=width,
            height=height,
            title=f"Villain to Top {top_k_words} Most Common Words"
        )
        return fig
    else:
        return "No data available for selected filters"


def get_avg_word_plot(villain_select, width, height):
    """Create bar graph of average words per line by each villain"""

    villains = villain_select if villain_select else None
    fig = api.create_avg_word_plot(villains)

    if fig:
        fig.update_layout(
            width=width,
            height=height,
            title="Average Words Per Line by Villain"
        )
        return fig
    else:
        return "No data available for selected villains"


def get_sentiment_box_plot(villain_select, width, height):
    """Create box plot of sentiment scores for each villain"""

    villains = villain_select if villain_select else None
    fig = api.create_sentiment_box_plot(villains)

    if fig:
        fig.update_layout(
            width=width,
            height=height,
            title="Sentiment Distribution by Villain"
        )
        return fig
    else:
        return "No data available for selected villains"


def get_word_length_plot(villain_select, width, height):
    """Create box plot of word length for each villain"""

    villains = villain_select if villain_select else None
    fig = api.create_word_length_plot(villains)

    if fig:
        fig.update_layout(
            width=width,
            height=height,
            title="Word Complexity Distribution by Villain"
        )
        return fig
    else:
        return "No data available for selected villains"


def get_stats_table(villain_select):
    """Create a data table of stats per villain"""
    villains = villain_select if villain_select else None
    stats_df = api.get_stats(villains)
    table = pn.widgets.Tabulator(
        stats_df,
        selectable=False,
        page_size=10
    )
    return table


# CALLBACK BINDINGS

data_table = pn.bind(get_data_table, villain_select)
sentiment_plot = pn.bind(get_sentiment_plot, villain_select, chunk_size, width, height)
sankey_plot = pn.bind(get_sankey_plot, villain_select, top_k_words, width, height)
verbosity_plot = pn.bind(get_avg_word_plot, villain_select, width, height)
sentiment_box_plot = pn.bind(get_sentiment_box_plot, villain_select, width, height)
word_complexity_plot = pn.bind(get_word_length_plot, villain_select, width, height)
stats_table = pn.bind(get_stats_table, villain_select)


# DASHBOARD WIDGET CONTAINERS

card_width = 320

filter_card = pn.Card(
    pn.Column(
        villain_select
    ),
    title="Filter Settings", width=card_width, collapsed=False
)

analysis_card = pn.Card(
    pn.Column(
        top_k_words,
        chunk_size
    ),
    title="Analysis Settings", width=card_width, collapsed=False
)

plot_card = pn.Card(
    pn.Column(
        width,
        height
    ),
    title="Plot Dimensions", width=card_width, collapsed=True
)


# LAYOUT

layout = pn.template.FastListTemplate(
    title="Villain Dialogue Analysis",
    sidebar=[
        filter_card,
        analysis_card,
        plot_card
    ],
    theme_toggle=False,
    main=[
        pn.Tabs(
            ("Data", data_table),
            ("Sentiment Score Progression", sentiment_plot),
            ("Sentiment Distribution", sentiment_box_plot),
            ("Sankey Network", sankey_plot),
            ("Average Words Comparison", verbosity_plot),
            ("Word Length", word_complexity_plot),
            ("Stats", stats_table),
            active=1
        )
    ],
    header_background='#8B0000'
).servable()

layout.show()