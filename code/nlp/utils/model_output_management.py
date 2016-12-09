import os
import sys
import boto3
import logging
from Queue import PriorityQueue
from collections import namedtuple


logger = logging.getLogger('model_output_handler_log')
logger.setLevel(logging.DEBUG)
LOGFILE = 'log/model_output_handler'

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


class OutputHelper(object):

    Viz = namedtuple('Viz', 'viz_path message_url team channel duration duration_unit')

    def __init__(self):
        self.output_ojects = PriorityQueue(0)
        self.sdb_status = False
        self.s3_status = False

    def simpledbConnect(self):
        """
        Function that uses the supplied token to connect to the AWS simpleDB
        client. Quits if failure to connect.

        Parameters:
        -----------
        None

        Returns: 
        ----------
        None
        """
        try:
            self.sdb = boto3.client('sdb')
        except:
            # logger.error(
            #     "Failed to connect to AWS. Have you configured "
            #     "AWS CLI?", exc_info=True)
            sys.exit()
        else:
            self.sdb_status = True
        return


    def s3Connect(self):
        """
        Function that uses the supplied token to connect to the AWS simpleDB
        client. Quits if failure to connect.

        Parameters:
        -----------
        None

        Returns: 
        ----------
        None
        """
        try:
            self.s3 = boto3.resource('s3')
        except:
            # logger.error(
            #     "Failed to connect to AWS. Have you configured "
            #     "AWS CLI?", exc_info=True)
            sys.exit()
        else:
            self.s3_status = True
        return


    def add_viz(self, viz_path, starter_message_url, team, channel, duration, duration_unit):
        new_viz = self.Viz(viz_path, starter_message_url, team, channel, duration, duration_unit)
        priority_ts = starter_message_url.split('/')[-1].replace('p', '')
        self.output_ojects.put((priority_ts, new_viz))
        return

    
    def upload(self, s3_bucket='awaybot_test', simple_db_domain='awaybot'):
        if not self.s3_status:
            self.s3Connect()
        if not self.sdb_status:
            self.simpledbConnect()

        sdb_payload = {
            'archiveURL': '',
            'modelURL': '',
            'numMessages': '0'
        }
        vizes = 0
        while not self.output_ojects.empty():
            viz = self.output_ojects.get()[1]

            # Upload to s3 and make public
            s3_viz_name = '{}_{}_{}_{}_{}.png'.format(
                viz.team, viz.channel, viz.duration, viz.duration_unit, vizes)
            viz_obj = self.s3.Object(s3_bucket, s3_viz_name)
            upload_viz_to_s3 = viz_obj.upload_file(viz.viz_path)
            viz_obj.Acl().put(ACL='public-read')
            s3_viz_url = 'https://s3.amazonaws.com/{}/{}'.format(
                s3_bucket, s3_viz_name)
            logger.info('Uploaded image to s3: {}'.format(s3_viz_url))
            
            vizes += 1
            # Update SimpleDB
            viz_sdb_key = '{}_{}_{}_{}_{}'.format(
                viz.team, viz.channel, viz.duration, viz.duration_unit, vizes)
            duration_sdb_key = '{}_{}_{}_{}'.format(
                viz.team, viz.channel, viz.duration, viz.duration_unit)
            sdb_payload['archiveURL'] = viz.message_url
            sdb_payload['modelURL'] = s3_viz_url
            
            sdb_payload['numMessages'] = str(vizes)
            item_attrs = [
                    {'Name': 'modelURL', 'Value': str(sdb_payload['modelURL']), 'Replace': True},
                    {'Name': 'archiveURL', 'Value': sdb_payload['archiveURL'], 'Replace': True}
                    ]
            self.sdb.put_attributes(
                DomainName=simple_db_domain,
                ItemName=viz_sdb_key,
                Attributes=item_attrs)
            logger.info("Created SimpleDB item {}".format(viz_sdb_key))
            # logger.info(response)

        num_message_attrs = [
            {'Name': 'numMessages', 'Value': str(sdb_payload['numMessages']), 'Replace': True},
            ]
        self.sdb.put_attributes(
                DomainName=simple_db_domain,
                ItemName=duration_sdb_key,
                Attributes=num_message_attrs)
        logger.info("Created SimpleDB item {}".format(duration_sdb_key))
        # logger.info(response)
        return

    def updateImageCount(self, team, channel, duration, duration_unit, simple_db_domain='awaybot'):
        if not self.sdb_status:
            self.simpledbConnect()
        item_name = '{}_{}_{}_{}'.format(team, channel, duration, duration_unit)
        no_message_attrs = [
            {'Name': 'numMessages', 'Value': '0', 'Replace': True},
        ]
        self.sdb.put_attributes(
                DomainName=simple_db_domain,
                ItemName=item_name,
                Attributes=no_message_attrs)
        logger.info("Created SimpleDB item {}".format(item_name))
        return








