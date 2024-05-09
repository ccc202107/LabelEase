from typing import *
from data.data_models import *
# from config import *
import pickle
import pandas as pd
import numpy as np
import os

def get_visited_service_set(trace: Trace) -> set:
    root_span = trace.root_span
    queue = [root_span]
    service_set = set()
    while len(queue):
        span = queue.pop(0)
        queue.extend(span.children_span_list)
        if span.service_name is None:
            span.service_name = span.cmdb_id
        service_set.add(span.service_name)
    
    return service_set

def get_call_path_set(trace: Trace) -> set:
    root_span = trace.root_span
    queue = [root_span]
    path_set = set()
    while len(queue):
        span = queue.pop(0)
        queue.extend(span.children_span_list)
        if span.service_name is None:
            span.service_name = span.cmdb_id

        for child in span.children_span_list:
            if child.service_name is None:
                child.service_name = child.cmdb_id
            path_set.add(f"{span.service_name}->{child.cmdb_id}")
    return path_set

def spectrum(trace_list: List[Trace], service_set: list) -> dict:

    service_statistic_dict ={
        service: 0.0
        for service in service_set
    }
    service_Oef_dict ={}

    for service in service_statistic_dict:
        ef = 0
        ep = 0
        nf = 0

        for trace in trace_list:
            service_set = get_visited_service_set(trace)

            if trace.anomaly == 1:
                if service in service_set:
                    ef += 1
                else:
                    nf += 1
            else:
                if service in service_set:
                    ep += 1
        
        ef = ef if ef > 0 else 0.0001
        ep = ep if ep > 0 else 0.0001
        nf = nf if nf > 0 else 0.0001

        statistic = ef / (((ef + ep) * (ef + nf)) ** 0.5)

        service_statistic_dict[service] = statistic
        service_Oef_dict[service] = ef
    
    return service_statistic_dict,service_Oef_dict


def get_duration_dic(selected_traces,service_set):
    anomaly_period_service_2_duration = {}
    for service in service_set:
        anomaly_period_service_2_duration[service] = []
    for trace in selected_traces:
        root_span = trace.root_span
        queue = [root_span]
        while len(queue):
            span = queue.pop(0)
            queue.extend(span.children_span_list)
            if span.service_name is None:
                span.service_name = span.cmdb_id
            anomaly_period_service_2_duration[span.service_name].append(span.duration)
    for service in anomaly_period_service_2_duration.keys():
        anomaly_period_service_2_duration[service] = np.array(anomaly_period_service_2_duration[service])
    return anomaly_period_service_2_duration


def get_fscore_and_services(period,out_path,data_file_path):

    df = pd.read_csv(os.path.join(data_file_path,"labels.csv"))
    fault_id = set()
    for i,j in zip(df['trace_id'],df['anomaly']):
        if j==1:
            fault_id.add(i)

    with open(os.path.join(data_file_path,"data.pkl"),'br') as f:
        data = pickle.load(f)
    selected_traces = []
    for trace in data:
        root_span = trace.root_span
        if period[0]<=root_span.timestamp/1000000<=period[1]:
            if trace.trace_id in fault_id:
                trace.anomaly = 1
            else:
                trace.anomaly = 0
            selected_traces.append(trace)

    service_set = set()
    call_path_set = set()
    for trace in selected_traces:
        _set = get_visited_service_set(trace)
        service_set = service_set | _set
        _set = get_call_path_set(trace)
        call_path_set = call_path_set | _set
    service_statistic_dict,service_Oef_dict = spectrum(selected_traces,list(service_set))
    # print(service_statistic_dict)
    # print(call_path_set)
    anomaly_period_service_2_duration = get_duration_dic(selected_traces,set(service_statistic_dict.keys()))
    return [service_statistic_dict,call_path_set,anomaly_period_service_2_duration,service_Oef_dict]

def main(period,out_path,data_file_path):
    with open(os.path.join(out_path,"service_ne.pkl"),'br') as f:
        res = pickle.load(f)
    return res
    service_statistic_dict,call_path_set,anomaly_period_service_2_duration,service_Oef_dict = get_fscore_and_services(period,out_path,data_file_path)
    nodes = []
    edges = []
    with open(os.path.join(out_path,'statistic','service2duration.pkl'),'br') as f:
        service2duration = pickle.load(f)
    for i,j in service_statistic_dict.items():
        node = {}
        node['id'] = i
        node['service'] = i
        node['ef'] = service_Oef_dict[i]
        node['label'] = i.split("service")[0]
        node['score'] = float("%.2f"%j)
        node['total_duration_mean'] = int(service2duration[i].mean())
        node['total_duration_std'] = int(service2duration[i].std())
        node['total_duration_median'] = int(np.median(service2duration[i]))
        node['period_duration_mean'] = int(anomaly_period_service_2_duration[i].mean())
        node['period_duration_std'] = int(anomaly_period_service_2_duration[i].std())
        node['period_duration_median'] = int(np.median(anomaly_period_service_2_duration[i]))
        node["shape"] = 'circle'

        r_min,r_max=73,230
        g_min,g_max=108,240
        b_min,b_max=206,254
        r = r_max-node['score']*(r_max-r_min)
        g = g_max-node['score']*(g_max-g_min)
        b = b_max-node['score']*(b_max-b_min)
        node['color'] = f'rgb({r}, {g}, {b})'
        

        nodes.append(node)
    
    for call_path in set(call_path_set):
        _from, _to = call_path.split("->")
        edge = {}
        edge['from'] = _from
        edge['to'] = _to
        edges.append(edge)

    with open(os.path.join(out_path,"service_ne.pkl"),'bw') as f:
        pickle.dump([nodes,edges],f)
    return nodes,edges



if __name__ == "__main__":
    nodes,edges = main([1703071804.771092, 1703072814.557692])
    print(nodes)
    print(edges)