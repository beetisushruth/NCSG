import csv
import argparse
import time

from tqdm import tqdm

from algorithm.brute_force_graphlet_counter import BruteForceGraphletCounter
from algorithm.dp_graphlet_counter import DPGraphletCounter
from algorithm.bfs_graphlet_counter import BFSGraphletCounter
from graph import Graph, Graphlet


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


def check_hash_function_collision(graphlet_map):
    # Check if there is a collision in the hash function
    overall_leaders = []
    for graphlet_key, graphlet_list in tqdm(graphlet_map.items()):
        leaders = []
        for graphlet in graphlet_list:
            # if not isomorphic to any of the leaders, add it to the leaders
            if not any([graphlet.is_isomorphic_brute_force(leader) for leader in leaders]):
                leaders.append(graphlet)
        if len(leaders) > 1:
            for i, leader in enumerate(leaders):
                print("Leader" + str(i), leader, leader.node_data_map)
                leader.visualize("leader" + str(i), {"activation": "green", "repression": "red"})
            print("Collision detected for graphlet key:", graphlet_key)
        overall_leaders.extend(leaders)
    for i in range(len(overall_leaders)):
        for j in range(i + 1, len(overall_leaders)):
            if overall_leaders[i].is_isomorphic_brute_force(overall_leaders[j], True):
                print("Collision detected in overall leaders")


def write_to_file(graphlet_map, file_name, header="Graphlet Key,Frequency"):
    with open(file_name, 'w') as file:
        file.write(header + "\n")
        for graphlet_key, graphlet_list in graphlet_map.items():
            file.write(str(graphlet_key) + "," + str(len(graphlet_list)) + "\n")


def solve(algorithms, file_name):
    # Solve the problem
    for algorithm in algorithms:
        print("Counting graphlets using", algorithm.__class__.__name__)
        start_time = time.time()
        n = input("Enter the graphlet size: ")
        graphlet_map = algorithm.count_graphlets(int(n))
        # 4209832230508172213
        for i in range(0, 8):
            print("persisting graphlets batch", i)
            algorithm.create_graphlets_persist(i)
        # check_hash_function_collision(graphlet_map)
        print("Time taken:", time.time() - start_time)
        # algorithm.display_frequent_graphlet_stats(count=10, name=file_name)
        # print("Number of graphlets:", len(graphlet_map))
        # sort the graphlets by frequency
        # graphlet_map = {k: v for k, v in sorted(graphlet_map.items(), key=lambda item: len(item[1]), reverse=True)}
        # write_to_file(graphlet_map, "./graph_output/Results_of_{}_using_{}_graphlet_size_{}.csv".format(file_name,n))


def aggregate_graphlet_count_maps(graph):
    graphlet_count_map = {}
    graphlet_obj_map = {}
    for i in range(0, 8):
        with open("graphlet_count_map_{}.txt".format(i), 'r') as file:
            for line in file:
                graphlet_key, graphlet_count, node_str = line.split(",")
                graphlet_count = int(graphlet_count)
                if graphlet_key in graphlet_count_map:
                    graphlet_count_map[graphlet_key] += graphlet_count
                else:
                    graphlet_count_map[graphlet_key] = graphlet_count
                    # strip the newline character
                    node_str = node_str[:-1]
                    nodes = node_str.split("|")
                    nodes = [graph.get_node(node) for node in nodes]
                    graphlet_obj_map[graphlet_key] = Graphlet(nodes, graph)
    # sort the graphlets by frequency
    graphlet_count_map = {k: v for k, v in sorted(graphlet_count_map.items(), key=lambda item: item[1], reverse=True)}
    with open("Results_of_df_regulon_using_DPGraphletCounter_graphlet_size_4.csv", 'w') as file:
        for graphlet_key, graphlet_count in graphlet_count_map.items():
            file.write("{},{}\n".format(graphlet_key, graphlet_count))
    keys = list(graphlet_count_map.keys())[:10]
    for index, key in enumerate(keys):
        graphlet = graphlet_obj_map[key]
        graphlet.visualize("graphlet_df_regulon_" + str(index + 1), {"activation": "green", "repression": "red"})
    return graphlet_count_map, graphlet_obj_map



def main():
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file_name", help="The name of the file to load data from", required=True)
    args = parser.parse_args()
    file_name = args.file_name if args.file_name else "thrust_human.csv"
    print("Loading data from file:", file_name)
    data = load_data(file_name)
    print("Creating graph")
    graph = create_graph(data)
    # new_graph = graph.mutate_graph(2000000)
    # new_graph.init_visualization(mode_color_map={"activation": "green", "repression": "red"}, num_edges=100)
    # new_graph.visualize("new_graph")
    print("Number of nodes:", len(graph.get_nodes()))
    print("Number of edges:", len(graph.get_edges()))
    # visualize the graph
    mode_color_map = {"activation": "green", "repression": "red"}
    graph.init_visualization(mode_color_map=mode_color_map, num_edges=100)
    graph.visualize()
    # count the graphlets
    algorithms = [DPGraphletCounter(graph, mode_color_map)]
    end_file_name = file_name.split("/")[-1].split(".")[0]
    solve(algorithms, end_file_name)


    # graphlet_count_map, graphlet_obj_map = aggregate_graphlet_count_maps(graph)



if __name__ == '__main__':
    main()
