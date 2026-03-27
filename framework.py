"""
File: framework.py
Author: Elizabeth Colby
Description: Reusable framework for comparative text analysis
"""
from collections import Counter
import pandas as pd
import plotly.express as px
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import sankey as sk


class Framework:

    def __init__(self, stopwords_file: str = 'stopwords.txt'):
        self.stopwords = self._load_stop_words(stopwords_file)
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def _load_stop_words(self, stopwords_file):
        """Load stopwords from file"""

        try:
            with open(stopwords_file, 'r') as f:
                return set(word.strip().lower() for word in f if word.strip())
        except FileNotFoundError:
            return set()

    def calculate_sentiment(self, df, text_col='text'):
        """ Calculates the sentiment score using VADER"""

        df = df.copy()
        df['sentiment'] = df[text_col].apply(
            lambda text: self.sentiment_analyzer.polarity_scores(str(text))['compound']
        )
        return df

    def make_sentiment_progression(self, df, group_col, progression_col, sentiment_col='sentiment', chunk_size=100):
        """ Make a scatterplot showing the progression of sentiment scores """

        if df.empty:
            return None

        plot_data = []
        for group_name in df[group_col].unique():
            group_df = df[df[group_col] == group_name].sort_values(progression_col)

            num_chunks = len(group_df) // chunk_size + (1 if len(group_df) % chunk_size else 0)

            for i in range(num_chunks):
                start_idx = i * chunk_size
                end_idx = min((i + 1) * chunk_size, len(group_df))
                chunk = group_df.iloc[start_idx:end_idx]

                if not chunk.empty:
                    plot_data.append({
                        group_col: group_name,
                        'chunk': i + 1,
                        'progression_range': f"{chunk[progression_col].min()}-{chunk[progression_col].max()}",
                        'avg_sentiment': chunk[sentiment_col].mean(),
                        'mid_progression': chunk[progression_col].mean()
                    })

        if not plot_data:
            return None

        df_plot = pd.DataFrame(plot_data)

        fig = px.line(
            df_plot,
            x='mid_progression',
            y='avg_sentiment',
            color=group_col,
            markers=True,
            title=f'Sentiment Progression)',
            labels={'mid_progression': progression_col.replace('_', ' ').title(),
                    'avg_sentiment': 'Average Sentiment Score'},
            hover_data=['chunk', 'progression_range']
        )

        fig.update_traces(
            line=dict(width=2),
            marker=dict(size=8, line=dict(width=1, color='white'))
        )
        fig.update_layout(
            hovermode='closest',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        return fig

    def make_sankey(self, df, source_col, target_col, text_col, k=10):
        """ Make sankey"""

        if df.empty:
            return None

        all_word_counts = {}
        for source in df[source_col].unique():
            source_df = df[df[source_col] == source]
            all_text = ' '.join(source_df[text_col].astype(str)).lower()
            words = all_text.split()
            words = [w for w in words if w not in self.stopwords and len(w) > 2]
            all_word_counts[source] = Counter(words)

        word_set = set()
        for source, counter in all_word_counts.items():
            top_words = [word for word, count in counter.most_common(k)]
            word_set.update(top_words)


        sankey_data = []
        for source, counter in all_word_counts.items():
            for word in word_set:
                count = counter.get(word, 0)
                if count > 0:
                    sankey_data.append({
                        'source': source,
                        'target': word,
                        'value': count
                    })

        if not sankey_data:
            return None

        df_sankey = pd.DataFrame(sankey_data)
        fig = sk.make_sankey(df_sankey, 'source', 'target', vals='value')

        return fig

    def make_avg_words_plot(self, df, group_col, wordcount_col='word_count'):
        """ Make a bar graph of the average words spoken"""

        if df.empty:
            return None

        verbosity = df.groupby(group_col)[wordcount_col].mean().reset_index()
        verbosity.columns = [group_col, 'avg_words']

        fig = px.bar(
            verbosity,
            x=group_col,
            y='avg_words',
            color=group_col,
            title=f'Average Words per Entry by {group_col.replace("_", " ").title()}',
            labels={'avg_words': 'Average Words'}
        )

        return fig

    def make_sentiment_box_plot(self, df, group_col, sentiment_col='sentiment'):
        """ Make a boxplot of sentiment scores """

        if df.empty:
            return None

        fig = px.box(
            df,
            x=group_col,
            y=sentiment_col,
            color=group_col,
            title=f'Sentiment Distribution by {group_col.replace("_", " ").title()}',
            labels={sentiment_col: 'Sentiment Score'}
        )

        return fig

    def calculate_word_length(self, df, text_col='text'):
        """ Calculate the average word length """

        df = df.copy()

        def avg_word_length(text):
            words = str(text).split()
            if not words:
                return 0
            return sum(len(word) for word in words) / len(words)

        df['avg_word_length'] = df[text_col].apply(avg_word_length)
        return df

    def make_word_length_plot(self, df, group_col, complexity_col='avg_word_length'):
        """ Make a box plot based on average word length """

        if df.empty:
            return None

        fig = px.box(
            df,
            x=group_col,
            y=complexity_col,
            color=group_col,
            title=f'Word Complexity Distribution by {group_col.replace("_", " ").title()}',
            labels={complexity_col: 'Average Word Length'}
        )

        return fig