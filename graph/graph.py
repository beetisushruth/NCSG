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

    # CURRENT HASH FUNCTION IN USE
    def node_edge_degree_hash(self):
        """
        Calculate the node edge degree hash of the graphlet
        For example: consider a graphlet with 3 nodes and 2 modes
        A, B, repression
        B, C, activation
        A, C, repression
        C, C, repression

        A has an out degree of 2 (1 repression to B, 1 repression to C)
        B has an in degree of 1 (1 repression from A)
        B has an out degree of 1 (1 activation to C)
        C has an in degree of 3 (1 repression from A, 1 activation from B, 1 repression from C)
        C has an out degree of 1 (1 repression to C)

        A's degree information is stored as a dictionary of other nodes and their degree information
        A: {B: [[0, 0], [1, 0]], C: [[0, 0], [1, 0]]}  # 0th index is in degree, 1st index is out degree
        Edge between A and B is a list of lists, where the first list is in degree information and the second list is
        out degree information
        The first element of the list is the number of activation edges, the second element is the number of repression edges

        The entire edge degree information is stored as a dictionary of nodes and their edge degree information
        {A: {B: [[0, 0], [1, 0]], C: [[0, 0], [1, 0]]}, B: {A: [[1, 0], [0, 0]], C: [[0, 0], [1, 0]]},
        C: {A: [[1, 0], [0, 0]], B: [[0, 0], [1, 0]], C: [[1, 0], [1, 0]]}}

        A node hash is calculated by sorting the edge degree information of the node and hashing the sorted list
        Self loops are counted and added to the node hash as well

        :return: the node edge degree hash
        """
        edge_degree_map = {}  # Initialize an empty dictionary to store edge degree information
        # Initialize a dictionary to store self loop count for each node
        node_loops = {node.name: 0 for node in self.nodes}

        # Define a function to update edge degree information
        def set_edge_degree_information(node_name, other_name, mode_type, degree_type):
            edge_degree_map.setdefault(node_name, {}).setdefault(other_name, [[0] * len(self.mode_map),
                                                                              [0] * len(self.mode_map)])
            edge_degree_map[node_name][other_name][degree_type][self.mode_map[mode_type]] += 1

        # Loop through all nodes and their neighbors to update edge degree information
        for node in self.nodes:
            neighbors = node.edges
            modes = neighbors.keys()
            for other in self.nodes:
                for mode in modes:
                    if other.name in neighbors[mode]:
                        if node.name == other.name:
                            node_loops[node.name] += 1
                        set_edge_degree_information(node.name, other.name, mode, 1)  # Update out degree
                        set_edge_degree_information(other.name, node.name, mode, 0)  # Update in degree

        node_hashes = []  # Initialize a list to store node hashes
        # print(edge_degree_map)
        # Loop through edge degree information to calculate node hashes
        for node_name, node_edge_degree_information in edge_degree_map.items():
            values = [self.convert_to_tuple(value) for value in node_edge_degree_information.values()]
            sorted_values = sorted(values, key=lambda x: custom_sort_key(x))  # Sort the list of values for each node
            sorted_values.append(node_loops[node_name])  # Add loop count to the sorted values
            h = hash(tuple(sorted_values))  # Hash the sorted values
            node_hashes.append(h)

        sorted_node_hashes = tuple(sorted(node_hashes))  # Sort the node hashes
        return hash(sorted_node_hashes)  # Return the hash value of the sorted node hashes

    def convert_to_tuple(self, ds):
        """
        util function to convert the nested list to a nested tuple
        """
        if len(ds) == 0:
            return tuple()
        if isinstance(ds[0], list):
            return tuple(self.convert_to_tuple(l) for l in ds)
        return tuple(ds)

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
        return self.node_edge_degree_hash()

    # OLD HASH FUNCTION - NOT IN USE
    # SIMPLER THAN NODE_EDGE_DEGREE_HASH BUT CAUSES LOSS OF INFORMATION AND HENCE COLLISIONS
    def node_combined_degree_hash(self):
        """
        Calculate the node combined degree hash of the graphlet
        :return: the node combined degree hash
        """
        self.node_data_map = {}
        for node in self.nodes:
            # maintain in and out degree for each node corresponding to each mode
            # and the number of self loops for each mode
            self.node_data_map[node.name] = [[0 for _ in range(len(self.mode_map))],
                                             [0 for _ in range(len(self.mode_map))],
                                             [0 for _ in range(len(self.mode_map))]]
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
        return hash(tuple(values))

    def visualize(self, file_path, edge_color_map, to_png=False):
        """
        Visualize the graphlet
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
        :param debug: if True, print debug information
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
        """
        Check if the node info is the same as the other graphlet
        :param node_info: the node info of the current permutation
        :param other_nodes: the nodes of the other graphlet
        :param other_info: the node info of the other graphlet
        :param node_map: the map of node name to index in the current permutation
        :param other_map: the map of node name to index in the other graphlet
        :return: True if the node info is the same as the other graphlet, False otherwise
        """
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
        """
        Get the node info of the other graphlet
        :param other_nodes: the nodes of the other graphlet
        :param other_nodes_map: the map of node name to index in the other graphlet
        :return: the node info of the other graphlet
        """
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

    def visualize(self, path="graph"):
        """
        Visualize the graph using pyvis
        :return: None
        """
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=False,
                      directed=True)
        net.from_nx(self.__visual_graph)
        # net.show_buttons(filter_=["physics"])
        net.show(path + ".html")

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
        # mutate graph using markov chain
        while steps > 0:
            # Choose two random edges
            index1, index2 = random.sample(range(len(edges)), 2)
            edge1, edge2 = edges[index1], edges[index2]
            # Check if edges share any nodes
            if len(set(edge1[:2] + edge2[:2])) != 4:
                continue
            # check if both edges are of same mode
            if edge1[2] != edge2[2]:
                continue
            u, v, mode = edge1
            x, y, mode = edge2
            # after swapping new edge will be (u, y, mode) and (x, v, mode)
            # so check if new edges are already present in the graph
            if self._check_edge(u, y, mode) or self._check_edge(x, v, mode):
                continue
            edges[index1] = (u, y, mode)
            edges[index2] = (x, v, mode)
            steps -= 1
        return self.get_new_graph(self._mode_map, edges)

    def sample(self, num_nodes):
        """
        Sample the graph
        :param num_nodes: number of nodes to sample
        :return: new graph
        """
        nodes = self.get_nodes()
        sampled_nodes = set(random.sample(nodes, num_nodes))
        edges = self.get_edges()
        sampled_edges = []
        for edge in edges:
            if edge[0] in sampled_nodes and edge[1] in sampled_nodes:
                sampled_edges.append(edge)
        return self.get_new_graph(self._mode_map, sampled_edges)

    @property
    def mode_map(self):
        """
        Get the mode map
        :return: mode map
        """
        return self._mode_map

    def get_num_edges(self):
        """
        Get the number of edges in the graph
        :return: number of edges
        """
        return len(self.get_edges())

    def get_num_nodes(self):
        """
        Get the number of nodes in the graph
        :return: number of nodes
        """
        return len(self.get_nodes())
