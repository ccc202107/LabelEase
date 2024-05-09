from transformers import BertTokenizer,TFBertModel
import tensorflow as tf

import numpy as np
import os
import pickle
import pandas as pd
from tqdm import tqdm

from config import *
from utils import clean
from data.data_models import *

def generate_data_pkl(data_file):
    df = pd.read_csv(f"{data_file}/data.csv")
    trace_list: List[Trace] = list()
    trace_id_span_list_dict = {}

    # 使用iterrows()方法遍历行  
    for index,row in tqdm(df.iterrows()):  
        trace_id = str(row['trace_id'])
        temp_list = trace_id_span_list_dict.get(trace_id, list())

        start_time = datetime.fromtimestamp(row['timestamp']/1000000)
        anomaly=0

        temp_list.append(Span(
            trace_id=trace_id,
            span_id=str(row['span_id']),
            parent_span_id=str(row['parent_span_id']),
            children_span_list=list(),
            service_name=row['service_name'],
            status=str(row['status']),
            start_time=start_time,
            timestamp=int(row['timestamp']),
            cmdb_id=str(row['cmdb_id']),
            operation_name=str(row['operation_name']),
            # end_time=end_time,
            duration=row['duration'],
            anomaly=anomaly
        ))
        trace_id_span_list_dict[trace_id] = temp_list

    for trace_id, span_list in tqdm(trace_id_span_list_dict.items()):
        anomaly=0
        span_id_dict = {}
        rca_service = ""
        for span in span_list:
            span_id_dict[span.span_id] = span
            if span.anomaly==1:
                anomaly=1
                rca_service = span.cmdb_id

        imcomplete_flag = False
        root_span: Span = None
        for span in span_list:

            parent_span = span_id_dict.get(span.parent_span_id, None)

            if span.parent_span_id != '0' and parent_span is None:
                no_parent_count += 1
                imcomplete_flag = True
            
            if parent_span is not None:
                parent_span.children_span_list.append(span)

            if span.parent_span_id == '0':
                root_span = span

        if imcomplete_flag:
            continue

        if root_span is None:
            continue

        trace = Trace(
            trace_id=trace_id,
            root_span=root_span,
            span_count=len(span_list),
            anomaly=anomaly
        )

        trace_list.append(trace)

    with open(f"{data_file}/data.pkl",'bw') as f:
        pickle.dump(trace_list,f)


def bert_encoder(s, no_wordpiece=0):
    """ Compute semantic vector with BERT
    Parameters
    ----------
    s: string to encode
    no_wordpiece: 1 if you do not use sub-word tokenization, otherwise 0

    Returns
    -------
        np array in shape of (768,)
    """
    if no_wordpiece:
        words = s.split(" ")
        words = [word for word in words if word in bert_tokenizer.vocab.keys()]
        s = " ".join(words)
        print("sdsadasda",s)
    inputs = bert_tokenizer(s, return_tensors='tf', max_length=512)
    outputs = bert_model(**inputs)
    v = tf.reduce_mean(outputs.last_hidden_state, 1)
    return np.array(v[0])


def trace_preprocess(path, no_word_piece=0):
    
    encoder = bert_encoder
    status_2_vector_path = os.path.join(path,"status_2_vector.pkl")
    operation_name_2_verctor_path = os.path.join(path,"operation_name_2_verctor.pkl")
    with open(os.path.join(path,"data.pkl"),'br') as f:
        trace_list = pickle.load(f)

    status_set = set()

    operation_name_2_verctor = {}
    for trace in tqdm(trace_list):
        trace_id = trace.trace_id
        span_stack = [trace.root_span]
        while len(span_stack)>0:
            span = span_stack.pop()
            children_span_list = span.children_span_list
            span_stack.extend(children_span_list)
            status_set.add(span.status)
            operation_name = clean(f"{span.cmdb_id} {span.operation_name}".lower()) 

            if operation_name not in operation_name_2_verctor.keys():
                # try:
                operation_name_2_verctor[operation_name] = encoder(operation_name, no_word_piece)

    status_2_vector = {}
    for i,code in enumerate(status_set):
        code_vector=np.zeros(len(status_set))
        code_vector[i]=1
        status_2_vector[code]=code_vector
    with open(status_2_vector_path,'bw') as f:
        pickle.dump(status_2_vector, f)

    with open(operation_name_2_verctor_path,'bw') as f:
        pickle.dump(operation_name_2_verctor, f)
    print('Done')

if __name__ == '__main__':
    generate_data_pkl(f"data/{data_type}")
    bert_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    bert_model = TFBertModel.from_pretrained('bert-base-uncased', from_pt=True)

    trace_preprocess(f"data/{data_type}")