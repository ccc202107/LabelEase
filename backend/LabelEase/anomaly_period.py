import pandas as pd
import json
import pickle
from tqdm import tqdm
import os
# from config import *

def merge(intervals):
    intervals.sort()
    merged_list = []
    for interval in intervals:
        if not merged_list or merged_list[-1][1] < interval[0]:
            merged_list.append(interval)
        else:
            merged_list[-1][1] = max(merged_list[-1][1], interval[1])
    return merged_list


def main(out_path,data_file_path):
    df = pd.read_csv(os.path.join(data_file_path,"labels.csv"))
    fault_id = set()
    for i,j in zip(df['trace_id'],df['anomaly']):
        if j==1:
            fault_id.add(i)
    with open(os.path.join(data_file_path,"data.pkl"),'br') as f:
        data = pickle.load(f)

    intervals = []
    for trace in tqdm(data):
        if trace.trace_id in fault_id:
            root_span = trace.root_span
            intervals.append([root_span.timestamp/1000000,root_span.timestamp/1000000+5*60])
    fault_period = merge(intervals)
    with open(os.path.join(out_path,'anomaly_period.json'),'w') as f:
        json.dump(fault_period,f) 
    print(len(fault_period))

if __name__=='__main__':
    main()