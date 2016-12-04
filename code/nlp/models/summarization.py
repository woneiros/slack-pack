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

# For our internal toolbox imports
import os, sys
path_to_here = os.path.abspath('.')
sys.path.append(path_to_here[:path_to_here.index('code')+4])

from nlp.text.corpus import Corpus
from nlp.grammar.tokenizer import SimpleCleaner



class TFIDF(object):
    """Wraps `gensim<>`'s Tfidf class to provide some additional auxilairy functionality

    The TF-IDF score is produced with the unigram token's score, however an a n-gram corpus may be specified to serve as basic visualization units.

    Attributes
    ----------
    corpus : |corpus|
        Corpus with one document per topic
    dictionary : `gensim.corpora.dictionary<https://radimrehurek.com/gensim/corpora/dictionary.html>`_
        Dictionary of the terms in the |corpus|
    model : `gensim.model.tfidf.TfidfModel<https://radimrehurek.com/gensim/models/tfidfmodel.html>`_
        Gensim's model implementation of the Term Frequency / Inverse Document Frequency
    n_gram_corpus : |corpus|
        Additional corpus with one document per topic containing n-gram's as base tokens (scores will be produced as the sum of the unigram scores)
    """
    def __init__(self, window, cleaner=None, n_grams=1):
        """Generate a TFIDF model object

        Parameters
        ----------
        window : |window|
            Window containing messages already classified into several topics
        cleaner : callable, optional
            Function that gets a str and returns a str back (meant for cleaning and removing stopwords)
        n_grams : int, optional
            Number of words to be grouped together and considered a unit token for the corpus (defaults to 1)
        """
        self.window = window
        self.n_grams = n_grams

        # Generate corpus from window
        cleaner = cleaner if cleaner is not None else lambda x: x

        # Initialize unigram corpus
        self.uni_corpus = Corpus([ ' '.join( map(lambda msg: cleaner(msg.text), tpc) ).lower().split() for tpc in window ])

        # If necessary, create n_gram_corpus
        if self.n_grams > 1:
            _process = lambda msg: self.get_ngrams( cleaner( msg.text.lower() ), self.n_grams)
            self.n_gram_corpus = Corpus([ reduce(lambda x,y: x+y, map(_process, tpc) ) for tpc in window ])
        else:
            self.n_gram_corpus = None

        # Initialize model from unigram corpus
        self.model = TfidfModel(corpus=self.uni_corpus)

    def get_score(self, document_id):
        """Generates the TF-IDF score table for each of the terms in the document

        Parameters
        ----------
        document_id : int
            Index of topic to obtain the TF-IDF score

        Returns
        -------
        list[tuples(str, float)]
            DataFrame containing a table with the termID, term and score of each of the terms in the document
        """
        if self.n_grams == 1:
            document = self.uni_corpus[document_id]
            # tid = map(lambda x: x[0], document)
            terms = map( lambda x: self.uni_corpus.dictionary.get(x[0]), document )
            scores = map( lambda x: x[1], self.model[document] )
            return zip(terms, scores)
            # return pd.DataFrame({ 'term': trm, 'score': scr })
        else:
            document = self.n_gram_corpus[document_id]
            # tid = map(lambda x: x[0], document)
            terms = map( lambda x: self.n_gram_corpus.dictionary.get(x[0]), document )

            words_in_tokens =[ self.n_gram_corpus.dictionary[token[0]].split() for token in document ]
            indices_in_tokens = [ self.uni_corpus.dictionary.doc2bow(ws) for ws in words_in_tokens ]
            scores_in_tokens = [ self.model[inds] for inds in indices_in_tokens ]
            scores = [ max([x[1] for x in scs ]) for scs in scores_in_tokens ]

            return zip(terms, scores)
            # return pd.DataFrame({ 'term': trm, 'score': scr })

    def get_top_terms(self, document_id, top=10):
        """Obtain the top terms from a document

        Parameters
        ----------
        document_id : int
            Index of topic to obtain the TF-IDF score
        top : int, optional
            Number of top terms to obtain (defaults to 10)

        Returns
        -------
        list[tuples(str, float)]
            List with the (term, score) tuples
        """
        scores = sorted(self.get_score(document_id), key=lambda x: x[1], reverse=True)
        return scores[:top]

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

    @staticmethod
    def get_ngrams(text, n_grams=1):
        """Returns the n-gram tokens of the specified text

        Parameters
        ----------
        text : str
            Text to tokenize
        n_grams : int, optional
            Number of words to be grouped together and considered a unit token for the corpus (defaults to 1)

        Returns
        -------
        list[str]
            List of n-gram tokens
        """
        word_list =  text.split()
        ngram_list = map(lambda x: ' '.join(x), zip(*[word_list[i:] for i in xrange(n_grams)]))
        return ngram_list
