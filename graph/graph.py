import copy
import itertools
import random

from pyvis.network import Network
import networkx as nx
from functools import cmp_to_key
import hashlib
import matplotlib.pyplot as plt


def custom_sort(a, b):
    """
    Custom sort function for graphlet
    :param a: the first element
    :param b: the second element
    :return: -1 if a < b, 0 if a == b, 1 if a > b
    """
    for i in range(len(a)):
        for j in range(len(a[i])):
            if a[i][j] < b[i][j]:
                return -1
            elif a[i][j] > b[i][j]:
                return 1
    return 0


custom_sort_key = cmp_to_key(custom_sort)


class Graphlet:
    """
    The graphlet class
    Subgraph of a graph with a fixed number of nodes
    """

    def __init__(self, nodes, graph):
        """
        Initialize the graphlet
        :param nodes: the nodes in the graphlet
        :param graph: the graph
        """
        self.nodes = nodes
        self.graph = graph
        self.mode_map = self.graph.mode_map
        self.node_data_map = {}
        self.hash_function = hashlib.sha256()

    def hash_value(self):
        """
        Hash function of the graphlet
        1) Maintain a map of node name to the value
        2) Value is list of in and out degree for each edge of the node
        eg: "A": {"B": [[1, 0], [0, 1]], "C": [[1, 0], [0, 1]]}
        3) Sort the list of values for each node
        4) Sort the list of nodes
        5) Hash the list
        """
        edge_degree_map = {}

        def set_edge_degree_information(node_name, other_name, mode_type, degree_type):
            if node_name not in edge_degree_map:
                edge_degree_map[node_name] = {}
            if other_name not in edge_degree_map[node_name]:
                edge_degree_map[node_name][other_name] = [[0 for _ in range(len(self.mode_map))],
                                                          [0 for _ in range(len(self.mode_map))]]
            edge_degree_map[node_name][other_name][degree_type][self.mode_map[mode_type]] += 1

        node_loops = {node.name: 0 for node in self.nodes}
        for node in self.nodes:
            neighbors = node.edges
            modes = neighbors.keys()
            for other in self.nodes:
                # in degree and out degree for each mode
                for mode in modes:
                    if other.name in neighbors[mode]:
                        if node.name == other.name:
                            node_loops[node.name] += 1
                        # update out degree
                        set_edge_degree_information(node.name, other.name, mode, 1)
                        # update in degree
                        # get node_edge_degree_information[other.name] and update the in degree
                        set_edge_degree_information(other.name, node.name, mode, 0)
        node_hashes = []
        for node_name, node_edge_degree_information in edge_degree_map.items():
            values = list(node_edge_degree_information.values())
            # change values to tuples
            for j in range(len(values)):
                value = values[j]
                for i in range(len(value)):
                    value[i] = tuple(value[i])
            values = [tuple(value) for value in values]
            sorted_values = sorted(values, key=custom_sort_key)
            sorted_values.append(node_loops[node_name])
            h = hash(tuple(sorted_values))
            node_hashes.append(h)
        sorted_node_hashes = tuple(sorted(node_hashes))
        return hash(sorted_node_hashes)

    def __hash__(self):
        """
        Hash the graphlet
        1. Create a map of node name to node data
        2. For each node, iterate through all the edges and maintain the in and out degree
        3. Create a list of frozenset of the node data
        4. Create a frozenset of the list of frozenset
        This will ensure that the graphlet is isomorphic and no loss of information
        :return: the hash of the graphlet
        """
        # return self.old_hash()
        # return self.new_hash()
        return self.old_hash()

    def old_hash(self):
        self.node_data_map = {}
        for node in self.nodes:
            # maintain in and out degree for each node corresponding to each mode
            # and the number of self loops for each mode
            self.node_data_map[node.name] = [[0 for _ in range(len(self.mode_map))],
                                             [0 for _ in range(len(self.mode_map))],
                                             [0 for _ in range(len(self.mode_map))]]

        # result = {1: [g1, g2, g3], 2: [g4, g5, g6], 3: [g6, g7, g8], 4:[g9, g10, g11]}
        # [g1 = l1, l2, l3, l3', l4]
        #
        # runs with O(n^2*modes) time complexity
        # where n is the number of nodes in the graphlet
        for from_node in self.nodes:
            for to_node in self.nodes:
                for mode, neighbors in from_node.edges.items():
                    if to_node.name in neighbors:
                        # maintain in and out degree for each node
                        from_node_data = self.node_data_map[from_node.name]
                        from_node_data[1][self.mode_map[mode]] += 1

                        to_node_data = self.node_data_map[to_node.name]
                        to_node_data[0][self.mode_map[mode]] += 1
                        # maintain the number of self loops for each mode
                        if from_node.name == to_node.name:
                            from_node_data[2][self.mode_map[mode]] += 1
        # convert node data map values to tuple of tuples
        for node_name, node_data in self.node_data_map.items():
            self.node_data_map[node_name] = tuple(tuple(data) for data in node_data)
        values = list(self.node_data_map.values())
        # custom sort using the custom sort function
        values.sort(key=custom_sort_key)
        # self.hash_function.update(str(values).encode())
        # return int(self.hash_function.hexdigest(), 16)
        return hash(tuple(values))

    def visualize(self, graphlet_name, edge_color_map, to_png=False):
        """
        Visualize the graphlet
        :param graphlet_name: the name of the graphlet
        :param edge_color_map: the map of edge mode to color
        :param to_png: if True, save the graphlet as a png file
        :return: None
        """
        g = nx.MultiDiGraph()
        node_names = [node.name for node in self.nodes]
        for node in self.nodes:
            for mode, neighbors in node.edges.items():
                for neighbor_name, neighbor in neighbors.items():
                    if neighbor_name in node_names:
                        # add edge without labels
                        g.add_edge(node.name, neighbor_name, color=edge_color_map[mode])
        file_path = "./graph_output/" + "size_" + str(len(self.nodes)) + "_" + graphlet_name
        if to_png:
            self._visualize_as_png(g, file_path)
        else:
            self._visualize_as_html(g, file_path)

    def _visualize_as_html(self, g, path):
        """
        Visualize the graphlet
        :param g: the graphlet
        :param path: the path to save the html file
        :return: None
        """
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="#10000000", notebook=False,
                      directed=True)
        net.from_nx(g)
        net.show(path + ".html")

    def _visualize_as_png(self, g, path):
        """
        Visualize the graphlet
        :param graphlet_name: the name of the graphlet
        :param edge_color_map: the map of edge mode to color
        :return: None
        """

        colors = nx.get_edge_attributes(g, 'color').values()
        nx.draw(g, with_labels=False, edge_color=colors)
        plt.savefig(path + ".png")
        plt.show()

    def is_isomorphic(self, other):
        """
        Check if the graphlet is isomorphic to another graphlet
        :param other: the other graphlet
        :return: True if the graphlets are isomorphic, False otherwise
        """
        # check if the number of nodes
        self_indegree_outdegree = list(self.node_data_map.values())
        other_indegree_outdegree = list(other.node_data_map.values())
        for node_data in self_indegree_outdegree:
            if node_data not in other_indegree_outdegree:
                return False
            other_indegree_outdegree.remove(node_data)
        return len(other_indegree_outdegree) == 0

    def is_isomorphic_brute_force(self, other, debug=False):
        """
        Check if the graphlet is isomorphic to another graphlet
        :param other: the other graphlet
        :return: True if the graphlets are isomorphic, False otherwise
        """
        # permutation of the nodes in the graphlet
        permutations = list(itertools.permutations(self.nodes))
        other_nodes = other.nodes
        other_nodes_map = {other_nodes[i].name: i for i in range(len(other_nodes))}
        other_info = self._get_node_info(other_nodes, other_nodes_map)
        for permutation in permutations:
            permutation_map = {permutation[i].name: i for i in range(len(permutation))}
            # get the node info for the current permutation
            permutation_info = self._get_node_info(permutation, permutation_map)
            # check if the node info is the same as the other graphlet
            if self._check_node_info(permutation_info, other_nodes, other_info, permutation_map, other_nodes_map):
                return True
        return False

    def _check_node_info(self, node_info, other_nodes, other_info, node_map, other_map):
        for node_name, edges in node_info.items():
            node_index = node_map[node_name]
            other_node = other_nodes[node_index]
            other_edges = other_info[other_node.name]
            node_edges = node_info[node_name]
            if len(node_edges) != len(other_edges):
                return False
            for mode, neighbors in node_edges.items():
                if mode not in other_edges:
                    return False
                if len(neighbors) != len(other_edges[mode]):
                    return False
                other_neighbors = other_edges[mode]
                other_edges_indexes = set(other_map[neighbor_name] for neighbor_name in other_neighbors.keys())
                for neighbor_name, neighbor in neighbors.items():
                    neighbor_index = node_map[neighbor_name]
                    if neighbor_index not in other_edges_indexes:
                        return False
        return True

    def _get_node_info(self, other_nodes, other_nodes_map):
        other_info = {}
        for other_node in other_nodes:
            # construct other edges from current other node
            other_edges = {}
            for mode, neighbors in other_node.edges.items():
                for neighbor_name, neighbor in neighbors.items():
                    if neighbor_name in other_nodes_map:
                        if mode not in other_edges:
                            other_edges[mode] = {}
                        other_edges[mode][neighbor_name] = neighbor
            other_info[other_node.name] = other_edges
        return other_info

    def __repr__(self):
        """
        String representation of the graphlet
        :return: the string representation of the graphlet
        """
        return str(self.nodes)


