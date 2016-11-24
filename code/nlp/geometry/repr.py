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

"""

from six import with_metaclass  # for python compatibility
from abc import ABCMeta, abstractmethod

from gensim.models.word2vec import Word2Vec
import numpy as np

from os.path import abspath
from glob import glob


# Obtain the absolute path to the corpora folder
__path = abspath('.')
__pos = __path.index('slack-pack')
PATH_TO_COPORA = __path[:__pos + 10] + '/data/corpora/'  # len('slack-pack') --> 10
PATH_TO_MODELS = __path[:__pos + 10] + '/data/models/'  # len('slack-pack') --> 10


def list_corpora():
    """Lists the corpora available

    Returns
    -------
    list[str]
        List of corpora available
    """
    non_zips = filter( lambda x: not (x.endswith('.zip') or x.endswith('.gz')), glob(PATH_TO_COPORA) )
    return map(lambda x: x.split('/')[-1], non_zips)


def list_models():
    """Lists the corpora available

    Returns
    -------
    list[str]
        List of models available
    """
    return glob( PATH_TO_MODELS )


class Representation(with_metaclass(ABCMeta, object)):
    """ Abstract class for a geometric representation of words

    Note
    ----
    This is an *abstract class* and therefore it cannot be instantiated

    """
    self.PATH_TO_COPORA = PATH_TO_COPORA
    self.PATH_TO_MODELS = PATH_TO_MODELS

    @abstractmethod
    def __load_model(self, fname):
        pass

    @abstractmethod
    def __getitem__(self, item):
        pass

    @abstractmethod
    def __str__(self):
        pass


class Word2Vec(Representation):
    """Trained object of `word2vec<https://code.google.com/archive/p/word2vec/>`_ as implemented by `gensim<https://radimrehurek.com/gensim/models/word2vec.html>`_
    """

    def __init__(self, fname):
        self.model = None
        self.__load_model(fname)


    def __load_model(self, fname):
        """Loads a given GloVe model

        Parameters
        ----------
        fname : str
            path to the gloVe model to load

        Returns
        -------
        dict
            dictionary containing the representations of the words
        """
        # Load the model
        return Word2Vec.load('models/word2vec_text8')


    def __getitem__(self, item):
        try:
            representation = self.model[item]
        except KeyError:
            representation = np.zeros_like(self.model[model_new.vocab.keys()[0]])
        finally:
            return representation

    def __str__(self):
        return 'word2vec'



class GloVe(Representation):
    """Trained object of `GloVe<http://nlp.stanford.edu/projects/glove/>`_ using the `stanfordnlp-trained datasets<http://nlp.stanford.edu/data/wordvecs/>`_

    Parameters
    ----------
    file_name : str or IOBuffer
        Path to the JSON object with the messages

    Attributes
    ----------
    vocab : dict
        dictionary with all the glove-trained representations of each term
    """
    def __init__(self, fname):
        self.vocab = self.__load_model(fname)


    def __load_model(self, fname):
        """Loads a given GloVe model

        Parameters
        ----------
        fname : str
            path to the gloVe model to load

        Returns
        -------
        dict
            dictionary containing the representations of the words
        """
        with open(fname, 'rb') as f:
            lines = f.readlines()

        repr_dict = {}  # Initialize dictionary

        for line in lines:
            _line = line.split()
            repr_dict[_line[0]] = np.array(map(float, _line[1:]))

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

    def __str__(self):
        return 'gloVe'


# NOTE: Experiment with LDA
