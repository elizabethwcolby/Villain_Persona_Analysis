"""
File: villain_api.py
Author: Elizabeth Colby
Description: The primary API for interacting with the specified files
"""
import pandas as pd
from framework import Framework


class VillainAPI:

    def __init__(self):
        self.df = None
        self.framework = Framework()

    def load_script(self, csv_path):
        """Load villain dialogue CSV and calculate sentiment"""
        self.df = pd.read_csv(csv_path)

        if 'sentiment' not in self.df.columns:
            self.df = self.framework.calculate_sentiment(self.df, text_col='dialogue')

        if 'avg_word_length' not in self.df.columns:
            self.df = self.framework.calculate_word_length(self.df, text_col='dialogue')

    def get_villain(self):
        """Get list of all villains (domain-specific)"""
        return sorted(self.df['villain'].unique())

    def get_movie(self):
        """Get list of all movies (domain-specific)"""
        return sorted(self.df['movie'].unique())

    def filter_data(self, villains, movies):
        """
        Filter data by villains and/or movies (domain-specific logic)
        """
        filtered = self.df.copy()

        if villains:
            filtered = filtered[filtered['villain'].isin(villains)]
        if movies:
            filtered = filtered[filtered['movie'].isin(movies)]

        return filtered

    def create_sentiment_plot(self, villains, chunk_size=100):
        """Create sentiment score progression scatterplot """

        if villains is None:
            villains = self.get_villain()

        filtered = self.df[self.df['villain'].isin(villains)]

        if filtered.empty:
            return None

        return self.framework.make_sentiment_progression(
            df=filtered,
            group_col='villain',
            progression_col='line_number',
            sentiment_col='sentiment',
            chunk_size=chunk_size
        )

    def create_sankey(self, villains, k=10):
        """ Create Sankey """

        if villains is None:
            villains = self.get_villain()

        filtered = self.df[self.df['villain'].isin(villains)]

        if filtered.empty:
            return None

        return self.framework.make_sankey(df=filtered, source_col='villain', target_col='word', text_col='dialogue')

    def create_avg_word_plot(self, villains):
        """ Create bar graph of average words per line by each villain"""

        if villains is None:
            villains = self.get_villain()

        filtered = self.df[self.df['villain'].isin(villains)]

        if filtered.empty:
            return None

        return self.framework.make_avg_words_plot(df=filtered, group_col='villain', wordcount_col='word_count')

    def create_sentiment_box_plot(self, villains):
        """ Create box plot of sentiment scores for each villain"""
        if villains is None:
            villains = self.get_villain()

        filtered = self.df[self.df['villain'].isin(villains)]

        if filtered.empty:
            return None

        return self.framework.make_sentiment_box_plot(df=filtered, group_col='villain', sentiment_col='sentiment')

    def create_word_length_plot(self, villains):
        """Create box plot of word length for each villain"""

        if villains is None:
            villains = self.get_villain()

        filtered = self.df[self.df['villain'].isin(villains)]

        if filtered.empty:
            return None

        return self.framework.make_word_length_plot(df=filtered, group_col='villain', complexity_col='avg_word_length')

    def get_stats(self, villains):
        """Calculate dialogue stats per villain"""

        if not villains:
            filtered = self.df
        else:
            filtered = self.df[self.df['villain'].isin(villains)]

        if filtered.empty:
            return pd.DataFrame()

        stats = filtered.groupby('villain').agg({
            'dialogue': ['count', lambda x: sum(len(str(d).split()) for d in x)],
            'sentiment': ['mean', 'std', 'min', 'max']
        }).reset_index()

        stats.columns = ['Villain', 'Total Lines', 'Total Words',
                         'Avg Sentiment', 'Sentiment Std', 'Min Sentiment', 'Max Sentiment']

        stats['Avg Words/Line'] = (stats['Total Words'] / stats['Total Lines']).round(1)

        return stats