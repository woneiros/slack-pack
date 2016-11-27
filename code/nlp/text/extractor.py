"""Message extraction and parsing module

.. module:: nlp.text.extractor
   :platform: Unix, Windows
   :synopsis: Message extraction and parsing

"""

import logging

from six import with_metaclass  # for python compatibility
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

    def __init__(self, file_name, logger=None):
        self.file_name = file_name
        self.jsonObject = self.parse()
        self.logger = False
        if logger is not None:
            self.set_logger(logger)
            self.logger = True

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
            try:
                id_ = message[self.TIMESTAMP]
                user = message[self.USER]
                text = message[self.TEXT]
                timestamp = float(message[self.TIMESTAMP])
            except:
                if self.logger:
                    logging.error("Failed to parse message", exc_info=True)
                continue

            yield Message(id_, text, user, timestamp)

    def set_logger(self, logfile):
        # Logging
        self.logger = logging.getLogger('extractor')
        self.logger.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # create console handler, set level of logging and add formatter
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)

        # create file handler, set level of logging and add formatter
        fh = logging.handlers.TimedRotatingFileHandler(logfile, when='M', interval=1)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        fh.suffix = '%Y-%m-%d_%H-%M-%S.log'

        # add handlers to logger
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)



class CassandraExtractor(Extractor):
    """ Queries `Cassandra database <http://cassandra.apache.org/>`_ and produces a generator of the extracted messages

    Parameters
    ----------
    cluster_ips : list[str]
        IPs to the Cassandra cluster
    session_keyspace : str
        Keyspace on which to connect in the Cassandra cluster
    table_name : str
        Name of the main table to be queried

    Attributes
    ----------
    QUERIES : dict
        dictionary with the allowed template queries depending on the intended extraction

    """
    # TODO: implement all queries... check how to get filter working
    QUERIES = { 'hour': 'SELECT * FROM {t}',
                'day': 'SELECT * FROM {t}',
                'week': 'SELECT * FROM {t}',
              }


    def __init__(self, cluster_ips, session_keyspace, table_name):
        self.cluster = Cluster(cluster_ips)
        self.session = self.cluster.connect(session_keyspace)
        self.table_name = table_name

    def add_query(self, label, query):
        """Adds a custom query to the QUERIES dictionary

        Parameters
        ----------
        label : str
            label of the CQL query to be called upon
        query : str
            CQL query to be executed

        """
        self.QUERIES[label] = query


    def get_messages(self, type_of_query, channel, table=None, min_words=5):
        """Gets the stream of messages

        Parameters
        ----------
        type_of_query : str
            Label of the query type unless custom queries are added: 'hour', 'day', 'week'
        channel : str
            channel to be queried
        table : str
            override table_name specified on instantiation
        min_words : int, optional
            Minimum amount of words in the message to be streamed (defaults to 5)

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
            if r.channel == channel:
                if len(r.message_text.split()) < min_words:
                    continue

                # Only stream messages with more than one word
                try:
                    timestamp = float(r.ts)
                except ValueError:
                    _datetime = pm.from_format(r.ts[:19], fmt='%Y-%m-%dT%H:%M:%S')
                    timestamp = float(_datetime.timestamp) + float(r.ts.split('+')[0].split('.')[-1])
                finally:
                    yield( Message(id=r.ts, text=r.message_text, author=r.user, timestamp=timestamp) )


