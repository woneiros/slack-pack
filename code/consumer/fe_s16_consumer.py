from awaybot_consumer import AwaybotConsumer

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


logger = logging.getLogger('fe_s16_awaybot_consumer_logger')
logger.setLevel(logging.DEBUG)
LOGFILE = 'log/fe_s16_consumer'

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

ac = AwaybotConsumer(
    "54.197.178.209:9092",
    "fe_s16_topic",
    ['54.175.189.47'],
    'test_keyspace')
logger.info("Connected to kafka and cassandra clusters!")
ac.session.execute("""
    CREATE TABLE IF NOT EXISTS fe_s16_messages (
        uuid text,
        message_text text,
        ts text,
        user text,
        team text,
        type text,
        channel text,
        message_url text,
        PRIMARY KEY (channel, ts)
    )
    """)
prepared_msg = ac.session.prepare("""
    INSERT INTO fe_s16_messages (uuid, message_text, ts,
        user, team, type, channel, message_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """)
for msg in ac.consumer:
    msg = json.loads(msg.value)
    if sorted(
        [
            u'text', u'ts', u'user',
            u'team', u'type',
            u'channel', u'uuid', u'message_url'
        ]
    ) == sorted(msg.keys()):

        ac.session.execute(
            prepared_msg,
            (msg['uuid'], msg['text'],
             msg['ts'], msg['user'],
             msg['team'], msg['type'],
             msg['channel'], msg['message_url']))
        # logger.info(
        #     'Consume Message:\n{}'.format(msg['uuid']))
        logger.info(msg)

