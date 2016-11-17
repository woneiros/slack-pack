"""Message extraction and parsing module

.. module:: nlp.text.extractor
   :platform: Unix, Windows
   :synopsis: Message extraction and parsing

"""

from abc import ABCMeta, abstractmethod
import json
from message import Message




class Extractor(metaclass=ABCMeta):
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
    ANON_TEXT = u'anon_text'
    TIMESTAMP = u'ts'

    def __init__(self, file_name):
        self.file_name = file_name
        self.jsonObject = self.parse()

    def get_messages(self):
        """Gets the stream of messages

        Returns
        -------
        iterator(|message|)
            Stream of messages
        """
        with open(self.file_name) as data_file:
            return json.load(data_file)

        users = self.jsonObject[self.USER]
        texts = self.jsonObject[self.ANON_TEXT]
        timestamps = self.jsonObject[self.TIMESTAMP]

        return ( Message(int(id), texts[id], users[id], timestamps[id]) for id in users.keys() )


# TODO: implement CassandraParser
class CassandraExtractor(Extractor):
    """ Parser of the raw JSON Slack generated history files

    Warning
    -------
    This class has not been yet implemented

    """

    def __init__(self):
        raise NotImplementedError()


    def get_messages(self):
        raise NotImplementedError()