class Node:
    """
    Node class for graph
    Contains a name and modes of edges
    Every node must maintain a dictionary of edges
    Keys are the modes of edges (types of edges)
    Values are the nodes that are connected to the current node by the mode
    """

    def __init__(self, name):
        """
        Constructor for Node
        :param name: name of the node
        """
        self.name = name
        # to store directed edges
        self.edges = {}
        # to store directed edges as undirected edges
        self.undirected_edges = {}

    def add_edge(self, node, node_name, mode):
        """
        Add a neighbor to the current node
        :param node_name: name of the neighbor node
        :param node: the neighbor node
        :param mode: mode of the edge
        :return: None
        """
        if mode not in self.edges:
            self.edges[mode] = {node_name: node}
        else:
            self.edges[mode][node_name] = node

    def add_undirected_edge(self, node, node_name):
        """
        Add a neighbor to the current node
        :param node_name: name of the neighbor node
        :param node: the neighbor node
        :return: None
        """
        self.undirected_edges[node_name] = node

    def get_edges(self):
        """
        Get all edges of the node
        :return: list of edges
        """
        edges = []
        for mode, nodes in self.edges.items():
            for node_name, node in nodes.items():
                edges.append((self.name, node_name, mode))
        return edges

    def get_undirected_edges(self):
        """
        Get all edges of the node
        :return: list of edges
        """
        edges = []
        for node in self.undirected_edges.values():
            edges.append((self.name, node.name))
        return edges

    def get_undirected_neighbors(self):
        """
        Get all neighbors of the node
        :return: list of neighbors
        """
        neighbors = []
        for node in self.undirected_edges.values():
            neighbors.append(node)
        return neighbors

    def get_neighbors(self):
        """
        Get all neighbors of the node
        :return: list of neighbors
        """
        neighbors = []
        for mode, nodes in self.edges.items():
            for node in nodes.values():
                neighbors.append(node)
        return neighbors

    def __repr__(self):
        """
        String representation of the node
        :return: string representation of the node
        """
        return "N: " + self.name

    def __hash__(self):
        """
        Hash of the node
        :return: hash of the node
        """
        return hash(self.name)

    def __eq__(self, other):
        """
        Equality of the node
        :param other: other node
        :return: True if equal, False otherwise
        """
        return self.name == other.name


