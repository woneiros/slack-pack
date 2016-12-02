# -*- coding: utf-8 -*-

"""Summarization models, e.g. TF-IDF

.. module:: nlp.models.cloud
   :platform: Unix, Windows
   :synopsis: Summarization models, e.g. TF-IDF

.. |message| replace:: :class:`nlp.text.message.Message`
.. |topic| replace:: :class:`nlp.text.topic.Topic`
.. |window| replace:: :class:`nlp.text.window.Window`
.. |corpus| replace:: :class:`nlp.text.corpus.Corpus`

"""

import matplotlib.pyplot as plt
import wordcloud as wc


# TODO: Document Wordcloud

class Wordcloud(object):
    """docstring for Word"""
    def __init__(self, model, document, words_show=10, background='#e9e9e9'):
        self.model = model
        self.document = document
        self.words_show = words_show

        self.wcloud = wc.WordCloud(background_color=background)
        self.cloud_img = None
        self.generate_wordcloud()

    def generate_wordcloud(self):
        data = self.model.get_top_terms(self.document, self.words_show)
        word_score = [ (t, val) for t, val in zip(data.term, data.score) ]
        self.cloud_img = self.wcloud.generate_from_frequencies( word_score )

    def show(self, title=None):
        plt.imshow(self.wcloud.to_array())

        if title is not None:
            plt.title(title, fontsize=15, fontweight='bold')

        plt.axis('off')  # remove axes
        plt.show()

    def save_png(self, filepath, title=None):
        fig = plt.imshow(self.wcloud.to_array())

        if title is not None:
            plt.title(title, fontsize=15, fontweight='bold')

        # Adjust axis and margins
        plt.axis('off')
        plt.subplots_adjust(left=0.02, right=.98, top=.9, bottom=0.1)

        # Save to path
        plt.savefig(filepath)
        plt.close()
