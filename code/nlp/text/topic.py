# -*- coding: utf-8 -*-

"""Slack topic implementation for Slack-Pack Topic Summarizer

.. module:: nlp.text.topic
   :platform: Unix, Windows
   :synopsis: Topic object

"""

class Topic:
    """Slack conversation topic: subset of highly-related messages

    Parameters
    ----------
    startMessage : :class:`nlp.text.message.Message`
        First message of the topic
    reason : str
        Rationale why the message was added to the topic

    """

    def __init__(self, startMessage, reason):
        self.startMessage = startMessage
        self.messages = [startMessage, ]
        self.reasons = [reason, ]

    def appendMessage(self, message, reason):
        """Add a message into the topic

        Parameters
        ----------
        message : :class:`nlp.text.message.Message`
            Message to be appended
        reason : str
            Reason as to why this message is being appended

        """
        self.messages.append(message)
        self.reasons.append(reason)

    def getStartMessage(self):
        return self.startMessage

    @property
    def size(self):
        """Topic message-length

        Returns
        -------
        int
            Amount of messages in the topic
        """
        return len(self.messages)

    def absorb(self, other_topic):
        """Absorb another topic

        Parameters
        ----------
        other_topic : :class:`nlp.text.topic.Topic`
            Topic to be absorbed

        """
        self.messages = self.messages + other.messages
        self.messages.sort(key=lambda msg: msg.id)
        self.reasons.extend( other.reasons )  # append reasons from other topic

