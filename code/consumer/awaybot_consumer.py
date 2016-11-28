from kafka import KafkaClient, KafkaConsumer
from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import logging
import logging.handlers
import time
import json
import sys
import uuid


logger = logging.getLogger('awaybot_consumer_logger')
logger.setLevel(logging.DEBUG)
LOGFILE = 'log/awaybot_consumer'

# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# create console handler, set level of logging and add formatter
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

# create file handler, set level of logging and add formatter
fh = logging.handlers.TimedRotatingFileHandler(LOGFILE, when='M', interval=1)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
fh.suffix = '%Y-%m-%d_%H-%M-%S.log'

# add handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)


class AwaybotConsumer:

    """A class for consuming messages from awaybot kafka cluster."""

    def __init__(self, kafka_ip, kafka_topic, cassandra_ip, keyspace):
        """
        Constructor for AwaybotConsumer class

        Paramters:
        -----------
        kafka_ip: str or list
            The ip address(es) of the kafka cluster we will connect to.
            The format of the list is ['host:port', 'host:port', ...]
        kafka_topic: str
            The kafka topic(s) which the consumer will subscribe to. Multiple
            topics are passed as a single space-separated string.
        cassandra_ip: list
            The ip address(es) of the cassandra cluster we will connect to
            The format of the list is ['host', 'host', ...]
        keyspace: str
            The cassandra keyspace where we will insert data to
        """
        try:
            logger.info(
                "Initializing cassandra connection"
                " with parameters:\n\tip: {}\n\tkeyspace: {}".format(
                    cassandra_ip, keyspace))
            self.cluster = Cluster(cassandra_ip)
            self.session = self.cluster.connect(keyspace)
        except:
            logging.error(
                "Failed to connect to cassandra cluster", exc_info=True)
            sys.exit()

        try:
            logger.info(
                "Initializing kafka connection"
                " with parameters:\n\tip: {}\n\topic: {}".format(
                    kafka_ip, kafka_topic))
            self.consumer = KafkaConsumer(
                kafka_topic, bootstrap_servers=kafka_ip)
        except:
            logging.error(
                "Failed to connect to kafka cluster", exc_info=True)
            sys.exit()


if __name__ == "__main__":
    try:
        logger.info("Starting __main__, simple test for awaybot_consumer.py")

        ac = AwaybotConsumer(
            "54.197.178.209:9092",
            "test_topic",
            ['54.175.189.47'],
            'test_keyspace')
        logger.info("Connected to kafka and cassandra clusters!")
        # for msg in ac.consumer:
        #     print msg
        ac.session.execute("""
            CREATE TABLE IF NOT EXISTS awaybot_messages2 (
                uuid text,
                message_text text,
                ts text,
                user text,
                team text,
                type text,
                channel text,
                PRIMARY KEY (channel, ts)
            )
            """)
        prepared_msg = ac.session.prepare("""
            INSERT INTO awaybot_messages2 (uuid, message_text, ts,
                user, team, type, channel)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """)
        for msg in ac.consumer:
            msg = json.loads(msg.value)
            logger.info(msg)
            if sorted(
                [
                    u'text', u'ts', u'user',
                    u'team', u'type',
                    u'channel', u'uuid'
                ]
                    ) == sorted(msg.keys()):
                ac.session.execute(
                    prepared_msg, 
                    (msg['uuid'], msg['text'],
                     msg['ts'], msg['user'], 
                     msg['team'], msg['type'],
                     msg['channel']))
                logger.info(
                    'Consume Message:\n{}'.format(msg['uuid']))
            

    except:
        logging.error(
            "Failed to initialize consumer", exc_info=True)
        sys.exit()
