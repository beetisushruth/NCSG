import networkx as nx
from pyvis.network import Network


def read_file(file_name):
    # Read the file
    edges = []
    with open(file_name, 'r') as file:
        lines = file.readlines()
        for line in lines:
            vertices = line.split()
            edges.append((vertices[0], vertices[1]))
    return edges


def create_graph(edges):
    # Create the graph
    graph = nx.Graph()
    graph.add_edges_from(edges)
    return graph


def visualize(graph):
    # Visualize the graph
    net = Network(notebook=False)
    net.from_nx(graph)
    net.show("test.html")


if __name__ == '__main__':
    # Read the file
    file_name = "/Users/sushruth/Downloads/nodes.txt"
    edges = read_file(file_name)
    # Create the graph
    graph = create_graph(edges)
    # Visualize the graph
    visualize(graph)
