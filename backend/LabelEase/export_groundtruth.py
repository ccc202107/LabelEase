import json
import os
# from config import *
import pandas as pd
from datetime import datetime

def main(out_path,data_file_path):
    with open(os.path.join(out_path,"anomaly_period.json"),'r') as f:
        anomaly_period = json.load(f)

    with open(os.path.join(out_path,"rcl_label.json"),'r') as f:
        res = json.load(f)
    res["timestamp"] = []
    res["duration"] = []
    for period in anomaly_period:
        timestamp = int(period[0])
        duration = int(period[1]-period[0])
        res["timestamp"].append(timestamp)
        res['duration'].append(duration)
    with open(os.path.join(data_file_path,"groundtruth.json"),'w') as f:
        json.dump(res,f)

if __name__ == "__main__":
    main()