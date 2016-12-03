# -*- coding: utf-8 -*-

"""Summarization models, e.g. TF-IDF

.. module:: nlp.models.summarization
   :platform: Unix, Windows
   :synopsis: Summarization models, e.g. TF-IDF

.. |message| replace:: :class:`nlp.text.message.Message`
.. |topic| replace:: :class:`nlp.text.topic.Topic`
.. |window| replace:: :class:`nlp.text.window.Window`
.. |corpus| replace:: :class:`nlp.text.corpus.Corpus`
.. |wordcloud| replace:: :class:`nlp.viz.cloud.Wordcloud`

"""

from gensim.models.tfidfmodel import TfidfModel

import pandas as pd   # TODO: remove the necessity of using pandas (make it lighter!!)


class TFIDF(object):
    """Wraps `gensim<>`'s Tfidf class to provide some additional auxilairy functionality

    Attributes
    ----------
    corpus : |corpus|
        Corpus with one document per topid
    dictionary : `gensim.corpora.dictionary<https://radimrehurek.com/gensim/corpora/dictionary.html>`_
        Dictionary of the terms in the |corpus|
    model : `gensim.model.tfidf.TfidfModel<https://radimrehurek.com/gensim/models/tfidfmodel.html>`_
        Gensim's model implementation of the Term Frequency / Inverse Document Frequency
    """
    def __init__(self, corpus, dictionary=None, n_gram=1):
        # TODO: add n-grams !!!
        self.corpus = corpus
        self.dictionary = dictionary if dictionary else self.corpus.dictionary

        # Initialize model
        if self.dictionary:
            self.model = TfidfModel(corpus=corpus, dictionary=dictionary)
        else:
            self.model = TfidfModel(corpus=corpus)

    def get_score(self, document):
        """Generates the TF-IDF score table for each of the terms in the document

        Parameters
        ----------
        document : str
            Document to obtain a TF-IDF score

        Returns
        -------
        `pandas.DataFrame<http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html>`_
            DataFrame conatining a table with the termID, term and score of each of the terms in the document
        """
        tid = map(lambda x: x[0], document)
        trm = map(lambda x: self.dictionary.get(x[0]), document)
        scr = map(lambda x: x[1], self.model[ document ])
        return pd.DataFrame({ 'termID': tid,
                              'term': trm,
                              'score': scr })

    def get_top_terms(self, document, top=10):
        """Obtain the top terms from a document

        Parameters
        ----------
        document : str
            Document to obtain a TF-IDF score
        top : int, optional
            Number of top terms to obtain (defaults to 10)

        Returns
        -------
        list[str]
            List with the terms
        """
        return self.get_score(document).sort_values(by='score', ascending=False)[['term', 'score']].head(top)

    @staticmethod
    def score_to_int(scores):
        """Converts float scores to integers (for example, for use with the |wordcloud|)

        Parameters
        ----------
        scores : list[float]
            List of float scores

        Returns
        -------
        list[int]
            List with the converted scores as integers
        """
        return map(int, 100 * scores.values / scores.min())

