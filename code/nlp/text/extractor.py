"""Message extraction and parsing module

.. module:: nlp.text.extractor
   :platform: Unix, Windows
   :synopsis: Message extraction and parsing

"""

import logging

from six import with_metaclass  # for python compatibility
from abc import ABCMeta, abstractmethod
import pendulum as pm
import warnings

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
    TIME_CALLS = { 'hour': lambda n: pm.now().add(hours=-1*n).timestamp,
                   'day': lambda n: pm.now().add(days=-1*n).timestamp,
                   'week': lambda n: pm.now().add(days=-7*n).timestamp,
                   'all': lambda: 0,
                 }

    BASE_QUERY = "SELECT * FROM {tb} WHERE ts > '{ts}' AND channel = '{c}' ALLOW FILTERING;"


    def __init__(self, cluster_ips, session_keyspace, table_name):
        self.cluster = Cluster(cluster_ips)
        self.session = self.cluster.connect(session_keyspace)
        self.table_name = table_name

        self.CUSTOM_QUERIES = {}
        self.__channels = None

    def add_query(self, label, query):
        """Adds a custom query to the QUERIES dictionary

        Parameters
        ----------
        label : str
            label of the CQL query to be called upon
        query : str
            CQL query to be executed

        """
        self.CUSTOM_QUERIES[label] = query

    def list_channels(self, table=None):
        """List the channels avaialable for the table

        Parameters
        ----------
        table : str
            override table_name specified on instantiation

        Returns
        -------
        set(str)
            Set with all the channels available in the specified table
        """
        if table is None:
            # Obtain channels for the object's `table_name`
            if self.__channels is None:
                self.__channels = set()
                for r in self.session.execute('select DISTINCT channel from {}'.format(self.table_name)):
                    self.__channels.add( r.channel )

            return self.__channels

        else:
            # Obtain the channel for the table specified
            temp_channels = set()
            for r in self.session.execute('select DISTINCT channel from {}'.format(table)):
                temp_channels.add( r.channel )

            return temp_channels

    def get_messages(self, type_of_query, periods=1, channel=None, table=None, min_words=5):
        """Gets the stream of messages

        Parameters
        ----------
        type_of_query : str
            Label of the query type unless custom queries are added: 'hour', 'day', 'week'
        periods : int, optional
            Number of periods you want to query back
        channel : str, optional
            channel to be queried
        table : str, optional
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

        # If the type_of_query is one of the base
        if type_of_query in self.TIME_CALLS:
            qtimestamp = self.TIME_CALLS[type_of_query](periods)
            print self.BASE_QUERY.format(tb=qtable, ts=qtimestamp, c=channel)
            rows = self.session.execute( self.BASE_QUERY.format(tb=qtable, ts=qtimestamp, c=channel) )

        # Else, fetch query from CUSTOM_QUERIES
        else:
            try:
                query = self.CUSTOM_QUERIES[type_of_query]
            except KeyError:
                error_msg = 'The specific type_of_query ({}) was not found. Queries can be added with `add_query`'
                raise KeyError(error_msg.format(type_of_query))

            rows = self.session.execute(query)

        if not rows:
            warnings.warn('No messages were returned from the query specified')

        for r in rows:
            # Only stream messages with more than the specified amount of minimum words
            if len(r.message_text.split()) < min_words:
                continue

            # Compute timestamps and yield
            try:
                timestamp = float(r.ts)
            except ValueError:
                _datetime = pm.from_format(r.ts[:19], fmt='%Y-%m-%dT%H:%M:%S')
                timestamp = float(_datetime.timestamp) + float(r.ts.split('+')[0].split('.')[-1])
            finally:
                yield( Message(id=r.ts,
                               text=r.message_text,
                               author=r.user,
                               team=r.team,
                               url=r.message_url,
                               timestamp=timestamp) )


