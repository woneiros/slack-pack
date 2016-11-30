# -*- coding: utf-8 -*-

"""Corpus with the parsed documents of the topics

.. module:: nlp.text.corpus
   :platform: Unix, Windows
   :synopsis: Corpus containing one (processed) document per topic

.. |message| replace:: :class:`nlp.text.message.Message`
.. |topic| replace:: :class:`nlp.text.topic.Topic`
.. |window| replace:: :class:`nlp.text.window.Window`
.. |tfidf| replace:: :class:`nlp.models.summarization.TFIDF`

"""

from collections import Counter
import cPickle as pk
from gensim import corpora

from topic import Topic
from window import Window


def from_window(window, cleaner=None):
    """Generates a :class: `nlp.text.corpus.Corpus` from a given |window|

    Parameters
    ----------
    window : |window|
        Window containing messages already classified into several topics
    cleaner : callable, optional
        Function that gets a str and returns a str back (meant for cleaning and removing stopwords)

    Returns
    -------
    :class : `nlp.text.corpus.Corpus`
        A :class: `nlp.text.corpus.Corpus` of the topics (each topic as a document containing all messages)
    """
    cleaner = cleaner if cleaner is not None else lambda x: x
    return Corpus([ ' '.join( map(lambda msg: cleaner(msg.text), tpc) ).lower().split() for tpc in window ] )


def from_documents(documents):
    """Generates a :class: `nlp.text.corpus.Corpus` from a given list of documents

    Parameters
    ----------
    documents : list[str]
        List of document strings

    Returns
    -------
    :class: `nlp.text.corpus.Corpus`
        A :class: `nlp.text.corpus.Corpus` of the topics (each topic as a document containing all messages)
    """
    return Corpus([ doc.split() for doc in documents ])


def load_corpus(filepath):
    """Load a pickled :class: `nlp.text.corpus.Corpus`

    Parameters
    ----------
    filepath : str or IO
        Path to the pickle with the :class: `nlp.text.corpus.Corpus`

    Returns
    -------
    :class: `nlp.text.corpus.Corpus`
        A corpus of the topics (each topic as a document containing all messages)
    """
    with open(filepath, 'rb') as f:
        corpus = pk.load(f)
    return corpus


class Corpus(object):
    """docstring for Corpus"""
    def __init__(self, document_wordlist, min_count=0):
        self.document_wordlist = document_wordlist  # word list for every topic

        # Generate a word counter
        self.token_count = Counter( reduce(lambda x,y: x+y, self.document_wordlist) )  # the flatenned list of words

        # Remove infrequent words if specified
        if min_count:
            self.document_wordlist = map(lambda doc: filter(lambda token: self.token_count[token] >= min_count, doc), self.document_wordlist)

        # Generate corpus
        self.dictionary = corpora.Dictionary(self.document_wordlist)
        self.corpus = [ self.dictionary.doc2bow(tpc) for tpc in self.document_wordlist ]

    def __getitem__(self, item):
        return self.corpus[item]

    def save(self, filepath):
        """Saves object into a pickled file

        Parameters
        ----------
        filepath : str or IO
            Path to the desired output pickle
        """
        with open(filepath, 'wb') as f:
            pk.dump(self, f)

