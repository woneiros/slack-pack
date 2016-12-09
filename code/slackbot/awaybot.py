# -*- coding: utf-8 -*-



"""
  Awaybot - Slackbot that responds to
  \summarize commands of the form
  \summarize [channel] [duration] [time unit]

  Example \summarize #general 1 days

  Responds to user inputs by querying SimpleDB
  for the item that matches the input command.
  Items are of the form
  [team]_[channel]_[duration]_[time unit]



.. module:: awaybot

  :platform: Unix, Windows

  :synopsis: Slack API, Slackbot

"""


import os
import time
from slackclient import SlackClient
import boto3
import logging
from logging.handlers import RotatingFileHandler

# create logger
logger = logging.getLogger('awaybot_logger')
logger.setLevel(logging.DEBUG)
LOGFILE = "log/awaybot"

# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# create console handler, set level of logging and add formatter
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

# create file handler, set level of logging and add formatter
fh = logging.handlers.TimedRotatingFileHandler(LOGFILE, when='M', interval =1)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
fh.suffix = '%Y-%m-%d_%H-%M-%S.log'

# add handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)

class Slackbot:
    """
    A class for our slackbot
    """
    def __init__(self,
                 slack_client,
                 bot_name,
                 command):
        """
        Constructor for Slackbot class
        
        Parameters
        ----------
        slack_client : object
            The slack client object to interact with a slack team server
        bot_name : str
            The name (not ID) of the slackbot for the relevant slack team
        command : str
            The command to invoke the slackbot
        """
        try:
            logger.info("""Initializing bot with parameters:
            \tslack_client : %s
            \tbot_name : %s
            \tcommand : %s""" % (slack_client, bot_name, command))
            self.slack_client = slack_client
            self.command = command
            self.bot_name = bot_name
            self.sdb_status = False
            api_call = self.slack_client.api_call("users.list")
            if api_call.get('ok'):
                # retrieve all users so we can find our bot
                users = api_call.get('members')
                # indicator for whether a user has been found matching our bot
                user_found = False
                for user in users:
                    if 'name' in user and user.get('name') == self.bot_name:
                        self.bot_id = user.get('id')
                        user_found = True
                        print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
                if not user_found:
                    raise SlackUserNotFoundError("Could not find bot user with the name " + self.bot_name)
        except SlackUserNotFoundError as e:
            print 'SlackUserNotFoundError:', e.value
            # at this point, quitting if we hit this issue
            quit()
    
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
            logger.error(
                "Failed to connect to AWS. Have you configured "
                "AWS CLI?", exc_info=True)
            sys.exit()
        else:
            self.sdb_status = True
        return

    def handle_command(self, team, command, simpleDB_domain):
        """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
        
        Parameters
        ----------
        command : dtr
            the command passed to the slackbot
        payload : str
            the location of the payload to be delivered by slackbot 
        """
        # split up the command into its component parts
        if not self.sdb_status:
            self.simpledbConnect()
        split_command = command.split()
        
        # ensure that command sent to bot matches
        # and is well formatted
        if command.startswith(self.command) and len(split_command) == 4:

            # command components
            command_channel = split_command[1]
            command_duration = split_command[2]
            command_duration_units = split_command[3]
            channel_name = command_channel.split('|')[-1][:-1]
            sdbItem = '{}_{}_{}_{}'.format(
                team_name, channel_name,
                command_duration, command_duration_units)
            logger.info('Fetching number of items for {}'.format(sdbItem))
            fetch_num_topics = self.sdb.get_attributes(
                DomainName='awaybot', ItemName=sdbItem, ConsistentRead=True)

            ## CASE ONE: VALID COMMAND BUT INVALID TIME RANGE
            try:
                num_topics = fetch_num_topics['Attributes'][0]['Value']
            except:
                logger.info("Could not fetch number of topics from Simple DB for COMMAND '%s'" % (command))
                response = ("""Not sure what you mean. Use the */summarize* command with the *channel name* and the *duration*. 
                    For example, if you want to see 3 weeks of history in the #general channel, type: */summarize #general 3 weeks*.
                    Valid time values are 1-12 hours, 1-6 days, 1-6 weeks.""")

                # post the response to the channel
                self.slack_client.api_call("chat.postMessage",
                                           channel=channel,
                                           text=response,
                                           as_user=True)
            else:
                logger.info("""COMMAND %s has a valid format for processing:
                command_channel : %s
                command_duration : %s
                command_duration_units : %s""" % (command,
                                                  command_channel,
                                                  command_duration,
                                                  command_duration_units))

                ## CASE TWO: VALID COMMAND BUT NOT ENOUGH MESSAGES FOR WORDCLOUD GENERATION
                if not int(num_topics):
                    response = "{} has no topics for last {} {}".format(
                        command_channel, command_duration, command_duration_units)
                    self.slack_client.api_call("chat.postMessage",
                                           channel=channel,
                                           text=response,
                                           as_user=True)
                else:
                    ## CASE THREE: VALID COMMAND AND WORDCLOUDS WERE GENERATED.
                    
                    # Respond with the summary and how many topics
                    response = "Your summary for {} for {} {} ({} topics).".format(
                        command_channel, command_duration, command_duration_units, num_topics)

                    self.slack_client.api_call("chat.postMessage",
                                           channel=channel,
                                           text=response,
                                           as_user=True)


                    # Respond for each topic
                    for topic in xrange(1, int(num_topics) + 1, 1):
                        sdbImageItem = '{}_{}_{}_{}_{}'.format(
                            team_name, channel_name,
                            command_duration, command_duration_units, topic)

                        fetch_image = self.sdb.get_attributes(
                            DomainName='awaybot', ItemName=sdbImageItem, ConsistentRead=True)
                        topic_url = [i['Value'] for i in fetch_image['Attributes'] if i['Name'] == 'archiveURL'][0]
                        topic_wordcloud = [i['Value'] for i in fetch_image['Attributes'] if i['Name'] == 'modelURL'][0]


                        response = '<{}|Go To Topic {}>'.format(topic_url, topic)
                        # set the attachment which is the duration with the url to the word cloud
                        attachment = '[{"title": "Topic '+ str(topic) + '" , "image_url":"'+ topic_wordcloud +'"}]'

                        # send the response with the image
                        logger.info("""Sending:
                        \tchannel : %s
                        \ttext : %s
                        \timage_url : %s""" % (channel, response, attachment))
                        self.slack_client.api_call("chat.postMessage", channel=channel, 
                                              text=response, 
                                              attachments=attachment,
                                              as_user=True)

        # otherwise post our response to help the user our
        else:
            # response for when the bot doesn't know quite what to do
            logger.info("Incorrectly formatted COMMAND '%s' sent to BOT '%s'" % (command, self.bot_name))
            response = ("""Not sure what you mean. Use the */summarize* command with the *channel name* and the *duration*. 
                For example, if you want to see 3 weeks of history in the #general channel, type: */summarize #general 3 weeks*.
                Valid time values are 1-12 hours, 1-6 days, 1-6 weeks.""")

            # post the response to the channel
            self.slack_client.api_call("chat.postMessage",
                                       channel=channel,
                                       text=response,
                                       as_user=True)
            
    def parse_messages(self,
                       slack_rtm_output):
        """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.        
        Parameters
        ----------
        slack_rtm_output : list
            A list of outputs from the slack RTM API
        Returns
        -------
        str
            str slice after @ for identified slack RTM API text message
        str
            slack team channel ID
        """
        # by default set the output to what was spit out 
        # by the fire hose
        output_list = slack_rtm_output
        # if we actually got something and not just an
        # empty array
        if output_list and len(output_list) > 0:

            # loop through each of the messages
            for output in output_list:

                # if we have some text in the message and 
                # this bot is mentioned
                if output and 'text' in output and self.bot_id in output['text']:

                    # return text after the @ mention, whitespace removed
                    logger.info("BOT '%s' has received MESSAGE '%s'" % (self.bot_name, output))
                    at_bot = "<@" + self.bot_id + ">"
                    return output['text'].split(at_bot)[1].strip().lower(), \
                           output['channel']
        return None, None

