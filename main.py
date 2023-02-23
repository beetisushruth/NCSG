import csv
import argparse
import time

from algorithm.bfs_graphlet_counter import BFSGraphletCounter
from brute_force_graphlet_counter import count_graphlets
from graph import Graph


def load_data(file_name):
    # Load data from the file
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        # Skip the header
        next(reader)
        data = list(reader)
    return data


def create_graph(data):
    # Create the graph
    graph = Graph()
    for row in data:
        if row[2] != 'unknown':
            graph.add_edge(row[0], row[1], row[2])
    return graph


def main():
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file_name", help="The name of the file to load data from", required=True)
    args = parser.parse_args()
    file_name = args.file_name if args.file_name else "thrust_human.csv"
    print("Loading data from file:", file_name)
    data = load_data(file_name)
    print("Data loaded successfully")
    print("Creating graph")
    graph = create_graph(data)
    print("Graph created successfully")
    print("Number of nodes:", len(graph.get_nodes()))
    print("Number of edges:", len(graph.get_edges()))
    # visualize the graph
    mode_color_map = {"activation": "green", "repression": "red"}
    graph.init_visualization(mode_color_map=mode_color_map, num_edges=100)
    graph.visualize()
    # count the graphlets
    algorithm = BFSGraphletCounter("BFS Graphlet Counter", graph, mode_color_map)
    n = input("Enter the number of graphlets to count: ")
    while not n.isdigit():
        n = input("Enter the number of graphlets to count: ")
    n = int(n)
    start_time = time.time()
    graphlet_map = algorithm.count_graphlets(n)
    algorithm.display_frequent_graphlet_stats()
    print("Time taken:", time.time() - start_time)
    print("Number of graphlets:", len(graphlet_map))


if __name__ == '__main__':
    main()
