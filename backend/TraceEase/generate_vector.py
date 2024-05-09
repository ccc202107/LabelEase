from model import GAT
from utils import clean
from tqdm import tqdm
from config import *
import numpy as np
import torch
import pickle
import random


def main():
    random.seed(seed)

    with open(f"./data/{data_type}/operation_name_2_verctor.pkl",'br') as f:
        operation_name_2_vector = pickle.load(f)
    with open(f"./data/{data_type}/status_2_vector.pkl",'br') as f:
        status_2_vector = pickle.load(f)


    with open(f"./data/{data_type}/data.pkl",'br') as f:
        trace_list = pickle.load(f)


    random.shuffle(trace_list)

    def get_graph_data(trace):
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

            node=np.concatenate((operation_name_2_vector[operation_name],np.array([duration_time,waiting_time,local_execution_time,relative_start_time]),status_2_vector[span.status]))

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
        # y = torch.LongTensor(trace.anomaly)
        y=trace.anomaly

        return (x,edge_index_list,y)


    trace_vector_list = []

    trace_id_list = []
    # device = torch.device('cuda:{}'.format(gpu_id))
    device = torch.device('cpu')
    gnn=GAT(embedding_size = embed_dim, hidden_dims = embed_dim,num_layers = num_layers).to(device)
    # gnn.load_state_dict(torch.load("./Output/0113__15epoch_0.0001lr_32bs_3layers/model_save/gnn_model_param.pkl"))
    gnn.load_state_dict(torch.load(os.path.join(save_dir,f"gnn_model_param.pkl")))
    gnn.eval()
    for trace in tqdm(trace_list):
        
        x,edge_index_list,y = get_graph_data(trace)
        if len(edge_index_list)==0:
            edge_index_list=torch.tensor([[0],[0]])
        batch = torch.zeros((x.size(0))).type(torch.int64)

        x,edge_index_list,batch = x.to(device),edge_index_list.to(device),batch.to(device)
        
        trace_vector = gnn(data=(x,edge_index_list,batch),device=device).cpu().detach()[0].numpy()

        trace_vector_list.append(trace_vector)
        trace_id_list.append(trace.trace_id)



    with open(os.path.join(out_path,"trace_vector_list.pkl"),'bw') as f:
        pickle.dump(trace_vector_list,f)
    with open(os.path.join(out_path,"trace_id_list.pkl"),'bw') as f:
        pickle.dump(trace_id_list,f)

if __name__ == "__main__":
    main()