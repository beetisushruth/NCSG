from pyvis.network import Network
import networkx as nx


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
        # self.nodes = sorted(nodes, key=lambda node: node.name)
        self.graph = graph

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
        node_data_map = {}
        for node in self.nodes:
            node_data_map[node.name] = {}
        # runs with O(n^2*modes) time complexity
        # where n is the number of nodes in the graphlet
        for from_node in self.nodes:
            for to_node in self.nodes:
                for mode, neighbors in from_node.edges.items():
                    if to_node.name in neighbors:
                        # maintain in and out degree for each node
                        from_node_data = node_data_map[from_node.name]
                        from_node_data.setdefault(mode, 0)
                        from_node_data[mode] += 1

                        to_node_data = node_data_map[to_node.name]
                        to_node_data.setdefault(mode, 0)
                        to_node_data[mode] += 1
        nodes_list = [frozenset(node_data.items()) for node_data in node_data_map.values()]
        graphlet_hash = hash(frozenset(nodes_list))
        return graphlet_hash

    def visualize(self, graphlet_name, edge_color_map):
        """
        Visualize the graphlet
        :param graphlet_name: the name of the graphlet
        :param edge_color_map: the map of edge mode to color
        :return: None
        """
        g = nx.DiGraph()
        node_names = [node.name for node in self.nodes]
        for node in self.nodes:
            for mode, neighbors in node.edges.items():
                for neighbor_name, neighbor in neighbors.items():
                    if neighbor_name in node_names:
                        g.add_edge(node.name, neighbor_name, color=edge_color_map[mode])
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=False,
                      directed=True)
        net.from_nx(g)
        net.show("./graph_output/"+str(len(self.nodes))+"_"+graphlet_name + ".html")

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
            for node in nodes:
                edges.append((self.name, node.name, mode))
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
        self.__visual_graph = nx.DiGraph()
        edges = self.get_edges()
        for edge in edges[:num_edges]:
            self.__visual_graph.add_edge(edge[0], edge[1], color=mode_color_map[edge[2]])

    def visualize(self):
        """
        Visualize the graph using pyvis
        :return: None
        """
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=False,
                      directed=True)
        net.from_nx(self.__visual_graph)
        # net.show_buttons(filter_=["physics"])
        net.show("./graph_output/graph.html")
