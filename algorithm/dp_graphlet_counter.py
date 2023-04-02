import threading
import time
from tqdm import tqdm

from algorithm.base import BaseAlgorithm
from graph import Graphlet
from util.heap import MyHeap
from functools import cmp_to_key


def custom_sort(a, b):
    """
    Custom sort function for graphlet
    :param a: the first element
    :param b: the second element
    :return: -1 if a < b, 0 if a == b, 1 if a > b
    """
    for i in range(len(a)):
        if a[i] < b[i]:
            return -1
        elif a[i] > b[i]:
            return 1
    return 0


custom_sort_key = cmp_to_key(custom_sort)


class DPGraphletCounter(BaseAlgorithm):
    def __init__(self, graph, mode_color_map):
        super().__init__(graph, mode_color_map)
        self._graphlet_count_map = {}

    def count_graphlets(self, graphlet_size=3):
        # get the list of nodes sorted by name
        nodes_list = sorted(list(self.graph.get_nodes()))
        # level 1: list of node groups of size 1
        nodes_group = set((node,) for node in nodes_list)
        # map of key: number of nodes, value: list of node groups
        for size in range(2, graphlet_size + 1):
            print("Processing node groups of size {}".format(size))
            nodes_group = self.get_node_groups_of_size_n(nodes_group)
        print("Creating graphlets, total graphlets = {}".format(len(nodes_group)))
        # use tqdm to show progress
        # split nodes_group into 4 parts and write them to files
        nodes_group_list = list(nodes_group)
        size = int(len(nodes_group_list) / 8)
        for i in range(8):
            start = i * size
            end = (i + 1) * size
            rem = len(nodes_group_list) - end
            if rem < size:
                end = len(nodes_group_list)
            with open("nodes_group_{}.txt".format(i), "w") as f:
                for node_group in nodes_group_list[start:end]:
                    f.write(",".join(node_group) + "\n")
        #
        # for i in range(4):
        #     with open("nodes_group_{}.txt".format(i), "r") as f:
        #         for line in tqdm(f):
        #             node_group = tuple(line.strip().split(","))
        #             self._create_and_save_graphlet(node_group)
        return self._graphlet_count_map

    def create_graphlets_persist(self, file_no):
        print("Processing file {}".format(file_no))
        self._graphlet_count_map = {}
        with open("nodes_group_{}.txt".format(file_no), "r") as f:
            print("Opened file nodes_group_{}.txt".format(file_no))
            for line in f:
                node_group = tuple(line.strip().split(","))
                self._create_and_save_graphlet(node_group)
        total_graphlets = 0
        with open("graphlet_count_map_{}.txt".format(file_no), "w") as f:
            for key, value in self._graphlet_count_map.items():
                nodes = [node.name for node in value[0].nodes]
                nodes = "|".join(nodes)
                total_graphlets += len(value)
                f.write("{},{},{}\n".format(key, len(value), nodes))
        print("Total graphlets = {}".format(total_graphlets))
        return self._graphlet_count_map

    def get_node_groups_of_size_n(self, nodes_group, persist_size=4):
        next_nodes_group = []
        for node_group in tqdm(nodes_group):
            node_set = set(node_group)
            for node_name in node_group:
                node = self.graph.get_node(node_name)
                neighbors = node.get_undirected_neighbors()
                for neighbor in neighbors:
                    if neighbor.name not in node_set:
                        next_node_group = tuple(sorted(node_group + (neighbor.name,)))
                        next_nodes_group.append(next_node_group)

        # next_node_group = sorted(next_nodes_group, key=custom_sort_key)
        # next_nodes_group = self.remove_duplicates(next_node_group)
        return next_nodes_group

    def remove_duplicates(self, sorted_array):
        """
        Remove duplicates from a sorted array
        :param sorted_array: the sorted array
        :return: the array with duplicates removed
        """
        if len(sorted_array) == 0:
            return []
        prev = sorted_array[0]
        result = [prev]
        for i in tqdm(range(1, len(sorted_array))):
            if sorted_array[i] != prev:
                result.append(sorted_array[i])
                prev = sorted_array[i]
        return result

    def get_node_groups_of_size_n_alternative(self, nodes_group):
        next_nodes_group = []
        for node_group in tqdm(nodes_group):
            node_set = set(node_group)
            for node_name in node_group:
                node = self.graph.get_node(node_name)
                neighbors = node.get_undirected_neighbors()
                for neighbor in neighbors:
                    if neighbor.name not in node_set and neighbor.name < node_name:
                        next_node_group = tuple(sorted(node_group + (neighbor.name,)))
                        next_nodes_group.append(next_node_group)
        return next_nodes_group

    def _create_and_save_graphlet(self, node_group):
        node_set = []
        for node_name in node_group:
            node = self.graph.get_node(node_name)
            node_set.append(node)
        g = Graphlet(node_set, self.graph)
        hash_key = hash(g)
        self._graphlet_count_map.setdefault(hash_key, [])
        self._graphlet_count_map[hash_key].append(g)

    def display_frequent_graphlet_stats(self, count=5, name='dp_algo'):
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
            print("Graphlet: {} Count: {} with algo: {}".format(graphlet, count, 'dp_algo'))
        self.generate_graphlet_visualization(name, [graphlet for graphlet, freq in top_graphlets])
