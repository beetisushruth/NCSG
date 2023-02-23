from graph import Graphlet


def bfs_search(node, node_group_size, graph, graphlet_count_map, processed_nodes):
    """
    Perform a breadth first search on the graph
    :param node: the node to start the search from
    :param node_group_size: the size of the node group to search for
    :param graph: the graph to search on
    :param graphlet_count_map: the map to store the graphlets and their counts
    :param processed_nodes: the set of nodes that have already been processed
    """
    # perform path search and store the paths
    path_queue = [[node]]
    distance_to_path_map = {1: [[node]]}
    node_distance_map = {node.name: 1}
    while len(path_queue) > 0:
        current_path = path_queue.pop(0)
        last_node = current_path[-1]
        neighbors = last_node.get_undirected_neighbors()
        for neighbor in neighbors:
            if neighbor.name not in processed_nodes and (neighbor.name not in node_distance_map or
                                                         node_distance_map[neighbor.name] > len(current_path)):
                new_path = current_path + [neighbor]
                node_distance_map[neighbor.name] = len(new_path)
                if len(new_path) != node_group_size:
                    path_queue.append(new_path)
                if len(new_path) <= node_group_size:
                    distance_to_path_map.setdefault(len(new_path), []).append(new_path)

    # perform path combination
    for node_count, paths in distance_to_path_map.items():
        if node_count != node_group_size and node_count != 1 and len(paths) > 0:
            for i in range(node_count, node_group_size):
                if i in distance_to_path_map and len(distance_to_path_map[i]) > 0:
                    if i == node_count:
                        for index1 in range(len(paths)):
                            for index2 in range(index1 + 1, len(paths)):
                                path_length = path_combination(paths[index1], paths[index2])
                                if path_length == node_group_size:
                                    g = Graphlet(set(paths[index1]).union(set(paths[index2])), graph)
                                    hash_key = hash(g)
                                    graphlet_count_map.setdefault(hash_key, [])
                                    graphlet_count_map[hash_key].append(g)
                    else:
                        for path1 in paths:
                            for path2 in distance_to_path_map[i]:
                                path_length = path_combination(path1, path2)
                                if path_length == node_group_size:
                                    g = Graphlet(set(path1).union(set(path2)), graph)
                                    hash_key = hash(g)
                                    graphlet_count_map.setdefault(hash_key, [])
                                    graphlet_count_map[hash_key].append(g)

    if node_group_size in distance_to_path_map:
        for path in distance_to_path_map[node_group_size]:
            g = Graphlet(set(path), graph)
            hash_key = hash(g)
            graphlet_count_map.setdefault(hash_key, [])
            graphlet_count_map[hash_key].append(g)


def count_graphlets_bfs(graph, node_group_size=3):
    """
    Count the graphlets in the graph
    :param graph: the graph to count the graphlets in
    :param node_group_size: the size of the node group to search for
    :return:   the map of graphlet hash to graphlet
    """
    nodes = list(graph.get_nodes())
    graphlet_count_map = {}
    processed_nodes = set()
    for node_name in nodes:
        node = graph.get_node(node_name)
        bfs_search(node, node_group_size, graph, graphlet_count_map, processed_nodes)
        processed_nodes.add(node_name)
    counts = []
    for graphlet_hash, graphlets in graphlet_count_map.items():
        counts.append(len(graphlets))
    return graphlet_count_map


def path_combination(path1, path2):
    """
    Combine two paths into one path
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


def count_graphlets(graph):
    """
    Count the graphlets in the graph
    :param graph: the graph to count the graphlets in
    :return:  the map of graphlet hash to graphlet
    """
    graphlet_size = 4
    graphlet_count_map = count_graphlets_bfs(graph, graphlet_size)
    counter = 0
    edge_color_map = {'activation': 'green', 'repression': 'red'}
    # sort graphlet_count_map by the number of graphlets
    graphlet_count_map = {k: v for k, v in sorted(graphlet_count_map.items(),
                                                  key=lambda item: len(item[1]), reverse=True)}
    for graphlet_hash, graphlets in graphlet_count_map.items():
        print(graphlets[0], len(graphlets))
        graphlets[0].visualize("graphlet"+str(counter), edge_color_map)
        counter += 1
        if counter == 5:
            break
    print(str(graphlet_size)+"-graphlets: ", len(graphlet_count_map))
