from algorithm.base import BaseAlgorithm
from graph import Graphlet
from util.heap import MyHeap


class DPGraphletCounter(BaseAlgorithm):
    def __init__(self, name, graph, mode_color_map):
        super().__init__(name, graph, mode_color_map)
        self._graphlet_count_map = {}

    def count_graphlets(self, graphlet_size=3):
        # get the list of nodes sorted by name
        nodes_list = sorted(list(self.graph.get_nodes()))
        # level 1: list of node groups of size 1
        nodes_group = [[node] for node in nodes_list]
        # map of key: number of nodes, value: list of node groups
        for size in range(2, graphlet_size + 1):
            nodes_group = self.get_node_groups_of_size_n(nodes_group, size)
        for node_group in nodes_group:
            self._create_and_save_graphlet(node_group)
        return self._graphlet_count_map

    def get_node_groups_of_size_n(self, nodes_group, size):
        next_nodes_group = []
        for i in range(len(nodes_group)):
            node_group = nodes_group[i]
            node_set = set(node_group)
            included_neighbors = set()
            for node_name in node_group:
                node = self.graph.get_node(node_name)
                neighbors = node.get_undirected_neighbors()
                for neighbor in neighbors:
                    # print("neighbor", neighbor)
                    if neighbor.name not in node_set and neighbor.name not in included_neighbors:
                        # neighbor can only be added if alphabetically greater than the last node in the group
                        if neighbor.name > node_group[-1]:
                            new_node_group = node_group + [neighbor.name]
                            next_nodes_group.append(new_node_group)
                            included_neighbors.add(neighbor.name)
        return next_nodes_group

    def _create_and_save_graphlet(self, node_group):
        node_set = set()
        for node_name in node_group:
            node = self.graph.get_node(node_name)
            node_set.add(node)
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
            print("Graphlet: {} Count: {}".format(graphlet, count))
        self.generate_graphlet_visualization([graphlet for graphlet, freq in top_graphlets])