class SlackUserNotFoundError(Exception):
    """
    Exception raised for error encountered for inexistent slack user name
    
    Attributes:
        message -- explanation of the error
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
        
class UnauthError(Exception):
    """
    Exception raised for error encountered for invalid slack credentials/token
    
    Attributes:
        message -- explanation of the error
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

if __name__ == "__main__":
    
    try:
        #######################################
        # THIS IS PREDEFINED PAYLOAD CODE START
        #######################################
        
        logger.info("Stating __main__, simple test for awaybot.py")
        
        SDB_DOMAIN = "awaybot"
        # SDB_ITEM = "test"
        
        # # connect to simpleDB
        # logger.info("Connecting to simpleDB")
        # simple_client = boto3.client('sdb')

        # # pull the relevant simpleDB entry
        # logger.info("Pulling ITEM '%s' from DOMAIN '%s'" % (SDB_ITEM, SDB_DOMAIN))
        # response = simple_client.get_attributes(DomainName=SDB_DOMAIN,
        #                                       ItemName=SDB_ITEM,
        #                                       ConsistentRead=True)

        # # gather just the link to the word cloud
        # word_cloud = [i['Value'] for i in response['Attributes'] if i['Name'] == 'modelURL'][0]
        # topic_url = [i['Value'] for i in response['Attributes'] if i['Name'] == 'archiveURL'][0]
        # payload = [word_cloud, topic_url]
        # logger.info("summary wordcloud URL: {}\ntopic url: {}".format(word_cloud, topic_url))

        #######################################
        # THIS IS PREDEFINED PAYLOAD CODE END
        #######################################

        READ_WEBSOCKET_DELAY = 1
        logger.info("RTM API read websocket delay set to '%s' seconds" % (READ_WEBSOCKET_DELAY))

        # try to connect to the real time messaging API
        sc = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

        bot = Slackbot(sc,
                     os.environ.get('SLACK_BOT_NAME'),
                     '/summarize')
        bot.simpledbConnect()

        team_name = sc.api_call('team.info')['team']['name']

        if bot.slack_client.rtm_connect():
            logger.info("starterbot connected and running!")
            # keep a continuous loop
            while True:
                # parse the output from the client using our
                # pre-defined parser function
                command, channel = bot.parse_messages(bot.slack_client.rtm_read())

                # if we have both a command and a channel, then
                # use our predefined handle command function
                # NOTE THAT THE PAYLOAD IS PREDEFINED
                if command and channel:
                    bot.handle_command(team_name, command, SDB_DOMAIN)

                # sleep for the number of seconds before reading from
                # the fire hose again
                time.sleep(READ_WEBSOCKET_DELAY)

        # if something went wrong, print out what happened
        else:
            raise UnauthError("Credentials/token invalid")
    except UnauthError as e:
        print 'UnauthError:', e
        quit()