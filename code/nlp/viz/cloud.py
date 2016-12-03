# -*- coding: utf-8 -*-

"""Wordcloud visualization of a topic

.. module:: nlp.models.cloud
   :platform: Unix, Windows
   :synopsis: Visualization of topics in wordclouds

.. |message| replace:: :class:`nlp.text.message.Message`
.. |topic| replace:: :class:`nlp.text.topic.Topic`
.. |window| replace:: :class:`nlp.text.window.Window`
.. |corpus| replace:: :class:`nlp.text.corpus.Corpus`
.. |model| replace:: :class:`nlp.text.models.Summarizer`

"""

import matplotlib.pyplot as plt
import wordcloud as wc



class Wordcloud(object):
    """docstring for Word

    Attributes
    ----------
    document : list[tuples(int,int)]
        List of tuples of the term-id and the count
    model : |model|
        Model with `get_top_terms` method which (given a document and an integer n) shoots out the top–n terms with their weights
    wcloud : WordCloud
        wordcloud object from the package `word_cloud<https://github.com/amueller/word_cloud>`_
    max_words : int
        Maximum number of words to be shown on the wordcloud
    """
    def __init__(self, model, document, max_words=10, background='#e9e9e9'):
        """Summary

        Parameters
        ----------
        model : |model|
            Model with `get_top_terms` method which (given a document and an integer n) shoots out the top–n terms with their weights
        document : list[tuples(int,int)]
            List of tuples of the term-id and the count
        max_words : int, optional
            Maximum number of words to be shown on the wordcloud
        background : str, optional
            Color of the background
        """
        self.model = model
        self.document = document
        self.max_words = max_words

        self.wcloud = wc.WordCloud(background_color=background)
        self.generate_wordcloud()

    def generate_wordcloud(self):
        """Generates the wordcloud internally by obtaining the tokens from the model (on instantiation)
        """
        data = self.model.get_top_terms(self.document, self.max_words)
        word_score = [ (t, val) for t, val in zip(data.term, data.score) ]
        self.cloud_img = self.wcloud.generate_from_frequencies( word_score )


    def show(self, title=None):
        """Plot the wordcloud

        Parameters
        ----------
        title : str, optional
            Title of the wordcloud (optional)
        """
        plt.imshow(self.wcloud.to_array())

        if title is not None:
            plt.title(title, fontsize=15, fontweight='bold')

        plt.axis('off')  # remove axes
        plt.show()

    def save_png(self, filepath, title=None):
        """Summary

        Parameters
        ----------
        filepath : str
            Path to the file where the wordcloud will be stored to
        title : str, optional
            Title of the wordcloud (optional)
       """
        fig = plt.imshow(self.wcloud.to_array())

        if title is not None:
            plt.title(title, fontsize=15, fontweight='bold')

        # Adjust axis and margins
        plt.axis('off')
        plt.subplots_adjust(left=0.02, right=.98, top=.9, bottom=0.1)

        # Save to path
        plt.savefig(filepath)
        plt.close()
