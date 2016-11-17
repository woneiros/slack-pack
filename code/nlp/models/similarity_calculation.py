# -*- coding: utf-8 -*-

"""Analyze the similarity between a message and a topic

.. module:: nlp.model.similarity_calculator
   :platform: Unix, Windows
   :synopsis: Measure message-topic similarity

.. |message| replace:: :class:`nlp.text.message.Message`
.. |topic| replace:: :class:`nlp.text.topic.Topic`
.. |window| replace:: :class:`nlp.text.window.Window`
.. |tokenizer| replace:: :class:`nlp.text.grammar.tokenizer`
.. |nparray| replace:: `Numpy Array <https://docs.scipy.org/doc/numpy/reference/generated/numpy.array.html>`_
"""

import sys
import math
import numpy as np
import gensim


class SimilarTopicCalculator:
    """Processes messages a calculates similarity to a |window| of |topic|s

    Attributes
    ----------
    representation : callable
        Callable that returns a messages representation
    similarity : callable
        Callable that returns a float when called over two representations
    tokenizer : callable, optional
        Message tokenizer

    Raises
    ------
    AttributeError
        If representation or similarity are not callable objects. Will also raise if tokenizer is not None nor callable.
    """

    def __init__(self, representation, similarity, tokenizer=None):
        if not hasattr(representation, '__call__'):
            raise AttributeError('representation needs to be a callable object')
        self.representation = representation

        if not hasattr(similarity, '__call__'):
            raise AttributeError('similarity needs to be a callable object')
        self.similarity = similarity

        if (tokenizer is not None) and not hasattr(tokenizer, '__call__'):
            raise AttributeError('tokenizer needs to be a callable object or None')
        self.tokenizer = tokenizer

    @property
    def has_tokenizer(self):
        """Does the similarity calculator have a tokenizer

        Returns
        -------
        bool
            True if messages will be tokenized
        """
        return tokenizer is not None

    def get_similarities(self, window, message):
        """Calculates the similarity of the |message| with the |topic|s in the |window|

        Parameters
        ----------
        window : |window|
            Window of |topic|s to which the mesage will be added to
        message : |message|
            Message to calculate the similarity

        Returns
        -------
        list[float]
            List of the similarities of the |message| with each of the |topic|s in the |window|
        """
        similarities = []

        for topic in self.window.topics:

            # get centroid of the topic
            centroid = self.calculate_centroid(topic)

            # get similarity with centroid
            similarities.append( self.similarity(centroid, messages.text_repr) )

        return similarities

    def calculate_centroid(self, topic):  # NOTE: might want to implement top 5% later...
        """Calculate the centroid of the topic based on the message representations

        Parameters
        ----------
        topic : |topic|
            Topic to calculate the centroid

        Returns
        -------
        |nparray|
            Geometric centroid of the geometric representations
        """
        proc = self.get_processor()  # obtain processor in case necessary
        pre_centroid = np.zeros_like( topic.start_message.text_repr )

        for message in topic.messages:
            # check if message was processed, process if necessary
            if not topic_message.is_processed:
                topic_message.process( proc )

            # update centroid based on the text_repr
            pre_centroid += message.text_repr

        pre_centroid /= len(topic)

        return pre_centroid

    def get_processor(self):
        """Produces a message processor according to the specified similarity_calculator

        Returns
        -------
        callable
            Message processing function. The processor will have an internal additional attribute `__id` with the processor specifications
        """
        def processor(message):
            """Proccesses the message according to

            Parameters
            ----------
            message : TYPE
                Description

            Returns
            -------
            TYPE
                Description
            """
            if self.has_tokenizer:
                message = self.tokenizer(message)  # the tokenizer is a callable object
            return self.representation(message)  # the representation is also a callable object
            processor.__id = 't:{tok!s}#r:{rep!s}'.format(tok=self.tokenizer, rep=self.representation)
        return processor


class TopicSimilarity:
    def __init__(self, topic, score, centroidDistance):
        self.topic = topic
        self.score = score
        self.centroidDistance = centroidDistance
