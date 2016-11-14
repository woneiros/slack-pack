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
    distance : callable
        Callable that returns a float when called over two representations
    tokenizer : callable, optional
        Message tokenizer

    Raises
    ------
    AttributeError
        If representation or distance are not callable objects. Will also raise if tokenizer is not None nor callable.
    """

    def __init__(self, representation, distance, tokenizer=None):
        if not hasattr(representation, '__call__'):
            raise AttributeError('representation needs to be a callable object')
        self.representation = representation

        if not hasattr(distance, '__call__'):
            raise AttributeError('distance needs to be a callable object')
        self.distance = distance

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
            self.calculate_centroid(topic)

            # get distance to centroid
            similarities.append( self.distance(centroid, messages.text_repr) )  # NOTE: distance to similarity!

        return similarities

        #     for topic_message in topic.messages:
        #         (centroidDistance, cosine) = self.model.calculateSimilarity(
        #             message, topic_message, message.getID() - topic_message.getID())
        #         similarities.append(TopicSimilarity(topic, cosine, centroidDistance))
        # similarities.sort(key=lambda x: x.getCentroidDistance())
        # # get top 5 percent
        # size = int(math.ceil(len(similarities) * 5. / 100))
        # similarities = similarities[0:size]
        # similarities.sort(key= lambda x: -x.getScore())
        # return None if len(similarities) == 0 else similarities[0]

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



class Model:
    def __init__(self, messages, tokenizer):
        self.tokenizer = tokenizer
        self.innerModel = self.trainNewModel(messages)
        self.index2wordSet = set(self.innerModel.index2word)

    def trainNewModel(self, messages):
        return gensim.models.Word2Vec(
            [self.tokenizer.stemAndTokenize(message) for message in messages],
            min_count = 1)

    def __getitem__(self, index):
        return self.innerModel[index]

    def calculateSimilarity(self, messageA, messageB, indexDistance):
        fullTokensA = self.tokenizer.stemAndTokenize(messageA)
        fullTokensB = self.tokenizer.stemAndTokenize(messageB)

        width = 10
        startA = 0
        best = (float('inf'), 0) # orthogonal
        decay = (0.993 ** indexDistance) # must be related to the cosine threshold
        while startA < len(fullTokensA):
            startB = 0
            tokensA = fullTokensA[startA:(startA + width)]
            while startB < len(fullTokensB):
                tokensB = fullTokensB[startB:(startB + width)]
                cosine = self.innerModel.n_similarity(tokensA, tokensB) * decay
                centroid = self.centroidDistance(tokensA, tokensB) / decay
                pair = (centroid, cosine)
                if best is None or best > pair:
                    best = pair
                startB = startB + width / 2
            startA = startA + width / 2
        return best

    def centroidDistance(self, tokensA, tokensB):
        centroidA = sum([self[t] for t in tokensA]) / len(tokensA)
        centroidB = sum([self[t] for t in tokensB]) / len(tokensB)
        return np.linalg.norm(self.centroid(tokensA) - self.centroid(tokensB))

    def centroid(self, tokens):
        return sum([self[t] for t in tokens]) / len(tokens)



