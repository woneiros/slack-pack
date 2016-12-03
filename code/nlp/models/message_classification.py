# -*- coding: utf-8 -*-

"""Model to identify reply messages

.. module:: nlp.models.reply_predictor
   :platform: Unix, Windows
   :synopsis: Model for identification of reply messages

.. |message| replace:: :class:`nlp.text.message.Message`
.. |topic| replace:: :class:`nlp.text.topic.Topic`
.. |window| replace:: :class:`nlp.text.window.Window`
.. |tokenizer| replace:: :module:`nlp.text.grammar.tokenizer`
.. |sentgram| replace:: :module:`nlp.text.grammar.grammar_analyzer`
.. |simcalc| replace:: :module:`nlp.text.models.similarity_calculation`
.. |messim| replace:: :class:`nlp.text.models.similarity_calculation`

"""

import nltk
import pendulum as pm

# For our internal toolbox imports
import os, sys
path_to_here = os.path.abspath('.')
sys.path.append(path_to_here[:path_to_here.index('code')+4])

from nlp.grammar.grammar_analyzer import SentenceGrammarAnalyzer
from nlp.text.topic import Topic
from nlp.text.window import Window
from nlp.models.similarity_calculation import MessageSimilarity


class SimpleClassifier(object):
    """A simple message classification engine/model

    Attributes
    ----------
    gram_analyzer : |sentgram|
        Grammar analyzer for identifying if a message is a reply (not to be specified)
    message_similarity : |simcalc|
        Message-to-message similarity calculator (defaults to || )
    sim_threshold : float
        Threshold between 0 and 1
    window : |window|
        Window with |topic|s

    """
    def __init__(self, window=None, message_similarity=None):
        self.window = window if window is not None else Window()
        self.message_similarity = message_similarity if message_similarity is not None else MessageSimilarity()

        # Check message_similarity is callable
        if not hasattr(self.message_similarity, '__call__'):
            raise IOError('The message_similarity needs to be a callable object')


    def classify_stream(self, message_stream, max_messages=20, max_active_topics=5,
                        low_threshold=.4, high_threshold=.7, low_step=.05, high_step=.02, verbose=True):
        """Classifies an entire stream of messages by predicting the topic to be appended to

        Parameters
        ----------
        message_stream : iterable of |message|s
            Iterator or list of messages
        distance : callable, optional
            Distance measure between two texts
        max_messages : int, optional
            Maximum amount of messages to classify (for debugging and illustration purposes)
        max_active_topics : int, optional
            Maximum amount of (most-recent) topics a message can be compared to for similarity
        low_threshold : float, optional
            Description
        high_threshold : float, optional
            Description
        low_step : float, optional
            Description
        high_step : float, optional
            Description
        verbose : bool, optional
            Print the classification stream (defaults to True - while construction)

        Returns
        -------
        |window|
            Window with the classified topics
        """
        for m, msg in enumerate(message_stream):
            if m > max_messages:
                m -= 1
                break

            if verbose:
                print '#{:>3}\033[33m ==> {}\033[0m'.format(m, msg.text.encode('ascii', 'ignore'))

            if self.window.is_empty:
                self.window.activate_topic( Topic(msg, 'First message') )
                # topics.insert(0, [(msg, 'First message')] )
                if verbose:
                    print '\t First message (new 0)\n'

            else:
                # We will sequentially try to append to each topic ...
                #    as time goes by it is harder to append to a topic

                low_th = low_threshold
                high_th = high_threshold
                topic_scores = []  # in case no topic is close

                for t in xrange( min(len(self.window), max_topic_length) ):
                    tp_len = len(self.window[t])
                    distances = map(lambda x: self.message_similarity(msg.text, x.text), topics[t])

                    # Assign a non-linear score (very close messages score higher)
                    score = sum([ 0 if d < low_th else 1 if d < high_th else 3 for d in distances ])

                    # Very small topics (< 3) should be easy to append to,
                    #   since the odds of a message being of this topic whould be quite high
                    if (tp_len < 3):
                        if (score > 0):
                            reason = 'len({}) < 3 and distances({})'.format(tp_len, distances)
                            # Append to the specific topic (this topic will now become the most active topic --> first topic in the window)
                            self.window.insert_message(message=msg, reason=reason, topic_index=t)
                            # _topic = topics.pop(t)  # pop from topic queue
                            # _topic.append( (msg, reason) )
                            # topics.insert(0, _topic)  # append to first topic
                            if verbose:
                                print '\t inserted to #{} : {}\n'.format(t, reason)
                            break

                    # Medium-sized topics (3 ~ 10) should have a varying score goal depending on their length,
                    #   as the topic gets bigger the score should increase (and the speed of increase should also grow)
                    elif (tp_len < 10):
                        if (score > (tp_len - (2 - tp_len/15.) )):
                            reason = 'len({}) < 10 and distances({})'.format(tp_len, distances)
                            # Append to the specific topic (this topic will now become the most active topic --> first topic in the window)
                            self.window.insert_message(message=msg, reason=reason, topic_index=t)
                            # _topic = topics.pop(t)  # pop from topic queue
                            # _topic.append( (msg, 'len({}) < 10 and distances({})'.format(tp_len, distances)) )
                            # topics.insert(0, _topic)  # append to first topic
                            if verbose:
                                print '\t inserted to #{} : {}\n'.format(t, reason)
                            break

                    # Very large topics (> 10) should be harder to append to,
                    #   since the odds of a casual match are higher
                    else:
                        if (score > tp_len*1.5):
                            reason = 'len({}) > 10 and distances({})'.format(tp_len, distances)
                            # Append to the specific topic (this topic will now become the most active topic --> first topic in the window)
                            self.window.insert_message(message=msg, reason=reason, topic_index=t)
                            # _topic = topics.pop(t)  # pop from topic queue
                            # _topic.append( (msg, 'len({}) > 10 and distances({})'.format(tp_len, distances)) )
                            # topics.insert(0, _topic)  # append to first topic
                            if verbose:
                                print '\t inserted to #{} : {}\n'.format(t, reason)
                            break

                    topic_scores.append( (tp_len,score) )  # append score to topic_scores

                    # else try with next topic --> harder
                    low_th += low_step if low_th+low_step < high_th else high_step
                    high_th += high_step
                else:
                    # If no topic was suitable --> Start new topic
                    self.window.activate_topic( Topic(msg, 'No similar topics (to 0) scores:({})'.format(topic_scores)) )
                    # topics.insert(0, [(msg, 'No similar topics (to 0) scores:({})'.format(topic_scores))] )
                    if verbose:
                        print '\t No similar topics (new 0) scores:({})\n'.format(topic_scores)

        print '... Done, processed {} messages'.format(m)
        return self.window


    def classify_stream_time(self, message_stream, max_messages=20, max_active_topics=5, autom_message_seconds=10,
                             low_threshold=.4, high_threshold=.7, low_step=.05, high_step=.02, verbose=True):
        """Classifies an entire stream of messages by predicting the topic to be appended to

        Parameters
        ----------
        message_stream : iterable of |message|s
            Iterator or list of messages
        distance : callable, optional
            Distance measure between two texts
        max_messages : int, optional
            Maximum amount of messages to classify (for debugging and illustration purposes)
        max_active_topics : int, optional
            Maximum amount of (most-recent) topics a message can be compared to for similarity
        autom_message_seconds : int, optional
            If the message was produced within less than the amount specified, it will be appended to the same topic as the last message
        low_threshold : float, optional
            Description
        high_threshold : float, optional
            Description
        low_step : float, optional
            Description
        high_step : float, optional
            Description
        verbose : bool, optional
            Print the classification stream (defaults to True - while construction)

        Returns
        -------
        list(tuples(|message|, str))
            Window (as list of topics)
        """
        for m, msg in enumerate(message_stream):
            if m > max_messages:
                m -= 1
                break

            last_timestamp = None

            if verbose:
                print '#{:>3}\033[33m ==> {}\033[0m'.format(m, msg.text.encode('ascii', 'ignore'))

            if self.window.is_empty:
                # initialize last_datetime
                # last_dt = pm.fromtimestamp(msg.timestamp) --> no longer necessary (embedded within the window)

                self.window.activate_topic( Topic(msg, 'First message') )
                # topics.insert(0, [(msg, 'First message')] )
                if verbose:
                    print '\t First message (new 0)\n'

            else:
                # We will sequentially try to append to each topic ...
                #    as time goes by it is harder to append to a topic

                # First check if the message was produced within `autom_message_seconds` seconds from the last message
                # diff_period = last_dt.diff(pm.fromtimestamp(msg.timestamp))
                diff_period = pm.fromtimestamp(self.window.last_timestamp).diff(pm.fromtimestamp(msg.timestamp))

                if diff_period.in_seconds() <= autom_message_seconds:
                    # Append to the last topic (no need to pop, since it is topic[0])
                    reason = 'Within {} seconds (diff of: {}s)'.format(autom_message_seconds, diff_period.in_seconds())
                    topics[0].append( (msg, reason) )
                    last_dt = pm.fromtimestamp(msg.timestamp)  # update last_datetime
                    if verbose:
                        print '\t inserted to #{} : {}\n'.format(t, reason)


                low_th = low_threshold
                high_th = high_threshold
                topic_scores = []  # in case no topic is close

                for t in xrange( min(len(self.window), max_topic_length) ):
                # for t in xrange( min(len(topics), max_topic_length) ):
                    tp_len = len(self.window[t])
                    # tp_len = len(topics[t])
                    distances = map(lambda x: self.message_similarity(msg.text, x[0].text), topics[t])

                    # Assign a non-linear score (very close messages score higher)
                    score = sum([ 0 if d < low_th else 1 if d < high_th else 3 for d in distances ])

                    # Very large topics (> 10) should be harder to append to,
                    #   since the odds of a casual match are higher
                    if (tp_len < 3):
                        if (score > 0):
                            reason = 'len({}) < 3 and distances({})'.format(tp_len, distances)
                            self.window.insert_message(message=msg, reason=reason, topic_index=t)
                            # _topic = topics.pop(t)  # pop from topic queue
                            # _topic.append( (msg, reason) )
                            # topics.insert(0, _topic)  # append to first topic
                            # last_dt = pm.fromtimestamp(msg.timestamp)  # update last_datetime
                            if verbose:
                                print '\t inserted to #{} : {}\n'.format(t, reason)
                            break

                    elif (tp_len < 10):
                        if (score > (tp_len - (2 - tp_len/15.) )):
                            reason = 'len({}) < 10 and distances({})'.format(tp_len, distances)
                            self.window.insert_message(message=msg, reason=reason, topic_index=t)
                            # _topic = topics.pop(t)  # pop from topic queue
                            # _topic.append( (msg, 'len({}) < 10 and distances({})'.format(tp_len, distances)) )
                            # topics.insert(0, _topic)  # append to first topic
                            # last_dt = pm.fromtimestamp(msg.timestamp)  # update last_datetime
                            if verbose:
                                print '\t inserted to #{} : {}\n'.format(t, reason)
                            break

                    else:
                        if (score > tp_len*1.5):
                            reason = 'len({}) > 10 and distances({})'.format(tp_len, distances)
                            self.window.insert_message(message=msg, reason=reason, topic_index=t)
                            # _topic = topics.pop(t)  # pop from topic queue
                            # _topic.append( (msg, 'len({}) > 10 and distances({})'.format(tp_len, distances)) )
                            # topics.insert(0, _topic)  # append to first topic
                            # last_dt = pm.fromtimestamp(msg.timestamp)  # update last_datetime
                            if verbose:
                                print '\t inserted to #{} : {}\n'.format(t, reason)
                            break

                    topic_scores.append( (tp_len,score) )  # append score to topic_scores

                    # else try with next topic --> harder
                    low_th += low_step if low_th+low_step < high_th else high_step
                    high_th += high_step
                else:
                    # If no topic was suitable --> Start new topic
                    self.window.activate_topic( Topic(msg, 'No similar topics (to 0) scores:({})'.format(topic_scores)) )
                    # topics.insert(0, [(msg, 'No similar topics (to 0) scores:({})'.format(topic_scores))] )
                    last_dt = pm.fromtimestamp(msg.timestamp)  # update last_datetime
                    if verbose:
                        print '\t No similar topics (new 0) scores:({})\n'.format(topic_scores)

        print '... Done, processed {} messages'.format(m)
        return self.window




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
    def __init__(self, window, similarity_threshold, similar_topic_calculator, reply_analysis=False):
        self.window = window
        self.sim_threshold = similarity_threshold
        self.sim_calc = similar_topic_calculator

        # Initialize a grammar analyzer to check if the message is a reply
        if reply_analysis:
            self.gram_analyzer = SentenceGrammarAnalyzer(self.sim_calc.tokenizer)
        else:
            self.grammar_analyzer = None

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
        if self.window.is_empty:
            # Create new topic and append to window
            self.window.activate_topic( Topic(message, 'window empty') )
            return

        # Check if the message is a reply
        if self.grammar_analyzer is not None:
            (is_reply, reason) = self.gram_analyzer.is_reply(message.text)
            if is_reply:  # we already know topics is not empty
                self.window.insert_message(message, 'grammatically ' + reason)  # will insert to the latest active channel
                return

        # If not a reply --> check most similar topic (using similarity calculator)
        similarities = self.sim_calc.get_similarities(self.window, message)
        which_max, sim_max = max( enumerate(similarities), key=lambda x: x[1] )

        if sim_max >= self.sim_threshold:  # if found similarity
            # self.window.activate_topic( self.window.topics[which_max] )
            self.window.insert_message(message, 'Distance {d:.3f} <= threshold({th})'.format(d=sim_max, th=self.sim_threshold), topic_index=which_max)
            return

        elif self.window.len_active == 1:  # else, if previous topic small, append to latest
            self.window.insert_message( message, 'No similarity ({d:.3f}) and previous topic with one element'.format(d=sim_max) )
            return

        else:  # start a new topic with the new message
            self.window.activate_topic( Topic(message, 'No similarity ({d:.3f}) nor grammatically a reply'.format(d=sim_max)) )
            return


    def classify_stream(self, message_stream):
        """Classifies an entire stream of messages (pre-obtains the processor and calls .classify(msg) on each message)

        Parameters
        ----------
        message_stream : iterable of |message|s
            Iterator or list of messages
        """
        # Pre-obtain processor and pass the same to every message for efficiency
        proc = self.sim_calc.get_processor()

        counter = 0  # initialize message counter

        # Process each of the messages in the stream
        for message in message_stream:
            counter += 1
            self.classify(message, processor=proc)

        print('  ... Finished classifying {} messages'.format(counter))

