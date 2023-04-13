from tqdm import tqdm

from algorithm.base import BaseAlgorithm
from graph import Graphlet
from util.heap import MyHeap
from util.logger_util import LoggerUtil

logger = LoggerUtil.get_logger("dp_graphlet_counter")


class DPGraphletCounter(BaseAlgorithm):
    def __init__(self, graph, mode_color_map):
        """
        Initialize the graphlet counter
        :param graph: the graph
        :param mode_color_map: the map of key: node name, value: node color
        """
        super().__init__(graph, mode_color_map)
        self._graphlet_count_map = {}

    def count_graphlets(self, graphlet_size=3):
        """
        Count the graphlets of a given size
        :param graphlet_size: the size of the graphlet
        :return: the map of key: graphlet hash, value: list of graphlets
        """
        # get the list of nodes sorted by name
        nodes_list = sorted(list(self.graph.get_nodes()))
        # level 1: list of node groups of size 1
        nodes_group = set((node,) for node in nodes_list)
        # map of key: number of nodes, value: list of node groups
        for size in range(2, graphlet_size + 1):
            logger.info("Creating node groups of size %d", size)
            nodes_group = self.get_node_groups_of_size_n(nodes_group)
        logger.info("Creating graphlets of size %d", graphlet_size)
        for node_group in tqdm(nodes_group):
            self._create_and_save_graphlet(node_group)
        return self._graphlet_count_map

    def get_node_groups_of_size_n(self, nodes_group):
        """
        Get the node groups of size n
        :param nodes_group: the node groups of size n - 1
        :return: the node groups of size n
        """
        next_nodes_group = set()
        for node_group in tqdm(nodes_group):
            node_set = set(node_group)
            for node_name in node_group:
                node = self.graph.get_node(node_name)
                neighbors = node.get_undirected_neighbors()
                for neighbor in neighbors:
                    if neighbor.name not in node_set:
                        next_node_group = tuple(sorted(node_group + (neighbor.name,)))
                        if next_node_group not in next_nodes_group:
                            next_nodes_group.add(next_node_group)
        return next_nodes_group

    def _create_and_save_graphlet(self, node_group):
        """
        Create and save the graphlet
        :param node_group: the node group
        """
        node_set = []
        for node_name in node_group:
            node = self.graph.get_node(node_name)
            node_set.append(node)
        g = Graphlet(node_set, self.graph)
        hash_key = hash(g)
        if hash_key not in self._graphlet_count_map:
            self._graphlet_count_map[hash_key] = (g, 1)
        else:
            self._graphlet_count_map[hash_key] = (self._graphlet_count_map[hash_key][0],
                                                  self._graphlet_count_map[hash_key][1] + 1)

    def display_frequent_graphlet_stats(self, count=5, name='dp_algo'):
        """
        Display the frequent graphlet stats
        :param count: the number of graphlets to display
        :param name: the name of the algorithm
        """
        heap = MyHeap(key=lambda x: x[2])
        for graphlet_hash, value in self._graphlet_count_map.items():
            heap.push((graphlet_hash, value[0], value[1]))
            if len(heap) > count:
                heap.pop()
        top_graphlets = []
        while len(heap) > 0:
            graphlet_hash, graphlet, count = heap.pop()
            top_graphlets.append((graphlet, count))
        top_graphlets.reverse()
        for graphlet, count in top_graphlets:
            logger.info("Graphlet: %s, Count: %s, with algo: %s", graphlet, count, 'dp_algo')
