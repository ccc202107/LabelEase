import os
from config import *
from utils import clean
from tqdm import tqdm
import numpy as np
import pickle
import json
import pandas as pd

# statistic
statistic_dir = os.path.join(out_path,"statistic")
if not os.path.exists(statistic_dir):
    os.mkdir(statistic_dir)


def get_call_path(called_path,span,path_set,operation2duration):
    if data_type=='data1':
        operation_name = clean(f"{span.cmdb_id} {span.operation_name}".lower()) 
    elif data_type=='data2':
        operation_name = f"{span.cmdb_id}".lower()
    called_path.append(operation_name)
    operation2duration["#".join(called_path)]=span.duration
    path_set.add("#".join(called_path))
    for _span in span.children_span_list:
        get_call_path(called_path,_span,path_set,operation2duration)
    called_path.pop()
    return operation2duration

def get_all_paths(trace_list):
    path_set = set()
    operation2duration_list = []
    for trace in tqdm(trace_list):
        operation2duration = get_call_path([],trace.root_span,path_set,{})
        operation2duration_list.append(operation2duration)
    print(len(path_set))
    path2index = {}
    for i,path in enumerate(path_set):
        path2index[path]=i
    data_list=[]
    for operation2duration in tqdm(operation2duration_list):
        # data = np.zeros(len(path_set))
        data = np.full(len(path_set),-1)
        for operation,duration in operation2duration.items():
            data[path2index[operation]]=duration
        data_list.append(data)
    return np.array(data_list),path2index


def stv_main():
    with open(f"./data/{data_type}/data.pkl",'br') as f:
        trace_list = pickle.load(f)
    stv,path2index = get_all_paths(trace_list)
    print(stv.shape)
    # np.save(os.path.join(statistic_dir,'stv.npy'),stv)
    # with open(os.path.join(statistic_dir,"path2index.json"),'w') as f:
    #     json.dump(path2index,f)
    path2duration = {}
    for i,j in path2index.items():
        duration_list = []
        for val in stv[:,j]:
            if val!=-1:
                duration_list.append(val)
        duration_list=np.array(duration_list)
        path2duration[i]={}
        path2duration[i]['median']=int(np.median(duration_list))
        path2duration[i]['mean']=int(np.mean(duration_list))
        path2duration[i]['std']=int(np.std(duration_list))

    with open(os.path.join(statistic_dir,'path2duration.json'),'w') as f:
        json.dump(path2duration,f)


def service_main():
    df = pd.read_csv(f"data/{data_type}/data.csv")
    service2duration = {}
    for service in set(df['service_name']):
        service2duration[service]=[]
    for service,duration in tqdm(zip(df['service_name'],df['duration'])):
        service2duration[service].append(duration)
    for service in service2duration.keys():
        service2duration[service] = np.array(service2duration[service])
    with open(os.path.join(statistic_dir,"service2duration.pkl"),'bw') as f:
        pickle.dump(service2duration,f)

def duration_main():
    df=pd.read_csv(f"./data/{data_type}/data.csv")
    res = {}
    res['max_duration'] = max(df['duration'])
    res['min_duration'] = min(df['duration'])
    with open(os.path.join(out_path,"max_min_duration.json"),'w') as f:
        json.dump(res,f)
        
def main():
    stv_main()
    service_main()
    # duration_main()

if __name__ == "__main__":
    main()


