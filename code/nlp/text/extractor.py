"""Message extraction and parsing module

.. module:: nlp.text.extractor
   :platform: Unix, Windows
   :synopsis: Message extraction and parsing

"""

from six import with_metaclass  # for python compatibility
import sys
from abc import ABCMeta, abstractmethod
import pendulum as pm

import json
from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

from message import Message



class Extractor(with_metaclass(ABCMeta, object)):
    """ Abstract class for a message parser

    Note
    ----
    This is an *abstract class* and therefore it cannot be instantiated

    """

    @abstractmethod
    def get_messages(self, *args, **kwargs):
        pass


class JSONExtractor(Extractor):
    """Parser of the raw JSON Slack generated history files

    Parameters
    ----------
    file_name : str or IOBuffer
        Path to the JSON object with the messages

    Attributes
    ----------
    ANON_TEXT : str
        JSON tag of the anonymized text of the message
    TIMESTAMP : str
        JSON tag of the timestamp of the message
    USER : str
        JSON tag of the author of the message

    """
    USER = u'user'
    TEXT = u'text'
    TIMESTAMP = u'ts'

    def __init__(self, file_name):
        self.file_name = file_name
        self.jsonObject = self.parse()

    def parse(self):
        with open(self.file_name) as data_file:
            return json.load(data_file)

    def get_messages(self):
        """Gets the stream of messages

        Returns
        -------
        iterator(|message|)
            Stream of messages
        """
        for message in self.jsonObject:
            id_ = message[self.TIMESTAMP]
            user = message[self.USER]
            text = message[self.TEXT]
            timestamp = float(message[self.TIMESTAMP])

            yield Message(id_, text, user, timestamp)



class CassandraExtractor(Extractor):
    """ Queries `Cassandra database <http://cassandra.apache.org/>`_ and produces a generator of the extracted messages

    Warning
    -------
    This class has not been yet implemented

    """
    # TODO: implement all queries... check how to get filter working
    QUERIES = { 'hour': 'SELECT ts, message_text, user FROM {t}',
                'day': 'SELECT ts, message_text, user FROM {t}',
                'week': 'SELECT ts, message_text, user FROM {t}',
              }


    def __init__(self, cluster_ips, session_keyspace, table_name):
        self.cluster = Cluster(cluster_ips)
        self.session = self.cluster.connect(session_keyspace)
        self.table_name = table_name

    def add_query(label, query):
        """Adds a custom query to the QUERIES dictionary

        Parameters
        ----------
        label : str
            label of the CQL query to be called upon
        query : str
            CQL query to be executed

        """
        self.QUERIES[label] = query


    def get_messages(self, type_of_query, channel, table=None):
        """Gets the stream of messages

        Parameters
        ----------
        type_of_query : str
            Label of the query type unless custom queries are added: 'hour', 'day', 'week'
        channel : str
            channel to be queried
        table : str
            override table_name specified on instantiation

        Returns
        -------
        iterator(|message|)
            Stream of messages

        Raises
        ------
        KeyError
            If the query type was not found
        """
        qtable = table if table is not None else self.table_name

        try:
            query = self.QUERIES[type_of_query].format(t=qtable)
        except KeyError:
            error_msg = 'The specific type_of_query ({}) was not found. Queries can be added with `add_query`'
            raise KeyError(error_msg.format(type_of_query))

        rows = self.session.execute(query)

        for r in rows:
            # TODO: if other todo does not work, implement filter here
            yield( Message(id=r.ts, text=r.message_text, author=r.user, timestamp=float(r.ts)) )


