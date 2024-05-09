import torch
import torch.nn as nn
import numpy as np
import torch.nn.functional as F
from torch_geometric.nn import GATConv, global_mean_pool,BatchNorm

class GAT(nn.Module):
    def __init__(self, embedding_size, hidden_dims, num_layers = 3, num_classes = 64,dropout=0.1):
        super(GAT, self).__init__()
        self.time_linear = nn.Linear(4, 12)
        self.convs = nn.ModuleList()
        self.batch_norms = nn.ModuleList()
        if num_layers <= 1:
            conv_0 = GATConv(in_channels=embedding_size, out_channels=embedding_size, dropout=dropout)
            bn_0 = BatchNorm(embedding_size)
            self.convs.append(conv_0)
            self.batch_norms.append(bn_0)
        else:
            conv_0 = GATConv(in_channels=embedding_size, out_channels=embedding_size, heads=3, dropout=dropout)
            conv_1 = GATConv(in_channels=embedding_size * 3, out_channels=embedding_size,
                                heads=1, dropout=dropout)
            bn_0 = BatchNorm(embedding_size * 3)
            bn_1 = BatchNorm(embedding_size)

            self.convs.append(conv_0)
            self.batch_norms.append(bn_0)

            num_layers -= 2
            if num_layers > 0:
                for i in range(num_layers):
                    conv = GATConv(in_channels=embedding_size * 3,
                                    out_channels=embedding_size, heads=3)
                    bn = BatchNorm(embedding_size * 3)
                    self.convs.append(conv)
                    self.batch_norms.append(bn)

            self.convs.append(conv_1)
            self.batch_norms.append(bn_1)

        self.mlp = nn.Sequential(nn.Linear(hidden_dims, 128),
                                    nn.Tanh(),
                                    nn.Linear(128, num_classes))

    def forward(self, data, device=None):
        x, edge_index, batch = data
        if device:
            x, edge_index, batch = x.to(device), edge_index.to(device), batch.to(device)
        time_expand = self.time_linear(x[:, 768:772])
        x = torch.cat([x[:, :768].clone().detach(),
                        time_expand,
                        x[:, 772:].clone().detach()], dim=-1)
        # time_expand = self.time_linear(x[:, 34:34+4])
        # x = torch.cat([x[:, :34].clone().detach(),
        #                 time_expand,
        #                 x[:, 34+4:].clone().detach()], dim=-1)

        for conv, batch_norm in zip(self.convs, self.batch_norms):
            x = torch.tanh(conv(x, edge_index))
            x = batch_norm(x)

        x = global_mean_pool(x, batch)
        x = F.relu(x)
        x = self.mlp(x)
        return x


class SiameseGNN(nn.Module):
    def __init__(self, gnn):
        super(SiameseGNN, self).__init__()
        self.gnn = gnn

    def forward(self, data1, data2, data3, device):
        # Obtain embeddings for each graph
        emb1 = self.gnn(data1, device)
        emb2 = self.gnn(data2, device)
        emb3 = self.gnn(data3, device)
        return emb1, emb2, emb3

    def get_embedding(self, trace):
        # Generate an embedding for a single graph
        # batch = []
        # batch.extend([0] * trace.feature.size(0))
        # batch = torch.tensor(batch)
        batch = torch.zeros((trace.feature.size(0)))
        emb = self.gnn((trace.feature, trace.edge_index.type(torch.int64), batch.type(torch.int64)))
        return emb[0]
    

class ContrastiveLoss(nn.Module):
    def __init__(self, margin=1.0):
        super(ContrastiveLoss, self).__init__()
        self.margin = margin

    def distance(self,emb1,emb2):
        return 1-torch.sum(emb1*emb2,dim=1)/(torch.norm(emb1,dim=1)*torch.norm(emb2,dim=1))

    def forward(self, emb1, emb2, emb3):
        # Euclidean distance
        # distance = torch.nn.functional.pairwise_distance(emb1, emb2)
        # logger.info(f"{label.shape}, {emb1.shape}")
        # loss = torch.mean((1 - label) * torch.pow(distance, 2) +
        #                   (label) * torch.pow(torch.clamp(self.margin - distance, min=0.0), 2))
        dis = self.distance(emb1,emb2)-self.distance(emb1,emb3)+self.margin
        dis[dis<0]=0
        loss = torch.mean(dis)
        return loss
    