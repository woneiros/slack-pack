# -*- coding: utf-8 -*-

"""Slack message implementation for Slack-Pack Topic Summarizer

.. module:: nlp.text.mesage
   :platform: Unix, Windows
   :synopsis: Message object

"""


import numpy as np
import pendulum as pm


class Message(object):
    """Slack message object

    Attributes
    ----------
    id : str
        Message ID
    text : str
        Message text
    author : str
        ID of the message's author
    timestamp : Optional[timestamp]
        Timestamp of the message
        .. note::
            In fact it is a `Pendulum <https://pendulum.eustace.io/>`_ object, (which is an extension of datetime.datetime)
    vector_text : tuple(float)
        Message's word embedding representation

    """

    def __init__(self, id, text, author, timestamp=None):
        self.id = id
        self.text = text
        self.vectorText = None
        self.author = author
        self.timestamp = pm.from_timestamp(timestamp) if timestamp else None

