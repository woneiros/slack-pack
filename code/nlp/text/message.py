# -*- coding: utf-8 -*-

"""Slack message implementation for Slack-Pack Topic Summarizer

.. module:: nlp.text.message
   :platform: Unix, Windows
   :synopsis: Message object

"""


import numpy as np
import pendulum as pm
import warnings


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
    url : str
        Message's URL for creating go-to links
    timestamp : Optional[timestamp]
        Timestamp of the message
        .. note::
            In fact it is a `Pendulum <https://pendulum.eustace.io/>`_ object, (which is an extension of datetime.datetime)
    text_repr : tuple(float)
        Message's word embedding representation

    """

    def __init__(self, id, text, author, url=None, timestamp=None):
        self.id = id
        self.text = text
        self.text_repr = None
        self.repr_id = None
        self.author = author
        self.url = url
        self.timestamp = pm.from_timestamp(timestamp) if timestamp else None

    @property
    def is_processed(self):
        return self.text_repr is not None

    def process(self, processor, verbose=False):
        """Processes the message text

        Parameters
        ----------
        processor : callable
            Message processor to create the text representation
        verbose : bool, optional
            Warn if processing is unnecessary

        """
        try:
            processor_id = processor.__id
        except AttributeError:
            # In case the processor_id is not specified defaults to the `now()` timestamp
            processor_id = pm.now()

        if processor_id == self.repr_id:
            if verbose:
                warnings.warn('Message will not be reprocessed')
        else:
            # process and save representation
            self.text_repr = processor(self.text)
            self.repr_id = processor_id

