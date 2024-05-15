from sklearn.cluster import OPTICS,KMeans
from sklearn.datasets import make_blobs
from collections import Counter
import pickle
import json
import numpy as np
import random
import time
from config import *

def cal_min_dis_index(v1,v2):
    return np.sum((v1-v2)*(v1-v2),axis=1).argmin()


def main():
    with open(os.path.join(out_path,"trace_id_list.pkl"),'br') as f:
        trace_id_list = pickle.load(f)
    with open(os.path.join(out_path,"trace_vector_list.pkl"),'br') as f:
        data = pickle.load(f)

    N = len(data)
    p_ = N//10
    # p = 60
    cluster_total_time=0
    print(N,p_)

    fw=open(f"{out_path}/cluster_time.txt",'w')

    random.seed(seed)
    np.random.seed(seed)
    selected_samples = random.sample(data,p_)
    selected_samples = np.array(selected_samples)
    # random.seed(seed)
    # np.random.seed(seed)
    # selected_y_true = np.array(random.sample(y_true,p_))
    random.seed(seed)
    np.random.seed(seed)
    selected_trace_id_list = random.sample(trace_id_list,p_)
    print("selected_samples:",selected_samples.shape)

    kmeans = KMeans(n_clusters=max(p,1))
    kmeans_start_time = time.time()
    kmeans.fit(selected_samples)
    kmeans_end_time = time.time()
    cluster_total_time += (kmeans_end_time-kmeans_start_time)

    # 获取聚类中心
    centroids = kmeans.cluster_centers_
    print("centroids:",centroids.shape)
    label_vector = []
    # label_y_true = []
    label_trace_id = []
    for centroid in centroids:
        min_index = cal_min_dis_index(selected_samples,centroid)
        label_vector.append(centroid)
        # label_y_true.append(selected_y_true[min_index])
        label_trace_id.append(selected_trace_id_list[min_index])


    label_vector = np.array(label_vector)
    # label_y_true = np.array(label_y_true)
    print(label_vector.shape)
    print("total_cluster_time:",cluster_total_time)
    fw.write(f"\ntotal_cluster_time:{cluster_total_time}\n")
    fw.close()

    with open(os.path.join(out_path,"chosed_central_vector.pkl"),'bw') as f:
        pickle.dump(label_vector,f)

    with open(os.path.join(out_path,"chosed_trace_id.json"),'w') as f:
        json.dump(label_trace_id,f)

    with open(f"./data/{data_type}/data.pkl",'br') as f:
        trace_list = pickle.load(f)
    
    chosedid2trace={}
    label_trace_id = set(label_trace_id)
    for trace in trace_list:
        if trace.trace_id in label_trace_id:
            chosedid2trace[trace.trace_id] = trace
    with open(os.path.join(out_path,"chosedid2trace.pkl"),'bw') as f:
        pickle.dump(chosedid2trace,f)

    

if __name__ == "__main__":
    main()