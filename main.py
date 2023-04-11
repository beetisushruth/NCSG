import csv
import argparse
import json
import logging
import os.path
import time
from pathlib import Path

from tqdm import tqdm

from algorithm.base import BaseAlgorithm
from graph import Graph, Graphlet
from util.logger_util import LoggerUtil

logger = LoggerUtil.get_logger("main")


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
        for graphlet_key, graphlet_info in graphlet_map.items():
            file.write(str(graphlet_key) + "," + str(graphlet_info[1]) + "\n")


def solve(algorithms, graphlet_size, file_name, folder_name):
    # Solve the problem
    for algorithm in algorithms:
        logger.info("Counting graphlets using %s", algorithm.__class__.__name__)
        start_time = time.time()
        graphlet_map = algorithm.count_graphlets(graphlet_size)
        # check_hash_function_collision(graphlet_map)
        logger.info("Time taken: %s seconds", time.time() - start_time)
        algorithm.display_frequent_graphlet_stats(count=10, name=file_name)
        logger.info("Number of unique graphlets: %s", len(graphlet_map))
        # sort the graphlets by frequency
        graphlet_map = {k: v for k, v in sorted(graphlet_map.items(), key=lambda item: item[1][1], reverse=True)}
        path = os.path.join(folder_name, file_name + "_" + algorithm.__class__.__name__ + "_graphlets_size_" + str(graphlet_size))
        write_to_file(graphlet_map, path + ".csv")


def get_algorithms_to_run(algorithms_available, algorithms_to_run):
    classes = BaseAlgorithm.__subclasses__()
    classes = {cls.__name__: cls for cls in classes}
    algorithms = []
    for algorithm in algorithms_to_run:
        if algorithm in algorithms_available:
            algorithms.append(classes[algorithm])
        else:
            logger.warning("Algorithm %s is not available", algorithm)
    return algorithms


def main():
    # read config file
    config_file = "config.json"
    with open(config_file, 'r') as file:
        config = json.load(file)

    # creating the graph
    input_file = config["input_file"]
    mode_color_map = {"activation": "green", "repression": "red"}
    sample_size = config["sample_size"]
    data = load_data(input_file)[:sample_size] if config["use_sampling"] else load_data(input_file)
    graph = create_graph(data)
    logger.info("Graph created from file: %s", input_file)
    logger.info("Number of nodes: %s", graph.get_num_nodes())
    logger.info("Number of edges: %s", graph.get_num_edges())

    # visualize the whole graph according to the config
    natural_file_name = Path(input_file).stem
    if config["output"]["visualizations"]["generate"]:
        vis_config = config["output"]["visualizations"]
        graph.init_visualization(mode_color_map, vis_config["graph_size"])
        path = os.path.join(vis_config["folder"], natural_file_name + "_graph")
        graph.visualize(path)

    # algorithms to run
    algorithms = [cls(graph, mode_color_map) for cls in
                  get_algorithms_to_run(config["algorithms_available"], config["algorithms_to_run"])]
    solve(algorithms, config["graphlet_size"], natural_file_name, config["output"]["visualizations"]["folder"])


if __name__ == '__main__':
    main()
