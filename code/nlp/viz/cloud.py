# -*- coding: utf-8 -*-

"""Wordcloud visualization of a topic

.. module:: nlp.viz.cloud
   :platform: Unix, Windows
   :synopsis: Visualization of topics in wordclouds

.. |message| replace:: :class:`nlp.text.message.Message`
.. |topic| replace:: :class:`nlp.text.topic.Topic`
.. |window| replace:: :class:`nlp.text.window.Window`
.. |corpus| replace:: :class:`nlp.text.corpus.Corpus`
.. |model| replace:: :class:`nlp.text.models.Summarizer`

"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import wordcloud as wc
import random



class Wordcloud(object):
    """Collection of most significant words in a topic with size proporational to significance

    Attributes
    ----------
    document : list[tuples(int,int)]
        List of tuples of the term-id and the count
    model : |model|
        Model with `get_top_terms` method which (given a document and an integer n) shoots out the top–n terms with their weights
    wcloud : WordCloud
        `wordcloud` object from the package `word_cloud<https://github.com/amueller/word_cloud>`_
    max_words : int
        Maximum number of words to be shown on the wordcloud
    """

    def __init__(self, model, document_id, max_words=10, background='#FFFFFF',font=None, multi_plot=False):
        """Summary

        Parameters
        ----------
        model : |model|
            Model with `get_top_terms` method which (given a document and an integer n) shoots out the top–n terms with their weights
        document_id : int
            Index of topic to obtain the TF-IDF score
        max_words : int, optional
            Maximum number of words to be shown on the wordcloud
        background : str, optional
            Color of the background
        """
        self.model = model
        self.document_id = document_id
        self.max_words = max_words
        self.multi_plot = multi_plot

        # initialize the word cloud depending on whether a font path exists
        if font is not None:
            self.wcloud = wc.WordCloud(font_path=font, background_color=background)

        else:
            self.wcloud = wc.WordCloud(background_color=background)

        # generate the word cloud
        self.generate_wordcloud()

        # If multi_plot add a secondary unigram wordcloud
        if multi_plot:
            if font is not None:
                self.uni_wcloud = wc.WordCloud(font_path=font, background_color=background)

            else:
                self.uni_wcloud = wc.WordCloud(background_color=background)

            self.generate_uni_wordcloud()


    def generate_wordcloud(self):
        """Generates the wordcloud internally by obtaining the tokens from the model (on instantiation)
        """
        try:
            max_words = self.max_words[0]
        except:
            max_words = self.max_words

        word_score = self.model.get_top_terms(self.document_id, top=max_words)
        # word_score = [ (t, val) for t, val in zip(data.term, data.score) ]
        self.cloud_img = self.wcloud.generate_from_frequencies( word_score )
        self.wcloud.recolor(color_func=self.slack_colorize)

    def generate_uni_wordcloud(self):
        """Generates the second wordcloud internally by obtaining the tokens from the model (on instantiation)
        """
        try:
            max_words = self.max_words[1]
        except:
            max_words = self.max_words

        word_score = self.model.get_top_terms(self.document_id, top=max_words, unigram=True)
        # word_score = [ (t, val) for t, val in zip(data.term, data.score) ]
        self.uni_cloud_img = self.uni_wcloud.generate_from_frequencies( word_score )
        self.uni_wcloud.recolor(color_func=self.slack_colorize)

    @staticmethod
    def slack_colorize(word, font_size, position, orientation, random_state=None, **kwargs):
        """Recolorizes the word cloud based on slack colors
        """

        # slack colors
        slack_colors = ["#361137","#DE1D64","#24927D","#72CADB","#E7A733"]

        # generate a random number between 0 and 4 (inclusive)
        rand_int = random.randint(0,len(slack_colors)-1)

        return slack_colors[rand_int]


    def show(self, title=None):
        """Plot the wordcloud

        Parameters
        ----------
        title : str, optional
            Title of the wordcloud (optional)
        """
        # Create figure
        num_plots = 2 if self.multi_plot else 1

        fig, ax = plt.subplots(1, num_plots, figsize=(2.7 * num_plots, 2))

        if num_plots == 1:
            ax.imshow( self.wcloud.to_array() )
            if title is not None:
                plt.title(title, fontsize=10, fontweight='bold')
            plt.axis('off')

        else:
            ax[0].imshow( self.uni_wcloud.to_array() )
            ax[0].axis('off')  # remove axes
            ax[1].imshow( self.wcloud.to_array() )
            ax[1].axis('off')  # remove axes

            if title is not None:
                plt.suptitle(title, fontsize=10, fontweight='bold')

        plt.subplots_adjust(left=0.02, right=.98, top=.9, bottom=0.1)
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
        # Create figure
        num_plots = 2 if self.multi_plot else 1

        fig, ax = plt.subplots(1, num_plots, figsize=(2.7 * num_plots, 2))

        if num_plots == 1:
            ax.imshow( self.wcloud.to_array() )
            if title is not None:
                plt.title(title, fontsize=10, fontweight='bold')
            plt.axis('off')

        else:
            ax[0].imshow( self.uni_wcloud.to_array() )
            ax[0].axis('off')  # remove axes
            ax[1].imshow( self.wcloud.to_array() )
            ax[1].axis('off')  # remove axes

            if title is not None:
                plt.suptitle(title, fontsize=10, fontweight='bold')

        plt.subplots_adjust(left=0.02, right=.98, top=.9, bottom=0.1)

        # Save to path
        plt.savefig(filepath)
        plt.close()
