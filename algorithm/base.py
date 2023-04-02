from abc import ABC, abstractmethod


class BaseAlgorithm(ABC):
    def __init__(self, graph, edge_color_map):
        """
        Base class for graphlet counting algorithms
        :param graph: graph
        :param edge_color_map: edge color map
        """
        self._graph = graph
        self._edge_color_map = edge_color_map

    @abstractmethod
    def count_graphlets(self, graphlet_size=3):
        """
        Count the graphlets in the graph
        :return:  the map of graphlet hash to graphlet
        """

    def generate_graphlet_visualization(self, algo, graphlets):
        for index, graphlet in enumerate(graphlets):
            graphlet.visualize("graphlet_{}_{}".format(algo, index + 1), self.edge_color_map)

    @property
    def graph(self):
        return self._graph

    @property
    def edge_color_map(self):
        return self._edge_color_map



