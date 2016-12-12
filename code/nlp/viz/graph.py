# -*- coding: utf-8 -*-

"""Graph visualization of the most significant words in a topic and their relationship

.. module:: nlp.viz.graph
   :platform: Unix, Windows
   :synopsis: Visualization of topics in an undirected graph

.. |message| replace:: :class:`nlp.text.message.Message`
.. |topic| replace:: :class:`nlp.text.topic.Topic`
.. |window| replace:: :class:`nlp.text.window.Window`
.. |corpus| replace:: :class:`nlp.text.corpus.Corpus`
.. |model| replace:: :class:`nlp.text.models.Summarizer`

"""

from collections import Counter, defaultdict
from itertools import combinations
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx


class Wordgraph(object):
    """Collection of most significant words in a topic displayed with the relationships between the words"""

    COLOR_BASE = ["#DE1D64","#24927D","#72CADB","#E7A733"]

    def __init__(self, model, document_id, max_words=10, min_font=10, max_font=20, edge_cmap=plt.cm.Blues):
        """Summary

        Parameters
        ----------
        model : |model|
            Model with `get_top_terms` method which (given a document and an integer n) shoots out the top–n terms with their weights
        document_id : int
            Index of topic to obtain the TF-IDF score
        max_words : int, optional
            Maximum number of words to be shown on the wordcloud
        min_font : int, optional
            Description
        max_font : int, optional
            Description
        edge_cmap : TYPE, optional
            Description
        """
        self.model = model
        self.document_id = document_id
        self.max_words = max_words
        self.MIN_FONT = min_font
        self.MAX_FONT = max_font
        self.EDGE_CMAP = edge_cmap

        self.ngrams_in_doc = map( lambda x: self.model.n_gram_corpus.dictionary.get(x[0]), self.model.n_gram_corpus.corpus[self.document_id] )
        self.reverse_uni_dict = { v:k for k,v in self.model.uni_corpus.dictionary.iteritems() }
        self.codified_ngrams = map( lambda x: [ self.reverse_uni_dict[w] for w in x.split() ], self.ngrams_in_doc)

        self.__compute_nodes()
        self.__compute_edges()

        self.generate_graph()

    def __compute_nodes(self):
        """Generates the nodes based on the top n-grams from the specified model
        """
        ALL_NODES = map( lambda x: x[0], self.model.uni_corpus.corpus[ self.document_id ] )
        TOP_NODES = set()
        weights = defaultdict(lambda: 0)

        for trg, sc in self.model.get_top_terms(document_id=self.document_id, top=self.max_words):
            for w in trg.split():
                TOP_NODES.add( self.reverse_uni_dict[w] )
                weights[w] += sc

        self.TOP_NODES = list(TOP_NODES)
        TOP_NODES_WEIGHTS = map( lambda x: weights[self.model.uni_corpus.dictionary.get(x)] , TOP_NODES )
        self.TOP_NODES_WEIGHTS = map( lambda x: x / max(TOP_NODES_WEIGHTS), TOP_NODES_WEIGHTS )  # make them between 0-1
        self.TOP_NODES_INTS = map( lambda x: int(100. * x / min(TOP_NODES_WEIGHTS) ), TOP_NODES_WEIGHTS )  # make them ints

    def __compute_edges(self):
        """Generates the edges based on the co-ocurrences of the top tokens in the top n-grams from the specified model
        """
        self.EDGES = defaultdict( lambda: 0 )
        for ngram in self.codified_ngrams:
            pairs = combinations( filter(lambda x: x in self.TOP_NODES, ngram), 2 )
            for a,b in pairs:
                if a != b:
                    a, b = min(a,b), max(a,b)  # always define EDGES by low-high
                    self.EDGES[(a,b)] += 1

    def generate_graph(self):
        """Generates the graph with the nodes and edges, adds labels and styles (color, size and font)

        Returns
        -------
        TYPE
            Description
        """
        self.gr = nx.Graph()

        for nd in self.TOP_NODES:
            self.gr.add_node(nd)

        for ed in self.EDGES.iterkeys():
            self.gr.add_edge(ed[0], ed[1])

        self.LABELS={}
        for w in self.TOP_NODES:
            self.LABELS[w] = self.model.uni_corpus.dictionary.get(w)

        self.FONT_SIZES = map( self.rescale , self.TOP_NODES_INTS )
        self.SIZES = [ x*5 for x in self.TOP_NODES_INTS ]
        self.COLORS = np.random.choice(self.COLOR_BASE, size=len( self.gr.nodes() ), replace=True)

        self.pos = nx.spring_layout(self.gr)

    def rescale(self, x):
        """Rescale a number to the specified font according to the specified max and min font

        Parameters
        ----------
        x : TYPE
            Description

        Returns
        -------
        TYPE
            Description
        """
        max_int = max(self.TOP_NODES_INTS)
        min_int = min(self.TOP_NODES_INTS)
        return self.MIN_FONT + (self.MAX_FONT - self.MIN_FONT) * (x - min_int)/(max_int - min_int)

    def show(self):
        """Plot the wordgraph
        """
        nx.draw(self.gr, self.pos,
                node_size=1,
                edge_color=range( len(self.gr.edges()) ),
                width=2,
                edge_cmap=self.EDGE_CMAP)

        nx.draw_networkx_nodes(self.gr, self.pos,
                               nodelist=self.TOP_NODES,
                               node_size=self.SIZES,
                               node_color=self.COLORS,
                               label=self.LABELS )

        nx.draw_networkx_labels(self.gr, self.pos, self.LABELS, font_size=13, font_color='#361137')
        plt.show()

    def save_png(self, filepath):
        """Saves the wordgraph as a png image to the specified filepath

        Parameters
        ----------
        filepath : str
            Path to the file where the wordgraph will be stored to
        """
        nx.draw(self.gr, self.pos,
                node_size=1,
                edge_color=range( len(self.gr.edges()) ),
                width=2,
                edge_cmap=self.EDGE_CMAP)

        nx.draw_networkx_nodes(self.gr, self.pos,
                               nodelist=self.TOP_NODES,
                               node_size=self.SIZES,
                               node_color=self.COLORS,
                               label=self.LABELS )

        nx.draw_networkx_labels(self.gr, self.pos, self.LABELS, font_size=13, font_color='#361137')

        plt.savefig(filepath)
        plt.close()