class Graph:
    def __init__(self):
        """
        Constructor for Graph
        """
        self.__graph_dict = {}
        self.__visual_graph = None
        self._mode_map = {}
        self._current_mode_count = 0

    def __register_node(self, node_name):
        """
        Register a node in the graph
        :param node_name: name of node
        :return: the node
        """
        if node_name not in self.__graph_dict:
            self.__graph_dict[node_name] = Node(node_name)
        return self.__graph_dict[node_name]

    def add_edge(self, node1_name, node2_name, mode):
        """
        Add an edge between two nodes
        :param node1_name: node 1 name
        :param node2_name: node 2 name
        :param mode: mode of the edge
        :return: None
        """
        node1 = self.__register_node(node1_name)
        node2 = self.__register_node(node2_name)
        node1.add_edge(node2, node2_name, mode)
        node1.add_undirected_edge(node2, node2_name)
        node2.add_undirected_edge(node1, node1_name)
        if mode not in self._mode_map:
            self._mode_map[mode] = self._current_mode_count
            self._current_mode_count += 1

    def get_node(self, node_name):
        """
        Get a node from the graph
        :param node_name: name of node
        :return: the node
        """
        return self.__graph_dict[node_name]

    def get_nodes(self):
        """
        Get all nodes in the graph
        :return: list of nodes
        """
        return self.__graph_dict.keys()

    def get_edges(self):
        """
        Get all edges in the graph
        :return: list of edges
        """
        edges = []
        for node in self.__graph_dict.values():
            for mode, nodes in node.edges.items():
                for key, value in nodes.items():
                    edges.append((node.name, key, mode))
        return edges

    def init_visualization(self, mode_color_map, num_edges=100):
        """
        Initialize the visualization
        :return: None
        """
        self.__visual_graph = nx.MultiDiGraph()
        edges = self.get_edges()
        for edge in edges[:num_edges]:
            self.__visual_graph.add_edge(edge[0], edge[1], color=mode_color_map[edge[2]])

    def visualize(self, name="graph"):
        """
        Visualize the graph using pyvis
        :return: None
        """
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=False,
                      directed=True)
        net.from_nx(self.__visual_graph)
        # net.show_buttons(filter_=["physics"])
        net.show("./graph_output/" + name + ".html")

    def _check_edge(self, node1, node2, mode):
        """
        Check if the edge exists
        :param node1: node 1
        :param node2: node 2
        :param mode: mode of the edge
        :return: True if edge exists, False otherwise
        """
        if node1 in self.__graph_dict:
            if mode in self.__graph_dict[node1].edges:
                if node2 in self.__graph_dict[node1].edges[mode]:
                    return True
        return False

    def get_new_graph(self, mode_color_map, edges):
        new_graph = Graph()
        for edge in edges:
            new_graph.add_edge(edge[0], edge[1], edge[2])
        new_graph.init_visualization(mode_color_map)
        return new_graph

    def mutate_graph(self, steps=100):
        """
        Mutate the graph
        :param steps: number of steps to mutate
        :return: new graph
        """
        edges = self.get_edges()

        total_edges = len(edges)
        # mutate graph using markov chain
        while steps > 0:
            # Choose two random edges
            index1, index2 = random.sample(range(len(edges)), 2)
            edge1, edge2 = edges[index1], edges[index2]
            # Check if edges share any nodes
            if len(set(edge1[:2] + edge2[:2])) != 4:
                continue
            # Flip nodes of the edges randomly
            nodes1 = [edge1[0], edge1[1]]
            choice1 = random.choice([True, False])
            if choice1:
                nodes1.reverse()
            nodes2 = [edge2[0], edge2[1]]
            choice2 = random.choice([True, False])
            if choice2:
                nodes2.reverse()
            new_edge1 = (nodes2[0], nodes1[1], edge1[2])
            if choice1:
                new_edge1 = (nodes1[1], nodes2[0], edge1[2])
            new_edge2 = (nodes1[0], nodes2[1], edge2[2])
            if choice2:
                new_edge2 = (nodes2[1], nodes1[0], edge2[2])
            # Check if new edges are already present in the graph
            if self._check_edge(*new_edge1) or self._check_edge(*new_edge2):
                continue
            edges[index1] = new_edge1
            edges[index2] = new_edge2
            steps -= 1
        return self.get_new_graph(self._mode_map, edges)

    @property
    def mode_map(self):
        return self._mode_map
