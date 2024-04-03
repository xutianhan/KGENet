import sys
sys.path.append('../')
import hierarchical_tree
import os
import pickle


label_type = '50'
label_dir = '../knowledge-data'

parient_children, level_0, level_1, level_2, level_3, adj, node2id, hier_dicts, hier_dicts_init, max_children_num \
    = hierarchical_tree.build_tree(os.path.join(label_dir, '50_attribute.txt'))
# 构建图
graph = hierarchical_tree.generate_graph(parient_children, node2id) #edges, nodes
# 序列化图
with open(os.path.join(label_dir, 'graph_%s.pkl' % label_type), 'wb') as f:
    pickle.dump(graph, f, protocol=0)

# 序列化标签结构
with open(os.path.join(label_dir, 'struct_%s.pkl' % label_type), 'wb') as f:
    pickle.dump(
        [parient_children, level_0, level_1, level_2, level_3, adj, node2id, hier_dicts, hier_dicts_init,
         max_children_num], f, protocol=0)
