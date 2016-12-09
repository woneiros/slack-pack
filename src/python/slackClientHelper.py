
from slackclient import SlackClient
import logging

# TODO:
#       define logging
#       define assertions in main class
#       test assertions one-by-one

class slackClient:
    'This is our slackClient wrapper'
    def __init__(self, token=None):
        'initializing slack client'
        self.token = token
        self.sc = None
        self.status = False
    def getTokenFromFile(self, auth_file):
        '''Function that returns the slack token contained
        in the supplied file.

        args: {
            auth_file: A single line text file containing
                a valid slack authorization token.
        }
        returns: None
        '''
        token_file = open(auth_file, 'r')
        token = [line.strip() for line in token_file.readlines()][0]
        token_file.close()
        self.token = token
    def connect(self):
        '''connect client to slack team RTM API.
        Raises ValueError if connection fails. 
        '''
        self.sc = SlackClient(self.token)
        token_test = self.sc.api_call("api.test")
        if not token_test['ok']:
            raise ValueError(
                "Could not connect to Slack API. "
                "Check that token is valid.")
        else:
            self.status = True
    def apiCall(self):
        'generate generic call to slack RTM API'
        print "apiCall"
    def apiGet(self):
        'return response from get-like call to slack RTM API'
        print "apiGet"
    def apiPost(self):
        'post-like request to slack RTM API'
    def getChannelList(self):
        '''return channel list for the slack team associated
        with the given token'''
        if not self.status:
            print 'connecting'
            self.connect()
        cl = [
            channel_dict['id'] for channel_dict in 
            self.sc.api_call("channels.list")['channels']]
        return cl

    def channelCheck(self):
        'lorem ipsum'
        channels = []
        for id in channels:
            print ""
if __name__ == "__main__":