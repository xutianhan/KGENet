import networkx as nx
import numpy as np
import torch
num_nodes = 10
p = 0.5
"""
创建图：要使用 networkx 创建随机图，可以使用 erdos_renyi_graph 函数。 
此函数有两个参数：图中的节点数和任意两个节点之间的边的概率。 以下是如何创建具有 10 个节点且概率为 0.5 的随机图的示例：
"""
graph = nx.erdos_renyi_graph(num_nodes, p)

"""
计算邻接矩阵：一旦有了 networkx 图，就可以使用 adjacency_matrix 函数计算邻接矩阵。 
此函数将图形作为参数并返回邻接矩阵的稀疏矩阵表示。 以下是如何计算 networkx 图的邻接矩阵的示例：
"""
adj_matrix = nx.adjacency_matrix(graph).todense()

degrees = np.array(adj_matrix.sum(1))
pmi_matrix = np.log(np.dot(degrees.T, degrees) / np.sum(degrees) ** 2)
pmi_matrix[np.isinf(pmi_matrix)] = 0
pmi_matrix = torch.tensor(pmi_matrix, dtype=torch.float32)
