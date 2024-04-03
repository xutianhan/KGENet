import networkx as nx
import pandas as pd
from graphviz import Digraph
from math import log2
import pickle
import numpy as np
import torch as th
import hierarchical_tree as tree

def create_graph(data_file, out_weight_file, threshold):
    # Load the MIMIC-III dataset
    df = pd.read_csv(data_file)
    # Create a dictionary that maps each ICD9 code to a set of labels that occur in the same row
    icd9_freq = {}
    icd9_occur = {}
    for _, row in df.iterrows():
        line_icds = set(str(row['LABELS']).split(';'))
        for code in line_icds:
            icd9_freq[code] = icd9_freq.get(code, 0) + 1
        icd_count = len(line_icds)
        icd_list = list(line_icds)
        for i in range(0, icd_count - 1):
            for j in range(i + 1, icd_count):
                code1 = icd_list[i]
                code2 = icd_list[j]
                icd9_occur[(code1, code2)] = icd9_occur.get((code1, code2), 0) + 1

    # Calculate the probability of each ICD9 code
    total = len(df)
    # Calculate the probability of each ICD9 code
    icd9_freq_probs = {code: count / total for code, count in icd9_freq.items()}
    # Calculate the joint probability of each pair of ICD9 codes occurring together
    icd9_joint_probs = {label: count / total for label, count in icd9_occur.items()}

    # Calculate the NPMI between each pair of ICD9 codes
    f = open(out_weight_file, 'w')
    npmi = {}
    for (icd9_code1, icd9_code2), joint_prob in icd9_joint_probs.items():
        p_icd9_code1 = icd9_freq_probs[icd9_code1]
        p_icd9_code2 = icd9_freq_probs[icd9_code2]
        denom = -log2(joint_prob)
        if denom == 0:
            npmi[(icd9_code1, icd9_code2)] = 1
        else:
            pmi = log2(joint_prob / (p_icd9_code1 * p_icd9_code2))
            npmi[(icd9_code1, icd9_code2)] = pmi / denom
        out_list = [str(icd9_code1), str(icd9_code2), str(npmi[(icd9_code1, icd9_code2)])]
        out_line = '\t'.join(out_list) + '\n'
        f.write(out_line)
    f.close()

    # Create graph
    cooccur_G = nx.Graph()
    # Add nodes and edges to the graph
    for icd, count in icd9_freq.items():
        cooccur_G.add_node(icd)
    for icd9_code1, icd9_code2 in npmi.keys():
        weight = npmi[(icd9_code1, icd9_code2)]
        if weight >= threshold:
            cooccur_G.add_edge(icd9_code1, icd9_code2, weight=weight)
    return cooccur_G


def build_complete_graph(tree_file, data_file, complete_graph_file, out_weight_file, threshold):
    parient_children, level_0, level_1, level_2, level_3, adj, node2id, hier_dicts, hier_dicts_init\
        , max_children_num  = tree.build_tree(tree_file)
    cooccur_G = create_graph(data_file, out_weight_file, threshold)
    print('number of cooccur nodes:', cooccur_G.number_of_nodes())
    print('number of cooccur edges:', cooccur_G.number_of_edges())

    hierarchical_G = tree.generate_graph(parient_children, node2id)
    hierarchical_G_sub = hierarchical_G.subgraph(cooccur_G.nodes)
    print('number of hierarchical sub nodes:', hierarchical_G_sub.number_of_nodes())
    print('number of hierarchical sub edges:', hierarchical_G_sub.number_of_edges())

    complete_G = nx.compose(cooccur_G, hierarchical_G_sub)
    print('number of complete nodes:', complete_G.number_of_nodes())
    print('number of complete edges:', complete_G.number_of_edges())
    serialize_graph(complete_graph_file, complete_G)

# def build_whole_graph(tree_file, data_file, complete_graph_file, out_weight_file, threshold):
#     parient_children, level_0, level_1, level_2, level_3, adj, node2id, hier_dicts, hier_dicts_init, max_children_num = tree.build_tree(tree_file)
#     labels_set = set(node2id.keys())  # Collecting labels from the hierarchical tree
#
#     # Generate the graph with only label nodes
#     complete_G = tree.generate_graph(parient_children, node2id, labels_set)
#
#     # Serialize the complete graph
#     serialize_graph(complete_graph_file, complete_G)

# Visualize the graph using Graphviz
def draw_graph(G, graph_name):
    dot = Digraph(comment=graph_name)
    for node in G.nodes:
        dot.node(node)
    for edge in G.edges:
        # weight = npmi[(edge[0], edge[1])]
        dot.edge(edge[0], edge[1], label='')
    dot.render(graph_name, view=True)

def serialize_graph(file, G):
    with open(file, "wb") as f:
        pickle.dump(G, f)
    return True

def reload_graph(file):
    with open(file, "rb") as f:
        G = pickle.load(f)
    return G


if __name__ == "__main__":
    tree_file = "../knowledge-data/50_attribute.txt"
    data_file = "../train-data/train_50_entities.csv"
    graph_file = "../knowledge-data/50_graph.pkl"
    weight_file = "../knowledge-data/50_npmi.txt"
    graph_name = "50_graph"
    build_complete_graph(tree_file, data_file, graph_file, weight_file, 0)

    # G = reload_graph(graph_file)
    # adj_matrix = nx.adjacency_matrix(G, weight='weight').toarray()
    # adj_matrix[np.isnan(adj_matrix)] = 0
    # in_matrix = th.from_numpy(adj_matrix)
    # print(in_matrix.size(0))
    # # draw_graph(G, graph_name)
    #
    # # data_file = "/Users/guyixun/Documents/PHD/healthcare-code/ICD-coding-baseline/mimicdata/mimic3/notes_labeled.csv"
    # # graph_file = "/Users/guyixun/Documents/PHD/healthcare-code/ICD-coding-baseline/mimicdata/icd_graph/all_graph.pkl"
    # # weight_file = "/Users/guyixun/Documents/PHD/healthcare-code/ICD-coding-baseline/mimicdata/icd_graph/all_npmi.txt"
    # # graph_name = "all_icd_graph"
    # # create_graph(data_file, graph_file, weight_file, 0)
    # # G = reload_graph(graph_file)