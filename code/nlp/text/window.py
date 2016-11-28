# -*- coding: utf-8 -*-

"""Window of observation (amount of topics being observed)

.. module:: nlp.text.window
   :platform: Unix, Windows
   :synopsis: Window object

.. |message| replace:: :class:`nlp.text.message.Message`
.. |topic| replace:: :class:`nlp.text.topic.Topic`

"""


# NOTE: make class iterable with __iter__ and __next__
class Window:
    """Window of observation for topics (amount of topics maintained)

    Parameters
    ----------
    window_size : int
        Maximum amount of |topic|s in the window

    Attributes
    ----------
    topics : list[|topic|]
        List of topics. Ordered from most recent to oldest

    """

    def __init__(self, window_size):
        self.topics = []
        self.windowSize = window_size

    @property
    def is_full(self):
        """Property, is the window at maximum capacity

        Returns
        -------
        bool
            Returns `True` if full

        """
        return self.windowSize <= len(self.topics)

    @property
    def is_empty(self):
        """Property, if the window doesn't have any topics

        Returns
        -------
        bool
            Returns `True` if empty

        """
        return len(self.topics) == 0

    @property
    def len_active(self):
        return len(self.topics[-1])

    def __len__(self):
        """Length of the window (number of topics)

        Returns
        -------
        int
            Number of topics
        """
        return len(self.topics)


    def activate_topic(self, topic):
        """Incorporate a new topic into the window, or set an older topic as most active

        Note
        ----
        The topics will be re-ordered, the topic which was added the latest will be the first one

        Warning
        -------
        If the topic is at maximum capacity the first topic will be dropped

        Parameters
        ----------
        topic : |topic|
            Topic to be added to the observed window
        """
        if topic in self.topics:
            # Pop the actual topic
            current_topic = self.topics.pop( self.topics.index(topic) )
            # Append to the last position
            self.topics.insert(0, current_topic )

        else:
            # If full drop the oldest topic first
            if self.is_full:
                _ = self.topics.pop(-1)

            self.topics.insert(0, topic)

    def insert_message(self, message, reason, topic_index=-1):
        """Inserts the messgae into the specified topic

        Parameters
        ----------
        message : |message|
            Description
        topic_index : int, optional
            Index of the |topic| to which the |message| will be appended.
            If no index is specified it will be added to the latest active |topic|
        reason : str
            Reason why the |message| will be appended to the specific |topic|
        """
        self.topics[topic_index].append_message(message, reason)

