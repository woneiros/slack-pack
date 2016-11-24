# -*- coding: utf-8 -*-

"""Implementation of the word2vec word-embedding

Note
----
Needs `gensim <https://radimrehurek.com/gensim/>`_

.. module:: nlp.repr.word2vec
   :platform: Unix, Windows
   :synopsis: Cosine distance between two words

.. |message| replace:: :class:`nlp.text.message.Message`
.. |tokenizer| replace:: :class:`nlp.text.grammar.tokenizer`
.. |sentgram| replace:: :class:`nlp.text.grammar.grammar_analyzer`

# TODO: add documentation with download links to corpora and models
"""
from six import with_metaclass  # for python compatibility
from abc import ABCMeta, abstractmethod

from gensim.models import word2vec as w2v
import numpy as np

from os.path import abspath
from glob import glob


# Obtain the absolute path to the corpora folder
__path = abspath('.')
__pos = __path.index('slack-pack')
PATH_TO_CORPORA = __path[:__pos + 10] + '/code/nlp/data/corpora/'  # len('slack-pack') --> 10
PATH_TO_MODELS = __path[:__pos + 10] + '/code/nlp/data/models/'  # len('slack-pack') --> 10


def list_corpora():
    """Lists the corpora available

    Returns
    -------
    list[str]
        List of corpora available
    """
    non_zips = filter( lambda x: not (x.endswith('.zip') or x.endswith('.gz') or x.endswith('.md')), glob(PATH_TO_CORPORA + '*') )
    return map(lambda x: x.split('/')[-1], non_zips)


def list_models():
    """Lists the corpora available

    Returns
    -------
    list[str]
        List of models available
    """
    non_mds = filter( lambda x: not x.endswith('.md'), glob( PATH_TO_MODELS + '*' ))
    return map(lambda x: x.split('/')[-1], non_mds)


class Representation(with_metaclass(ABCMeta, object)):
    """ Abstract class for a geometric representation of words

    Note
    ----
    This is an *abstract class* and therefore it cannot be instantiated

    """
    PATH_TO_CORPORA = PATH_TO_CORPORA
    PATH_TO_MODELS = PATH_TO_MODELS

    @abstractmethod
    def load_model(self, file_name):
        pass

    @abstractmethod
    def __getitem__(self, item):
        pass

    @abstractmethod
    def __call__(self, item):
        pass

    @abstractmethod
    def __str__(self):
        pass


class Word2Vec(Representation):
    """Trained object of `word2vec<https://code.google.com/archive/p/word2vec/>`_ as implemented by `gensim<https://radimrehurek.com/gensim/models/word2vec.html>`_

    Parameters
    ----------
    file_name : str or IOBuffer
        Path to the saved model from which to load the representation

    Attributes
    ----------
    model : `gensim.models.word2vec.Word2vec<https://radimrehurek.com/gensim/models/word2vec.html#gensim.models.word2vec.Word2Vec>`_
        word2vec model (gensim implementation)
    """

    def __init__(self, file_name):
        self.model = self.load_model(file_name)


    def load_model(self, file_name):
        """Loads a given GloVe model

        Parameters
        ----------
        file_name : str
            path to the gloVe model to load

        Returns
        -------
        dict
            dictionary containing the representations of the words
        """
        # Load the model
        return w2v.Word2Vec.load(self.PATH_TO_MODELS + file_name)


    def __getitem__(self, item):
        try:
            representation = self.model[item]
        except KeyError:
            # Not found terms are represented with a random vector (to minimize probability of chance collision)
            representation = np.random.ranf( self.model.vector_size )
        finally:
            return representation


    # NOTE: research other aggregation methods (other than mean)
    def __call__(self, message_text):
        """Geometric representation of a document

        Parameters
        ----------
        message_text : str
            Message to obtain a representation from

        Returns
        -------
        np.array(float)
            Geometric representation of the message_text
        """
        representation = 0.
        words = message_text.lower().split()
        for w in words:
            representation += self.__getitem__( w.strip() )

        representation /= len(words)

        return representation


    def __str__(self):
        return 'word2vec'



class GloVe(Representation):
    """Trained object of `GloVe<http://nlp.stanford.edu/projects/glove/>`_ using the `stanfordnlp-trained datasets<http://nlp.stanford.edu/data/wordvecs/>`_

    Parameters
    ----------
    file_name : str or IOBuffer
        Path to the lookup-corpus from which to load the representation

    Attributes
    ----------
    vocab : dict
        dictionary with all the glove-trained representations of each term
    """
    def __init__(self, file_name):
        self.vocab = self.load_model(self.PATH_TO_CORPORA + file_name)


    def load_model(self, file_name):
        """Loads a given GloVe model

        Parameters
        ----------
        file_name : str
            path to the gloVe model to load

        Returns
        -------
        dict
            dictionary containing the representations of the words
        """
        repr_dict = {}  # initialize dictionary

        with open(file_name, 'rb') as f:
            for line in iter(f.readline, ''):
                _terms = line.split()
                repr_dict[_terms[0]] = np.array(map(float, _terms[1:]))

        return repr_dict

    def __getitem__(self, item):
        """Geometric representation of the object

        Parameters
        ----------
        item : word
            term to lookup

        Returns
        -------
        np.array(float)
            Geometric representation of the term
        """
        try:
            representation = self.vocab[item]
        except KeyError:
            representation = self.vocab['<unk>']
        finally:
            return representation


    # NOTE: research other aggregation methods (other than mean)
    def __call__(self, message_text):
        """Geometric representation of a document

        Parameters
        ----------
        message_text : str
            Message to obtain a representation from

        Returns
        -------
        np.array(float)
            Geometric representation of the message_text
        """
        representation = 0.
        words = message_text.lower().split()
        for w in words:
            representation += self.__getitem__( w.strip() )

        representation /= len(words)

        return representation


    def __str__(self):
        return 'gloVe'


# NOTE: Experiment with LDA
