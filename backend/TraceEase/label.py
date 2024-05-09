import pickle
import json
import random
import numpy as np
import pandas as pd
import tqdm
import os

def main(out_path,data_file_path,seed=2020):
    random.seed(seed)
    np.random.seed(seed)

    with open(os.path.join(out_path,"chosed_central_vector.pkl"),'br') as f:
        chosed_central_vector = pickle.load(f)
    with open(os.path.join(out_path,"chosed_trace_labels.json"),'r') as f:
        chosed_y_pred = json.load(f)

    with open(os.path.join(out_path,"trace_vector_list.pkl"),'br') as f:
        vectors = np.array(pickle.load(f))
    with open(os.path.join(out_path,"trace_id_list.pkl"),'br') as f:
        trace_id_list = np.array(pickle.load(f))


    def cal_min_dis_index(v1,v2):
        return np.sum((v1-v2)*(v1-v2),axis=1).argmin()


    print(vectors.shape)

    trace_labels = []

    for vector,trace_id in tqdm.tqdm(zip(vectors,trace_id_list)):
        min_index = cal_min_dis_index(chosed_central_vector,vector)
        trace_labels.append({'trace_id':trace_id,'anomaly':chosed_y_pred[min_index]})

    df = pd.DataFrame(trace_labels)
    df.to_csv(os.path.join(data_file_path,"labels.csv"),index=False)

if __name__ == '__main__':
    main()