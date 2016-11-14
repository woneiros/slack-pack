# -*- coding: utf-8 -*-

"""Model to identify reply messages

.. module:: nlp.models.reply_predictor
   :platform: Unix, Windows
   :synopsis: Model for identification of reply messages

.. |message| replace:: :class:`nlp.text.message.Message`
.. |topic| replace:: :class:`nlp.text.topic.Topic`
.. |window| replace:: :class:`nlp.text.window.Window`
.. |tokenizer| replace:: :class:`nlp.text.grammar.tokenizer`
.. |sentgram| replace:: :class:`nlp.text.grammar.grammar_analyzer`
.. |simcalc| replace:: :class:`nlp.text.models.similarity_calculation`

"""

import nltk


# For our internal toolbox imports
import os, sys
path_to_here = os.path.abspath('.')
sys.path.append(path_to_here[:path_to_here.index('code')+4])

from nlp.grammar.grammar_analyzer import SentenceGrammarAnalyzer
from nlp.text.topic import Topic


class MessageClassifier(object):
    """A message classification engine/model

    Attributes
    ----------
    gram_analyzer : |sentgram|
        Grammar analyzer for identifying if a message is a reply (not to be specified)
    sim_calc : |simcalc|
        For message-topic similarity calculation
    sim_threshold : float
        Threshold between 0 and 1
    window : |window|
        Window with |topic|s

    """
    def __init__(self, window, similarity_threshold, similar_topic_calculator):
        self.window = window
        self.sim_threshold = similarity_threshold
        self.sim_calc = similar_topic_calculator

        # Initialize a grammar analyzer to check if the message is a reply
        self.gram_analyzer = SentenceGrammarAnalyzer(message, self.tokenizer)

    def classify(self, message, processor=None):
        """Predict the topic to be appended to along with the reason for the given message

        Parameters
        ----------
        message : |message|
            Message to be classified
        processor : callable, optional
            Message processor that returns the text's representation

        Returns
        -------
        tuple(|topic|, str)
            (Topic to be appended to, reason for appending)
        """
        # Process message - if no processor was given, obtain the processor
        if processor is None:
            processor = self.sim_calc.get_processor()
        message.process(processor)  # processed text is stored in the message

        # If the window is empty --> start first topic
        if self.window.topics.is_empty:
            # Create new topic and append to window
            self.window.activate_topic( Topic(message, 'window empty') )

        # Check if the message is a reply
        (is_reply, reason) = analyzer.is_reply()
        if is_reply:  # we already know topics is not empty
            self.window.insert_message(message, 'grammatically ' + reason)  # will insert to the latest active channel

        # If not a reply --> check most similar topic (using similarity calculator)
        similarities = self.sim_calc.get_similarities(self.window, message)
        which_max, sim_max = max( enumerate(similarities), key=lambda x: x[1] )

        if sim_max >= self.sim_threshold:  # if found similarity
            self.window.activate_topic( self.window.topics[which_max] )
            self.window.insert_message(message, 'distance {d:.3f} <= threshold({th})'.format(d=similarity.score, th=self.sim_threshold))

        elif self.window.len_active == 1:  # else, if previous topic small, append to latest
            self.window.insert_message(message, 'previous topic with one element')

        else:  # start a new topic with the new message
            self.window.activate_topic( Topic(message, 'no similarity nor grammatically a reply') )


    def classify_stream(self, message_stream):
        """Classifies an entire stream of messages (pre-obtains the processor and calls .classify(msg) on each message)

        Parameters
        ----------
        message_stream : TYPE
            Description

        Returns
        -------
        TYPE
            Description
        """
        # Pre-obtain processor and pass the same to every message for efficiency
        proc = self.sim_calc.get_processor()

        # Process each of the messages in the stream
        for message in messages:
            yield self.classify(message, processor=proc)

