# -*- coding: utf-8 -*-

"""Window of observation (amount of topics being observed)

.. module:: nlp.text.window
   :platform: Unix, Windows
   :synopsis: Window object

.. |message| replace:: :class:`nlp.text.message.Message`
.. |topic| replace:: :class:`nlp.text.topic.Topic`
.. |tfidf| replace:: :class:`nlp.models.summarization.TFIDF`

"""

from topic import Topic


def from_topic_list(topic_list):
    """Generates a Window from a list of "topics", in which each "topic" is a list of tuples of (message, reason))

    Parameters
    ----------
    topic_list : list(tuples(|message|, str))
        List of lists of tuples of (message, reason)

    Returns
    -------
    TYPE
        :class:`nlp.text.window.Window`
    """
    _window = Window()
    for topic in topic_list[::-1]:
        # Append topics from oldest to most recent
        uninit = True

        for m,r in topic:
            if uninit:
                # generate new topic and append to window
                _window.activate_topic( Topic(start_message=m, reason=r) )
                uninit = False  # no longer uninit
            else:
                _window.insert_message(message=m, reason=r)

    return _window



class Window:
    """Window of observation for topics (amount of topics maintained)

    Parameters
    ----------
    window_size : int, optional
        Maximum amount of |topic|s in the window. If left unspecified the window will not have a maximum

    Attributes
    ----------
    topics : list[|topic|]
        List of topics. Ordered from most recent to oldest

    """

    def __init__(self, window_size=None):
        self.topics = []
        self.window_size = window_size if window_size is not None else float('inf')
        self.last_timestamp = None

    @property
    def is_full(self):
        """Property, is the window at maximum capacity

        Returns
        -------
        bool
            Returns `True` if full

        """
        return self.window_size <= len(self.topics)

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

    def __getitem__(self, item):
        return self.topics[item]

    def __len__(self):
        """Length of the window (number of topics)

        Returns
        -------
        int
            Number of topics
        """
        return len(self.topics)

    def __iter__(self):
        """Iterates over the topics

        Yields
        -------
        |topic|
            Next topic to be iterated over
        """
        for topic in self.topics:
            yield topic

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
            # Append to the first position
            self.topics.insert(0, current_topic )

        else:
            # If full drop the oldest topic first
            if self.is_full:
                _ = self.topics.pop(-1)

            self.topics.insert(0, topic)

        self.last_timestamp = self.topics[0].last_timestamp

    def generate_topic_list(self, cleaner=None):
        """Generates a list with a list for each topic with all words contained in that topic (for |tfidf| model)

        Parameters
        ----------
        cleaner : callable, optional
            Function that gets a str and returns a str back (meant for cleaning and removing stopwords)

        Returns
        -------
        list[list[str]]
            List of list of words (all words in a single topic)
        """
        cleaner = cleaner if cleaner is None else lambda x: x
        return [ ' '.join( map(lambda msg: cleaner(msg.text), tpc) ).lower().split() for tpc in self.topics ]


    def insert_message(self, message, reason, topic_index=0, force_inactive=False):
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

        # Unless specified not to, activate the topic we just appended to
        if not force_inactive:
            self.activate_topic( self.topics[topic_index] )

    def report_topics(self):
        """Prints out a report of the amount of topics and the size (in messages) of each topic
        """
        print( 'Window has #{} topics\n'.format( len(self.topics) ) )
        print( 'Topic length report:' )
        for i, topic in enumerate(self.topics):
            print( '  Topic #{:>2}  --> size: {:<3}'.format(i, len(topic)) )

