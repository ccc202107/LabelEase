import pickle
import math
import random
from config import *

def main():
    random.seed(seed)
    # SAMPLE_NUM = 60000
    SAMPLE_NUM = 60

    with open(f"./data/{data_type}/data.pkl",'br') as f:
        trace_list = pickle.load(f)


    def span_hash(_span,span_level):
        _hash = hash(_span.cmdb_id) + hash(_span.operation_name) + span_level*11
        for child_span in _span.children_span_list:
            h = span_hash(child_span,span_level+1)
            _hash += h
        return _hash

    print(len(trace_list))

    hash2span = {}
    for trace in trace_list:
        _hash = span_hash(trace.root_span, 0)
        if _hash in hash2span:
            hash2span[_hash].append(trace)
        else:
            hash2span[_hash]=[trace]

    new_hash2span = {}
    new_hash2span['-1']=[]
    for k,v in hash2span.items():
        if len(v)<40:
            new_hash2span['-1'].extend(v)
        else:
            new_hash2span[k]=v
    hash2span = new_hash2span

    weights = {}
    for k,v in sorted(hash2span.items(),key=lambda x:-len(x[1])):
        print(k,"->",math.pow(math.log(len(trace_list)/len(v)),0.5))
        weights[k]=math.log(len(trace_list)/len(v))

    trace_tuple = []

    anomaly_tuple = []
    while SAMPLE_NUM>0:
        # print(SAMPLE_NUM)
        SAMPLE_NUM-=1
        selected_type = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
        a = random.choice(hash2span[selected_type])
        selected_type = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
        b = random.choice(hash2span[selected_type])
        selected_type = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
        c = random.choice(hash2span[selected_type])

        a_hash = span_hash(a.root_span,0)
        b_hash = span_hash(b.root_span,0)
        c_hash = span_hash(c.root_span,0)

        if len(set((a_hash,b_hash,c_hash)))==2:
            if a_hash==b_hash and a_hash!=c_hash:
                trace_tuple.append([a,b,c])
            elif a_hash==c_hash and a_hash!=b_hash:
                trace_tuple.append([a,c,b])
            elif b_hash==c_hash and b_hash!=a_hash:
                trace_tuple.append([b,c,a])

        elif len(set((a_hash,b_hash,c_hash)))==1:

            a_duration = a.root_span.duration
            b_duration = b.root_span.duration
            c_duration = c.root_span.duration
            a_b_duration = abs(a_duration-b_duration)
            a_c_duration = abs(a_duration-c_duration)
            b_c_duration = abs(b_duration-c_duration)

            if a_b_duration< a_c_duration and a_b_duration< b_c_duration:
                trace_tuple.append([a,b,c])
                anomaly_tuple.append((trace_tuple[-1][0].anomaly,trace_tuple[-1][1].anomaly,trace_tuple[-1][2].anomaly))
            elif a_c_duration< a_b_duration and a_c_duration< b_c_duration:
                trace_tuple.append([a,c,b])
                anomaly_tuple.append((trace_tuple[-1][0].anomaly,trace_tuple[-1][1].anomaly,trace_tuple[-1][2].anomaly))
            elif b_c_duration< a_c_duration and b_c_duration < a_b_duration:
                trace_tuple.append([b,c,a])
                anomaly_tuple.append((trace_tuple[-1][0].anomaly,trace_tuple[-1][1].anomaly,trace_tuple[-1][2].anomaly))


            # if a_b_duration *80< a_c_duration and a_b_duration*80 < b_c_duration:
            #     trace_tuple.append([a,b,c])
            #     anomaly_tuple.append((trace_tuple[-1][0].anomaly,trace_tuple[-1][1].anomaly,trace_tuple[-1][2].anomaly))
            #     continue
            # elif a_c_duration*80< a_b_duration and a_c_duration*80< b_c_duration:
            #     trace_tuple.append([a,c,b])
            #     anomaly_tuple.append((trace_tuple[-1][0].anomaly,trace_tuple[-1][1].anomaly,trace_tuple[-1][2].anomaly))
            #     continue
            # elif b_c_duration*80< a_c_duration and b_c_duration*80< a_b_duration:
            #     trace_tuple.append([b,c,a])
            #     anomaly_tuple.append((trace_tuple[-1][0].anomaly,trace_tuple[-1][1].anomaly,trace_tuple[-1][2].anomaly))
            #     continue
        else:
            SAMPLE_NUM+=1
            
            

    from collections import Counter
    print(Counter(anomaly_tuple),len(anomaly_tuple))

    with open(f"./data/{data_type}/trace_tuple.pkl",'bw') as f:
        pickle.dump(trace_tuple,f)

if __name__ == "__main__":
    main()