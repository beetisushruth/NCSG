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


def solve(algorithm, graphlet_size, execution_name):
    # Solve the problem
    logger.info("Counting graphlets using %s", algorithm.__class__.__name__)
    start_time = time.time()
    graphlet_map = algorithm.count_graphlets(graphlet_size)
    # check_hash_function_collision(graphlet_map)
    logger.info("Time taken: %s seconds", time.time() - start_time)
    algorithm.display_frequent_graphlet_stats(count=10, name=execution_name)
    logger.info("Number of unique graphlets: %s", len(graphlet_map))
    # sort the graphlets by frequency
    graphlet_map = {k: v for k, v in sorted(graphlet_map.items(), key=lambda item: item[1][1], reverse=True)}
    return graphlet_map


def get_algorithm_class(algorithm_to_use):
    """
    Get the algorithm object from the algorithm name
    :param algorithm_to_use: the name of the algorithm
    :return: the algorithm class
    """
    classes = {cls.__name__: cls for cls in BaseAlgorithm.__subclasses__()}
    if algorithm_to_use in classes:
        return classes[algorithm_to_use]
    return None


def run_graphlet_counting(graph, graphlet_size, sample_size, num_of_samples, markov_steps,
                          num_of_markov_graphs, algorithm_class, mode_color_map):
    # sample the graph
    aggregate_graphlet_map = {}
    for i in range(num_of_markov_graphs):
        logger.info("Generating markov graph %s with %s steps", i + 1, markov_steps)
        graph = graph.mutate_graph(markov_steps)
        for j in range(num_of_samples):
            graph_sample = graph.sample(sample_size)
            logger.info("Sampling graph %s of size %s", j + 1, sample_size)
            algorithm = algorithm_class(graph_sample, mode_color_map)
            graphlet_map = solve(algorithm, graphlet_size, "markov_graph_" + str(i + 1) + "_sample_" + str(j + 1))
            for graphlet_key, graphlet_info in graphlet_map.items():
                if graphlet_key in aggregate_graphlet_map:
                    value = aggregate_graphlet_map[graphlet_key]
                    aggregate_graphlet_map[graphlet_key] = (value[0], value[1] + graphlet_info[1])
                else:
                    aggregate_graphlet_map[graphlet_key] = graphlet_info
    for graphlet_key, graphlet_info in aggregate_graphlet_map.items():
        aggregate_graphlet_map[graphlet_key] = (graphlet_info[0], graphlet_info[1] / (num_of_markov_graphs * num_of_samples))
    # sort the graphlets by frequency descending
    aggregate_graphlet_map = {k: v for k, v in sorted(aggregate_graphlet_map.items(), key=lambda item: item[1][1], reverse=True)}
    return aggregate_graphlet_map


def main():
    # read config file
    config_file = "config.json"
    with open(config_file, 'r') as file:
        config = json.load(file)

    # configurations
    input_file = config["input_file"]
    algorithm_to_use = config["algorithm_to_use"]
    graphlet_size = config["graphlet_size"]
    sample_size = config["sample_size"]
    use_sampling = config["use_sampling"]
    num_of_samples = config["num_of_samples"]
    markov_steps = config["markov_steps"]
    use_markov_graph_generation = config["use_markov_graph_generation"]
    num_of_markov_graphs = config["num_of_markov_graphs"]
    output_config = config["output"]
    generate_csv_output = output_config["csv_output"]["generate"]
    csv_output_folder = output_config["csv_output"]["folder"]
    generate_graph_visualizations = output_config["visualizations"]["generate"]
    visualization_folder = output_config["visualizations"]["folder"]
    mode_color_map = output_config["visualizations"]["mode_colors"]

    # load data
    data = load_data(input_file)
    graph = create_graph(data)
    logger.info("Graph created from file: %s", input_file)
    logger.info("Number of nodes: %s", graph.get_num_nodes())
    logger.info("Number of edges: %s", graph.get_num_edges())

    # setup
    num_of_samples = num_of_samples if use_sampling else 1
    sample_size = sample_size if use_sampling else graph.get_num_nodes()
    num_of_markov_graphs = num_of_markov_graphs if use_markov_graph_generation else 1
    markov_steps = markov_steps if use_markov_graph_generation else 0
    logger.info("Using sampling and markov generation leads to an average approximation of the graphlet counts of all "
                "iterations")
    # visualize the whole graph according to the config
    readable_file_name = Path(input_file).stem

    # algorithms to run
    algorithm = get_algorithm_class(algorithm_to_use)
    if not algorithm:
        logger.info("No valid algorithm provided")
        return
    aggregate_graphlet_map = run_graphlet_counting(graph, graphlet_size, sample_size, num_of_samples, markov_steps,
                                                   num_of_markov_graphs, algorithm, mode_color_map)
    if generate_csv_output:
        logger.info("Writing graphlet counts to csv file")
        name = "Results_graphlet_size_{}_{}_{}_sampling_{}_{}_markov_{}_{}".format(readable_file_name, graphlet_size,
                                                                                   algorithm.__name__,
                                                                                   use_sampling,
                                                                                   sample_size,
                                                                                   use_markov_graph_generation,
                                                                                   markov_steps,
                                                                                   num_of_markov_graphs)
        path = os.path.join(csv_output_folder, name + ".csv")
        write_to_file(aggregate_graphlet_map, path)
    if generate_graph_visualizations:
        logger.info("Generating graph visualizations")
        results = list(aggregate_graphlet_map.items())[:10]
        for index, (graphlet_key, graphlet_info) in enumerate(results):
            graphlet = graphlet_info[0]
            name = "{}_graphlet_size_{}_{}_{}_sampling_{}_{}_markov_{}_{}".format(index + 1, graphlet_size,
                                                                                  readable_file_name,
                                                                                  algorithm.__name__,
                                                                                  use_sampling,
                                                                                  sample_size,
                                                                                  use_markov_graph_generation,
                                                                                  markov_steps)
            path = os.path.join(visualization_folder, name + ".html")
            graphlet.visualize(path, mode_color_map)


if __name__ == '__main__':
    main()
