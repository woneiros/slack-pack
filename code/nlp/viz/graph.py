# -*- coding: utf-8 -*-

"""Graph visualization of the most significant words in a topic and their relationship

.. module:: nlp.viz.cloud
   :platform: Unix, Windows
   :synopsis: Visualization of topics in an undirected graph

.. |message| replace:: :class:`nlp.text.message.Message`
.. |topic| replace:: :class:`nlp.text.topic.Topic`
.. |window| replace:: :class:`nlp.text.window.Window`
.. |corpus| replace:: :class:`nlp.text.corpus.Corpus`
.. |model| replace:: :class:`nlp.text.models.Summarizer`

"""

from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import networkx as nx

# TODO: try out with n-gram... but also with the coocurrence in the documents per se

class Wordgraph(object):
    """Collection of most significant words in a topic displayed with the relationships between the words

    Attributes
    ----------
    document : list[tuples(int,int)]
        List of tuples of the term-id and the count
    model : |model|
        Model with `get_top_terms` method which (given a document and an integer n) shoots out the top–n terms with their weights
    wcloud : graph
        `Graph` object from the package `networkx<http://networkx.readthedocs.io/en/networkx-1.10/>`_
    max_words : int
        Maximum number of words to be shown on the wordcloud
    """
    def __init__(self, model, document_id, max_words=10):
        """Summary

        Parameters
        ----------
        model : |model|
            Model with `get_top_terms` method which (given a document and an integer n) shoots out the top–n terms with their weights
        document_id : int
            Index of topic to obtain the TF-IDF score
        max_words : int, optional
            Maximum number of words to be shown on the wordcloud
        """
        self.model = model
        self.document_id = document_id
        self.corpus = self.model.uni_corpus if self.model.n_grams == 1 else self.model.n_gram_corpus
        self.max_words = max_words

        self.wcloud = wc.WordCloud(background_color=background)
        self.generate_wordcloud()


    def __compute_nodes(self, document_id):
        nodes = Counter()
        for tkn in self.corpus[document_id]:
            nodes.update( tkn.split() )

        self.NODES = { i: n[0] for i,n in enumerate(nodes.most_common(self.max_words)) }


    def __compute_edges(self, document_id):
        self.EDGES = defaultdict( lambda: 0 )

        for nd1, w1 in self.NODES.iteritems():
            for nd2, w2 in self.NODES.iteritems():
                self.EDGES += sum([ 1 for sent in self.corpus[document_id] if (w1 in sent.split()) and (w2 in sent.split()) ])

    def generate_graph(self):
        self.G = nx.Graph()

        for nd in NODES.iterkeys():
            self.G.add_node(nd)

        for ed in set(EDGES):
            self.G.add_edge(ed[0], ed[1])

        nx.draw_networkx_labels(self.G, nx.spring_layout(self.G), labels=self.NODES, font_size=16)


    def show(self):
        """Plot the wordgraph
        """
        nx.draw(self.G)
        plt.show()

    def save_png(self, filepath):
        """Summary

        Parameters
        ----------
        filepath : str
            Path to the file where the wordgraph will be stored to
       """
        nx.draw(self.G)
        plt.savefig(filepath)
        plt.close()

