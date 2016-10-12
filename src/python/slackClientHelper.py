#!/usr/bin/env python

from slackclient import SlackClient as sc
import logging

# TODO:
#       define logging
#       define assertions in main class
#       test assertions one-by-one

class slackClient:
  'This is our slackClient wrapper'
  def __init__(self, token=None):
      'initializing slack client'
      if not token:
          print "stuff"
      else:
          print "stuff"
      self.token = token
      self.sc = None

  def connect(self):
      'connect client to slack team RTM API'
      print "stuff"

  def apiCall(self):
      'generate generic call to slack RTM API'
      print "apiCall"
  def apiGet(self):
      'return response from get-like call to slack RTM API'
      print "apiGet"
  def apiPost(self):
    'post-like request to slack RTM API'
  def getChannelList(self):
      'return channel list for '
    cl = sc.api_call("channels.list")
    print "getChannelList"

  def channelCheck(self):
      'lorem ipsum'
    channels = []
    for id in channels:
      print ""

if __name__ == "__main__":
