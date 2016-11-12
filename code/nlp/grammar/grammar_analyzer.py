# -*- coding: utf-8 -*-

"""Grammar analysis of messages to identify reply messages given the starting sentence

.. module:: nlp.grammar.grammar_analyzer
   :platform: Unix, Windows
   :synopsis: Analysis of grammar to identify reply messages

.. |message| replace:: :class:`nlp.text.message.Message`
.. |tokenizer| replace:: :class:`nlp.text.grammar.tokenizer`

"""

import nltk
from sets import Set

class SentenceGrammarAnalyzer:
    """Analyzes grammar to assess if a message is a reply to a previous message

    Some message are replies based on their opening sentence, e.g. messages starting with words such as `OK`

    Attributes
    ----------
    message : |message|
        Message to be analyzed
    REPLY_POS_VALID_UNIVERSAL_TAGS : TYPE
        Description
        .. note::
            Check `Penn treebank <http://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html>`_ for a good list
    REPLY_POS_VALID_UPENN_TAGS : set[str]
        Set of reply-message starting POS-tags
    REPLY_STARTERS : list[str]
        List of reply-message starters
    tokenizer :
        Tokenizer for processing the message

    Parameters
    ----------
    message : |message|
        Message to be analayzed
    tokenizer : |tokenizer|
        Tokenizer for processing the message

    """

    REPLY_POS_VALID_UNIVERSAL_TAGS = Set(['CONJ'])
        # check http://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html for a good list
    REPLY_POS_VALID_UPENN_TAGS = Set(['WDT', 'DT'])
    REPLY_STARTERS = Set(['ok', 'ok.', 'k', 'k.' 'mine', 'his', 'hers', 'theirs', 'ours'])

    def __init__(self, message, tokenizer):
        self.message = message
        self.tokenizer = tokenizer

    def isAReply(self):
        """Summary

        Returns
        -------
        tuple(bool, str)
            Assessment of message being a starter: (Boolean, Reason)

        """
        stemmedTokens = self.tokenizer.stemAndTokenize(self.message)

        if len(stemmedTokens) <= 1:
            return (True, 'stemmed length of ' + str(len(stemmedTokens)))

        tokens = self.tokenizer.tokenize(self.message)
        univeralTags = nltk.pos_tag(tokens, tagset='universal')

        if univeralTags[0][1] in SentenceGrammarAnalyzer.REPLY_POS_VALID_UNIVERSAL_TAGS:
            return (True, 'universal tag ' + univeralTags[0][1])

        upennTags = nltk.pos_tag(tokens)
        if upennTags[0][1] in SentenceGrammarAnalyzer.REPLY_POS_VALID_UPENN_TAGS:
            return (True, 'upenn tag ' + upennTags[0][1])
        if tokens[0].lower() in SentenceGrammarAnalyzer.REPLY_STARTERS:
            return (True, 'reply starter ' + tokens[0].lower())
        return (False, 'not a reply')

