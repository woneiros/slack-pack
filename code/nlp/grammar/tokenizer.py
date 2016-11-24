# -*- coding: utf-8 -*-

"""Message tokenization implementation

.. module:: nlp.grammar.tokenizer
   :platform: Unix, Windows
   :synopsis: Tokenization of messsages

.. |message| replace:: :class:`nlp.text.message.Message`

"""

from nltk.stem.snowball import SnowballStemmer
from nltk import word_tokenize
from nltk.corpus import stopwords
import re



class MessageTokenizer(object):
    """A Message tokenizer

    Attributes
    ----------
    cache : dict
        Cache with the tokenized/stemmed words (applying _memoization_)
    stemmer : callable
        `Word stemmer <https://en.wikipedia.org/wiki/Stemming>`_, defaults to the NLTK's SnowballStemmer
    stopWords : list[int]
        Defaults to NLTK's emglish stopwords: `stopwords.words("english")`
    userRe : `RegexObject <https://docs.python.org/2/library/re.html?highlight=pattern#re.RegexObject>`_
        Compiled regex pattern

    Note
    ----
    None of these attributes should be specified on instantiation

    """

    def __init__(self):
        self.stopWords = []  # stopwords.words("english")
        self.stemmer = SnowballStemmer('english')
        self.cache = {}
        self.userRe = re.compile('<@U\w\w\w\w\w\w\w\w>')  # TODO: change the user compilation

    def __call__(self, message):
        """ Fully processes a message (stem and tokenize)

        Parameters
        ----------
        message : |message|
            Message to be processed

        Returns
        -------
        |message|
            Processed message

        """
        return [ self.stemmer.stem(t) for t in self.getValidTokens(message) ]


    def tokenize(self, message):
        """Tokenizes the message text and removes the usernames

        Parameters
        ----------
        message : |message|
            Message to be processed

        Returns
        -------
        |message|
            Parsed message

        """
        return [ w for w in word_tokenize(self.removeUsers(message)) ]

    def punctuationTokenize(self, message):
        """Filters the non alpha-numeric tokenized words

        Parameters
        ----------
        message : |message|
            Message to be processed

        Returns
        -------
        |message|
            Parsed message

        """
        return [ w for w in self.tokenize(message) if w.isalnum() ]

    def getValidTokens(self, message):
        """Obtain the tokenized words and filter stopwords

        Parameters
        ----------
        message : |message|
            Message to be processed

        Returns
        -------
        |message|
            Parsed message

        """
        return [ word for word in self.punctuationTokenize(message)
            if word not in self.stopWords ]

    def removeUsers(self, message):
        """Remove usernames from the message

        Parameters
        ----------
        message : |message|
            Message to be processed

        Returns
        -------
        |message|
            Parsed message

        """
        return self.userRe.sub('', message)


# TODO: create TopicTokenizer
class TopicTokenizer(object):
    pass