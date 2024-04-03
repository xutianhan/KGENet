import torch
import torch.nn as nn


class GGNN(nn.Module):
    def __init__(self, input_dim, time_step, in_matrix, out_matrix):
        super(GGNN, self).__init__()
        self.input_dim = input_dim
        self.time_step = time_step
        self._in_matrix = in_matrix
        self._out_matrix = out_matrix

        self.fc_w1 = nn.Linear(2 * input_dim, input_dim)
        self.fc_u1 = nn.Linear(input_dim, input_dim)
        self.fc_w2 = nn.Linear(2 * input_dim, input_dim)
        self.fc_u2 = nn.Linear(input_dim, input_dim)
        self.fc_w3 = nn.Linear(2 * input_dim, input_dim)
        self.fc_u3 = nn.Linear(input_dim, input_dim)

    def forward(self, input):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        batch_size = input.size()[0]
        input = input.view(-1, self.input_dim)
        node_num = self._in_matrix.size()[0]
        batch_aog_nodes = input.view(batch_size, node_num, self.input_dim).to(device)
        batch_in_matrix = self._in_matrix.repeat(batch_size, 1).view(batch_size, node_num, -1).to(device)
        batch_out_matrix = self._out_matrix.repeat(batch_size, 1).view(batch_size, node_num, -1).to(device)
        for t in range(self.time_step):
            # eq(15)
            av = torch.cat((torch.bmm(batch_in_matrix, batch_aog_nodes), torch.bmm(batch_out_matrix, batch_aog_nodes)), 2)
            av = av.view(batch_size * node_num, -1)

            flatten_aog_nodes = batch_aog_nodes.view(batch_size * node_num, -1)

            # eq(16.1)
            zv = torch.sigmoid(self.fc_w1(av) + self.fc_u1(flatten_aog_nodes))

            # eq(16.2)
            rv = torch.sigmoid(self.fc_w2(av) + self.fc_u2(flatten_aog_nodes))

            #eq(16.3)
            hv = torch.tanh(self.fc_w3(av) + self.fc_u3(rv * flatten_aog_nodes))

            # eq(16.4)
            flatten_aog_nodes = (1 - zv) * flatten_aog_nodes + zv * hv
            batch_aog_nodes = flatten_aog_nodes.view(batch_size, node_num, -1)
        return batch_aog_nodes


