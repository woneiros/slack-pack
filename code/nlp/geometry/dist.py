# -*- coding: utf-8 -*-

"""Implementation of different distances to use for a geometry

.. module:: nlp.geometry.dist
   :platform: Unix, Windows
   :synopsis: Distances between message representations

.. |message| replace:: :class:`nlp.text.message.Message`
.. |tokenizer| replace:: :class:`nlp.text.grammar.tokenizer`
.. |sentgram| replace:: :class:`nlp.text.grammar.grammar_analyzer`

"""


class CosineDistance(object):
    """Cosine distance between two words


    Parameters
    ----------
    representation : TYPE
        Description

    """

    def __init__(self, representation):
        """Summary

        """
        self.arg = arg
