import sys
sys.path.append('../')

import torch as th
import torch.nn as nn
import torch.nn.functional as F
from networks.attribute_encoder import AttributeEncoder
from networks.ehr_encoder import EHREncoder

from networks.ggnn import GGNN
import networkx as nx
import knowledge_graph.label_graph as lg
import numpy as np
from torch.autograd import Variable

class KGENet(nn.Module):

    def __init__(self, label_emb_model_name, ehr_emb_model_name, label_attr_file,
                 embedding_size, mid_size, num_classes, label_graph, theta, time_step):
        super(KGENet, self).__init__()
        # Init Label Attribute Embedding
        self.label_encoder = AttributeEncoder(label_emb_model_name)

        # Init EHR embedding
        self.ehr_encoder = EHREncoder(ehr_emb_model_name)

        self.embedding_size = embedding_size
        self.num_classes = num_classes

        self.W1 = nn.Linear(embedding_size, mid_size)
        self.W2 = nn.Linear(mid_size, 1)
        # label embeddings
        self.label_embeddings = self.label_encoder.init_all_label_embeddings(label_attr_file) # (num_class, embedding_size)

        # Instantiate GGNN
        self.time_step = time_step
        # reload label graph
        self.graph_file = label_graph

        G = lg.reload_graph(self.graph_file)
        adj_matrix = nx.adjacency_matrix(G, weight=theta).toarray()

        # Replace missing values with 0
        adj_matrix[np.isnan(adj_matrix)] = 0
        # convert ndarray to tensor
        self.in_matrix, self.out_matrix = self.load_matrix(adj_matrix)

        self.graph_net = GGNN(input_dim=2 * self.embedding_size,
                              time_step=self.time_step,
                              in_matrix=self.in_matrix,
                              out_matrix=self.out_matrix)
        # Instantiate FCN for classifier
        self.fcs = nn.ModuleList([nn.Linear(4 * self.embedding_size, 1) for _ in range(self.num_classes)])

    def forward(self, x):
        H = self.ehr_encoder.compute_ehr_embedding(x) #(batch_size, sequence_length, embedding_size)
        # label attention
        T = th.tanh(self.W1(H)) # (batch_size, sequence_length, mid_size)
        label_attention_scores = F.softmax(self.W2(T), dim=1) # (batch_size, sequence_length, 1)
        label_attention_trans = label_attention_scores.transpose(1, 2) #(batch_size, 1, sequence_length)
        label_attention_output = th.matmul(label_attention_trans, H) # (batch_size, 1, embedding_size)

        # cross-attention
        query = self.label_embeddings.weight.repeat(x.size(0), 1, 1) # (batch_size, num_class, embedding_size)
        key = H.transpose(1, 2) # (batch_size, embedding_size, sequence_length)
        value = H # (batch_size, sequence_length, embedding_size)
        cross_attention_scores = th.matmul(query, key) # (batch_size, num_class, sequence_length)
        cross_attention_weights = F.softmax(cross_attention_scores, dim=-1) # (batch_size, num_class, sequence_length)
        cross_attention_output = th.matmul(cross_attention_weights, value) # (batch_size, num_class, embedding_size)
        num_class = cross_attention_output.size(1)

        # 将 label_attention_output 复制 num_class 次
        label_attention_output_expanded = label_attention_output.expand(-1, num_class, -1)  # (batch_size, num_class, embedding_size)

        # get attention features
        attn_feature_all = th.cat([label_attention_output_expanded, cross_attention_output], dim=-1) # (batch_size, num_class, 2 * embedding_size)

        # Compute graph feature
        graph_feature = self.graph_net.forward(attn_feature_all)
        # concatenate features, output B X M X d_e
        out_feature = th.cat((attn_feature_all, graph_feature), dim=-1)
        # classifier B X M
        outputs = th.zeros((out_feature.size(0), self.num_classes))
            # .to(self.device)
        outputs = outputs.type_as(out_feature)
        for code, fc in enumerate(self.fcs):
            outputs[:, code:code + 1] = fc(out_feature[:, code, :])
        return outputs, cross_attention_weights


    def load_matrix(self, adjacency_matrix):
        in_matrix, out_matrix = adjacency_matrix.astype(np.float32), adjacency_matrix.T.astype(np.float32)
        in_matrix = Variable(th.from_numpy(in_matrix), requires_grad=False)
        out_matrix = Variable(th.from_numpy(out_matrix), requires_grad=False)
        return in_matrix, out_matrix
