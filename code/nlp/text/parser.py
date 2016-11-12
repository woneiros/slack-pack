"""Message extraction and parsing module

.. module:: nlp.text.parser
   :platform: Unix, Windows
   :synopsis: Message extraction and parsing

"""

from abc import ABCMeta, abstractmethod
import json
from message import Message


USER = u'user'
ANON_TEXT = u'anon_text'
TIMESTAMP = u'ts'


# TODO: Implement anonymization on parse

class Parser(metaclass=ABCMeta):
    """ Abstract class for a message parser

    Note
    ----
    This is an *abstract class* and therefore it cannot be instantiated

    """

    @abstractmethod
    def getMessage(self):
        pass

    @abstractmethod
    def parse(self):
        pass


class JSONParser(Parser):
    """ Parser of the raw JSON Slack generated history files

    Parameters
    ----------
    file_name : str or IOBuffer
        Path to the JSON object with the messages

    """

    def __init__(self, file_name):
        self.file_name = file_name
        self.jsonObject = self.parse()

    def parse(self):
        with open(self.file_name) as data_file:
            return json.load(data_file)

    def getMessages(self):
        users = self.jsonObject[USER]
        texts = self.jsonObject[ANON_TEXT]
        timestamp = self.jsonObject[TIMESTAMP]
        return sorted(
            [ Message(int(id), texts[id], users[id]) for id in users.keys() ],
            key=lambda msg: msg.id() )


# TODO: implement CassandraParser
class CassandraParser(Parser):
    """ Parser of the raw JSON Slack generated history files

    Warning
    -------
    This class has not been yet implemented

    """

    def __init__(self):
        raise NotImplementedError()
        # self.file_name = file_name
        # self.jsonObject = self.parse()

    def parse(self):
        raise NotImplementedError()
        # with open(self.file_name) as data_file:
        #     return json.load(data_file)

    def getMessages(self):
        raise NotImplementedError()
        # users = self.jsonObject[USER]
        # texts = self.jsonObject[ANON_TEXT]
        # return sorted(
        #     [Message(int(id), texts[id], users[id]) for id in users.keys()],
        #     key=lambda message: message.getID())