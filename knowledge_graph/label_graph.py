import networkx as nx
from graphviz import Digraph
import pickle
import knowledge_graph.hierarchical_tree as tree
import pandas as pd
import csv

def generate_relation_graph(node_file, relation_file):
    icd_list = []
    with open(node_file, 'r', encoding='utf-8') as node_f:
        for line in node_f:
            line = line.strip()
            array = line.split('\t')
            if len(array) < 1:
                continue
            icd_code = array[0]
            icd_list.append(icd_code)
    # 创建一个空的有向图
    G = nx.DiGraph()
    G.add_nodes_from(icd_list)
    # 读取relation文件构建relation
    with open(relation_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # 跳过标题行
        for row in reader:
            head_entity = row[0]
            tail_entity = row[2]
            relation = row[4]
            G.add_edge(head_entity, tail_entity, relation=relation)
    return G

def save_triplets_to_csv(graph, output_file):
    triplets = []
    for edge in graph.edges(data=True):
        head_entity = edge[0]
        tail_entity = edge[1]
        weight = edge[2]['weight']
        triplets.append((head_entity, weight, tail_entity))
    df = pd.DataFrame(triplets, columns=['Head_Entity', 'Weight', 'Tail_Entity'])
    df.to_csv(output_file, index=False)
    print("Triplets saved to", output_file)


def build_complete_graph(node_file, relation_file, complete_graph_file):
    parient_children, level_0, level_1, level_2, level_3, adj, node2id, hier_dicts, hier_dicts_init\
        , max_children_num  = tree.build_tree(node_file)
    relation_G = generate_relation_graph(node_file, relation_file)
    print('number of relation nodes:', relation_G.number_of_nodes())
    print('number of relation edges:', relation_G.number_of_edges())

    hierarchical_G = tree.generate_hierarchical_graph(parient_children, node2id)
    hierarchical_G_sub = hierarchical_G.subgraph(relation_G.nodes)
    print('number of hierarchical sub nodes:', hierarchical_G_sub.number_of_nodes())
    print('number of hierarchical sub edges:', hierarchical_G_sub.number_of_edges())

    complete_G = nx.compose(relation_G, hierarchical_G_sub)
    print('number of complete nodes:', complete_G.number_of_nodes())
    print('number of complete edges:', complete_G.number_of_edges())
    serialize_graph(complete_graph_file, complete_G)

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
        assert isinstance(G, nx.DiGraph), "Reloaded graph is not a DiGraph"
    return G


if __name__ == "__main__":
    node_file = "../knowledge-data/50_attribute.txt"
    relation_file = "../knowledge-data/50_relation_filtered.csv"
    output_graph_file = "../knowledge-data/50_graph.pkl"
    build_complete_graph(node_file, relation_file, output_graph_file)
    G = reload_graph(output_graph_file)