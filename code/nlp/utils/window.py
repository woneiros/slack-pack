# -*- coding: utf-8 -*-

"""Window of observation (amount of topics being observed)

.. module:: nlp.utils.window
   :platform: Unix, Windows
   :synopsis: Window object

"""


from collections import deque

class Window:
    """Window of observation for topics (amount of topics maintained)

    Parameters
    ----------
    window_size : int
        Maximum amount of topics in the window

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

    def addTopic(self, topic):
        """Incorporate a new topic into the window

        Note
        ----
        The topics will be re-ordered, the topic which was added the latest will be the last one

        Warning
        -------
        If the topic is at maximum capacity the first topic will be dropped

        Parameters
        ----------
        topic : :class:`nlp.text.topic.Topic`
            Topic to be added to the observed window

        """
        if topic in self.topics:
            # Pop the actual topic
            current_topic = self.topics.pop( self.topics.index(topic) )
            # Append to the last position
            self.topics.append( current_topic )

        else:
            # If full drop the oldest topic first
            if self.is_full:
                _ = self.topics.pop(0)

            self.topics.append(topic)

