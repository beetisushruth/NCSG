from algorithm.base import BaseAlgorithm
from graph import Graphlet
from util.heap import MyHeap


class BruteForceGraphletCounter(BaseAlgorithm):

    def __init__(self, graph, edge_color_map):
        super().__init__(graph, edge_color_map)
        self._graphlet_count_map = {}
        self._processed_nodes = set()

    def count_graphlets(self, graphlet_target_size=3):
        """
            Count the graphlets in the graph
            :return:  the map of graphlet hash to graphlet
            """
        count = 0
        node_names = list(self._graph.get_nodes())
        node_combinations = self._get_node_combinations(node_names, graphlet_target_size)
        for node_combination in node_combinations:
            is_valid = self._check_valid_combination(node_combination, graphlet_target_size)
            if is_valid:
                count += 1
                self._create_and_save_graphlet(node_combination)
        print("Total number of graphlets: ", count)
        return self._graphlet_count_map

    def _get_node_combinations(self, node_names, size):
        """
            Get all possible combinations of nodes
            :param node_names: list of node names
            :param size: size of the combination
            :return: list of combinations
            """
        if size == 1:
            return [[node_name] for node_name in node_names]
        else:
            combinations = []
            for i in range(len(node_names)):
                for combination in self._get_node_combinations(node_names[i + 1:], size - 1):
                    combination.append(node_names[i])
                    combinations.append(combination)
            return combinations

    def _check_valid_combination(self, node_combination, size):
        nodes_set = set(node_combination)
        node_index_map = {node_name: i for i, node_name in enumerate(node_combination)}
        edge_count = 0
        for i, node_name in enumerate(node_combination):
            node = self.graph.get_node(node_name)
            for neighbor in node.get_undirected_neighbors():
                if neighbor.name in nodes_set and node_index_map[neighbor.name] > i:
                    edge_count += 1
                    if edge_count >= size - 1:
                        return True
        return False

    def _create_and_save_graphlet(self, node_group):
        node_set = []
        for node_name in node_group:
            node = self.graph.get_node(node_name)
            node_set.append(node)
        g = Graphlet(node_set, self.graph)
        hash_key = hash(g)
        self._graphlet_count_map.setdefault(hash_key, [])
        self._graphlet_count_map[hash_key].append(g)

    def display_frequent_graphlet_stats(self, count=5):
        heap = MyHeap(key=lambda x: len(x[1]))
        for graphlet_hash, graphlets in self._graphlet_count_map.items():
            heap.push((graphlet_hash, graphlets))
            if len(heap) > count:
                heap.pop()
        top_graphlets = []
        while len(heap) > 0:
            graphlet_hash, graphlets = heap.pop()
            top_graphlets.append((graphlets[0], len(graphlets)))
        top_graphlets.reverse()
        for graphlet, count in top_graphlets:
            print("Graphlet: {} Count: {} with algo {}".format(graphlet, count, 'brute_force_algo'))
        self.generate_graphlet_visualization('brute_force_algo', [graphlet for graphlet, freq in top_graphlets])
