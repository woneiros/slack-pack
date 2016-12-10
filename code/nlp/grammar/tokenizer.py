# -*- coding: utf-8 -*-

"""Message tokenization implementation

.. module:: nlp.grammar.tokenizer
   :platform: Unix, Windows
   :synopsis: Tokenization of messsages

.. |message| replace:: :class:`nlp.text.message.Message`
.. |re_pattern| replace :: `re object<https://docs.python.org/3/library/re.html#re-objects>`_

"""

from nltk.stem.snowball import SnowballStemmer
from nltk import word_tokenize
from nlp.text.stopwords import STOPWORDS
import re


class SimpleCleaner(object):
    """A light-weight text cleaner: removes stopwords, usernames and symbols (some are removed some are wrapped in spaces)

    Parameters
    ----------
    remove_stopwords : bool, optional
        Remove stopwords on clean (defaults to True)
    symbols_to_remove : |re_pattern|, optional
        Symbols to remove (defaults to `,.:'"<>!?*\/`)
    symbols_to_space : |re_pattern|, optional
        Symbols to wrap in whitespace (defaults to `()[]{}`)
    user : |re_pattern|, optional
        Username pattern (defaults to `<@U-------->` or `<@u-------->`, where `-` is any alphanumeric)
    """
    PATTERNS = { 'user': re.compile('<@[Uu]\w{8}>'),
                 'symbols_remove': re.compile(ru'[\.,/\\<>\!\?\*\+"\'&`´#@\u2019]', re.UNICODE),
                 'symbols_space': re.compile('[:;_\(\)\[\]\{\}]') }

    def __init__(self, remove_stopwords=True, user=None, symbols_to_remove=None, symbols_to_space=None):
        self.remove_stopwords = remove_stopwords
        if (user is not None) and hasattr(user, 'sub'):
            self.PATTERNS['user'] = user
        if (symbols_to_remove is not None) and hasattr(symbols_to_remove, 'sub'):
            self.PATTERNS['symbols_remove'] = symbols_to_remove
        if (symbols_to_space is not None) and hasattr(symbols_to_space, 'sub'):
            self.PATTERNS['symbols_space'] = symbols_to_space

    def __call__(self, text):
        """ Fully processes a message

        Parameters
        ----------
        message : |message|
            Message to be processed

        Returns
        -------
        |message|
            Processed message
        """
        text = self.PATTERNS['user'].sub('', text.lower() )
        text = self.PATTERNS['symbols_remove'].sub('', text)
        text = self.PATTERNS['symbols_space'].sub(' ', text)

        if self.remove_stopwords:
            return ' '.join( filter(lambda x: x not in STOPWORDS, text.split()) )
        else:
            return text


class MessageTokenizer(object):
    """A Message tokenizer performing tokenization, stemming and stopword removal

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
        self.userRe = re.compile('<@[Uu]\w{8}>')

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
