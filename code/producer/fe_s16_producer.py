from awaybot_producer import AwaybotProducer
from slackclient import SlackClient
from kafka import KafkaClient, KafkaConsumer, KafkaProducer
import logging
import time
import os
import boto3
import sys
import uuid
import datetime
import json

# create logger
logger = logging.getLogger('fe_s16_awaybot_producer_logger')
logger.setLevel(logging.DEBUG)
LOGFILE = "log/fe_s16_awaybot"

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

ap = AwaybotProducer(
    token=os.environ.get('FE_S16_SLACK_TOKEN'),
    kafka_ip=os.environ.get('KAFKA_IP'))
team_id = ap.getTeamName()
team_domain = ap.getTeamDomain()
team_archive_url = r'https://{}.slack.com/archives/'.format(team_domain)
logger.info('Team name: {}'.format(team_id))
latest_timestamp = ap.getLatestTimestamp(
    domain='awaybot', team_name=team_id)
logger.info(
    'Latest timestamp for team {} is {}'.format(
        team_id, datetime.datetime.fromtimestamp(
            float(latest_timestamp)).strftime('%Y-%m-%d %H:%M:%S')))
channels = ap.getChannelList()
channel_dict = {}
for i in channels:
    channel_dict.update(i)
logger.info('Channnels available to producer: {}'.format
            (' '.join([i.values()[0] for i in channels])))
history = ap.fetchSlackHistory(
    team_name=team_id, archive_url=team_archive_url,
    channel_list=channels, timestamp=latest_timestamp)
c = 0


for msg in history:
    logger.info(msg)
    ap.produceMessage("fe_s16_topic", msg)
