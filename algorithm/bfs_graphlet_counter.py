import heapq

from algorithm.base import BaseAlgorithm
from graph import Graphlet
from util.heap import MyHeap


class BFSGraphletCounter(BaseAlgorithm):

    def __init__(self, algo_name, graph, edge_color_map):
        super().__init__(algo_name, graph, edge_color_map)
        self._graphlet_count_map = {}
        self._processed_nodes = set()

    def _perform_path_search(self, node, target_path_length):
        """
        Perform a breadth first search on the graph and store the paths
        :param node: the node to start the search from
        :param target_path_length: the size of the node group to search for
        :return: the map of key: distance, value: list of paths
        """
        path_queue = [[node]]
        # map of key: distance, value: list of paths
        distance_to_path_map = {1: [[node]]}
        # map of key: node name, value: distance
        node_distance_map = {node.name: 1}
        while len(path_queue) > 0:
            current_path = path_queue.pop(0)
            last_node = current_path[-1]
            neighbors = last_node.get_undirected_neighbors()
            for neighbor in neighbors:
                if neighbor.name not in self._processed_nodes and \
                        (neighbor.name not in node_distance_map or
                         node_distance_map[neighbor.name] > len(
                                    current_path)):
                    new_path = current_path + [neighbor]
                    node_distance_map[neighbor.name] = len(new_path)
                    if len(new_path) != target_path_length:
                        path_queue.append(new_path)
                    if len(new_path) <= target_path_length:
                        distance_to_path_map.setdefault(len(new_path), []).append(new_path)
        return distance_to_path_map

    def _create_and_save_graphlet(self, path1, path2):
        """
        Create a graphlet from two paths and save it
        :param path1: path 1
        :param path2: path 2
        :return: None
        """
        g = Graphlet(set(path1).union(set(path2)), self._graph)
        hash_key = hash(g)
        self._graphlet_count_map.setdefault(hash_key, [])
        self._graphlet_count_map[hash_key].append(g)

    def _perform_path_combination(self, distance_to_path_map, graphlet_target_size):
        """
        Combine paths to create graphlets
        :param distance_to_path_map: map of distance to list of paths
        :param graphlet_target_size: the size of the graphlet
        :return: None
        """
        for node_count, paths in distance_to_path_map.items():
            if node_count != graphlet_target_size and node_count != 1 and len(paths) > 0:
                for i in range(node_count, graphlet_target_size):
                    if i in distance_to_path_map and len(distance_to_path_map[i]) > 0:
                        if i == node_count:
                            for index1 in range(len(paths)):
                                for index2 in range(index1 + 1, len(paths)):
                                    combined_path_length = self.get_combined_path_length(paths[index1], paths[index2])
                                    if combined_path_length == graphlet_target_size:
                                        self._create_and_save_graphlet(paths[index1], paths[index2])
                        else:
                            for path1 in paths:
                                for path2 in distance_to_path_map[i]:
                                    combined_path_length = self.get_combined_path_length(path1, path2)
                                    if combined_path_length == graphlet_target_size:
                                        self._create_and_save_graphlet(path1, path2)

        if graphlet_target_size in distance_to_path_map:
            for path in distance_to_path_map[graphlet_target_size]:
                self._create_and_save_graphlet(path, path)

    def get_combined_path_length(self, path1, path2):
        """
        Combine two paths length into one path
        :param path1:
        :param path2:
        :return: the length of the combined path
        """
        total = len(path1) + len(path2)
        common = 0
        for i in range(len(path1)):
            if i < len(path2) and path1[i] == path2[i]:
                common += 1
            else:
                break
        return total - common

    def count_graphlets(self, graphlet_size=3):
        """
        Count the graphlets in graph
        :param graphlet_size: the size of the graphlet
        :return: the map of graphlet hash to graphlet
        """
        node_list = list(self.graph.get_nodes())
        for node_name in node_list:
            node = self.graph.get_node(node_name)
            distance_to_path_map = self._perform_path_search(node, graphlet_size)
            self._perform_path_combination(distance_to_path_map, graphlet_size)
            self._processed_nodes.add(node_name)
        return self._graphlet_count_map

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




