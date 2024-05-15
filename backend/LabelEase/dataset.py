# from torch_geometric.data import Dataset, Data
# from typing import *
from data.data_models import *
import os
import torch
from torch.utils.data import Dataset
import pickle
from utils import clean
import numpy as np

class TraceDataset(Dataset):
    def __init__(self,data_type):
        super(TraceDataset, self).__init__()
        self.data_type = data_type
        with open(f"./data/{data_type}/trace_tuple.pkl",'br') as f:
            self.pair_list = pickle.load(f)
        with open(f"./data/{data_type}/operation_name_2_verctor.pkl",'br') as f:
            self.operation_name_2_vector = pickle.load(f)
        with open(f"./data/{data_type}/status_2_vector.pkl",'br') as f:
            self.status_2_vector = pickle.load(f)


    
    def __len__(self):
        return len(self.pair_list)
    
    def __getitem__(self, idx):
        trace_pair = self.pair_list[idx]
        return (
            self.get_graph_data(trace_pair[0]),
            self.get_graph_data(trace_pair[1]),
            self.get_graph_data(trace_pair[2]),
        )


    @staticmethod
    def collate_fn(batch):
        # 分别处理两个trace的特征和边索引
        trace1_features, trace2_features, trace3_features = [], [], []
        trace1_edge_indices, trace2_edge_indices, trace3_edge_indices = [], [], []
        trace1_batch, trace2_batch, trace3_batch = [], [], []
        trace1_ptr, trace2_ptr, trace3_ptr = 0, 0, 0

        for trace1, trace2, trace3 in batch:
            # 处理第一个trace
            trace1_features.append(trace1[0])
            trace1_edge_indices.append(trace1[1] + trace1_ptr)  # 更新边索引
            trace1_batch.extend([trace1_ptr] * trace1[0].size(0))
            trace1_ptr += 1

            # 处理第二个trace
            trace2_features.append(trace2[0])
            trace2_edge_indices.append(trace2[1] + trace2_ptr)  # 更新边索引
            trace2_batch.extend([trace2_ptr] * trace2[0].size(0))
            trace2_ptr += 1

            # 处理第3个trace
            trace3_features.append(trace3[0])
            trace3_edge_indices.append(trace3[1] + trace3_ptr)  # 更新边索引
            trace3_batch.extend([trace3_ptr] * trace3[0].size(0))
            trace3_ptr += 1

        # 合并数据
        trace1_features = torch.cat(trace1_features, dim=0)
        trace1_edge_indices = torch.cat(trace1_edge_indices, dim=1).type(torch.long)
        trace1_batch = torch.tensor(trace1_batch, dtype=torch.long)

        trace2_features = torch.cat(trace2_features, dim=0)
        trace2_edge_indices = torch.cat(trace2_edge_indices, dim=1).type(torch.long)
        trace2_batch = torch.tensor(trace2_batch, dtype=torch.long)
        
        trace3_features = torch.cat(trace3_features, dim=0)
        trace3_edge_indices = torch.cat(trace3_edge_indices, dim=1).type(torch.long)
        trace3_batch = torch.tensor(trace3_batch, dtype=torch.long)



        return (trace1_features, trace1_edge_indices, trace1_batch), \
               (trace2_features, trace2_edge_indices, trace2_batch), \
               (trace3_features, trace3_edge_indices, trace3_batch)


    def get_graph_data(self, trace):
        node_feats=[]
        edge_index=[]
        span_dic={}

        trace_id = trace.trace_id
        start_time = trace.root_span.start_time
        span_stack = [trace.root_span]
        while len(span_stack)>0:
            span = span_stack.pop()
            children_span_list = span.children_span_list
            span_stack.extend(children_span_list)

            cmdb_id,operation_name = span.cmdb_id, span.operation_name
            operation_name = clean(f"{cmdb_id} {operation_name}".lower())  


            duration_time = span.duration
            waiting_time = sum(map(lambda span:span.duration,span.children_span_list))
            local_execution_time = duration_time-waiting_time
            relative_start_time = (span.start_time-start_time).total_seconds()
            
            node=np.concatenate((self.operation_name_2_vector[operation_name],np.array([duration_time,waiting_time,local_execution_time,relative_start_time]),self.status_2_vector[span.status]))
            # if self.data_type == 'data1':
            #     node=np.concatenate((self.operation_name_2_vector[operation_name],np.array([duration_time,waiting_time,local_execution_time,relative_start_time]),self.status_2_vector[int(span.status)]))
            # elif self.data_type=='data2':
            #     node=np.concatenate((self.operation_name_2_vector[operation_name],np.array([duration_time,waiting_time,local_execution_time,relative_start_time]),self.status_2_vector[span.status]))
            # else:
            #     node=np.concatenate((self.operation_name_2_vector[operation_name],np.array([duration_time,waiting_time,local_execution_time,relative_start_time]),self.status_2_vector[int(span.status)]))

            node_feats.append(node)
            span_dic[span.span_id]=len(span_dic)
            edge_index.append([span.parent_span_id,span.span_id])

        edge_index_list = []
        for ps,s in edge_index:
            if ps in span_dic and s in span_dic:
                edge_index_list.append([span_dic[ps],span_dic[s]])
        edge_index_list=np.array(edge_index_list).T
        edge_index_list=torch.LongTensor(edge_index_list)


        x = torch.FloatTensor(node_feats)
        y = torch.LongTensor([trace.anomaly])

        return (x,edge_index_list)

        # data = Data(x=x,edge_index=edge_index_list,y=y,trace_id=trace_id)
