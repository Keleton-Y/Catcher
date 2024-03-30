
import math
import os.path
import numpy as np
import pandas as pd
from globals.variable import BASE_PATH
import warnings

warnings.filterwarnings('ignore')


def read_csv(filename: str) -> pd.DataFrame:
    return pd.read_csv(os.path.join(BASE_PATH, "dao/data/" + filename + ".csv"))



def normalize_sub_cost():
    sub_costs = read_csv("sub_costs")

    sub_costs_sampled = sub_costs.sample(frac=0.005, random_state=1)
    sub_costs_sampled["timestamp"] = sub_costs_sampled["timestamp"] - sub_costs_sampled["timestamp"] % 3600
    sub_costs_sampled.to_csv("data/sub_costs_normalized_hour.csv", index=False)



def merge_msg_info():
    msg_info = read_csv("msg_info")
    msg_info_merged_hour = msg_info[["start_time", "update_triggerd_insert", "update_triggered_delete"]]

    
    msg_info_merged_hour["start_time"] = msg_info_merged_hour["start_time"] - msg_info_merged_hour["start_time"] % 600

    msg_info_merged_hour['count'] = msg_info_merged_hour.groupby('start_time')['start_time'].transform('count')

    msg_info_merged_hour = msg_info_merged_hour.groupby('start_time', as_index=False). \
        agg({
        'update_triggerd_insert': 'sum',
        'update_triggered_delete': 'sum',
        'count': 'first'
    })

    msg_info_merged_hour.to_csv("data/msg_info_merged_minute.csv", index=False)


def merge_global_latency():
    global_latency = read_csv("global_latency")
    global_latency["timestamp"] = global_latency["timestamp"] - global_latency["timestamp"] % 120
    global_latency = global_latency.groupby('timestamp', as_index=False).agg({'latency': 'sum'})
    global_latency.to_csv("data/global_latency_merged_minute.csv", index=False)


def samply_global_latency():
    global_latency = read_csv("global_latency")
    global_latency_sampled = global_latency.sample(frac=0.005, random_state=1)
    global_latency_sampled.to_csv("data/global_latency_sampled.csv", index=False)



def merge_sub_costs_1minute():
    sub_costs = read_csv("sub_costs")
    print(sub_costs["timestamp"].min(), sub_costs["timestamp"].max())
    sub_costs["timestamp"] = sub_costs["timestamp"] - sub_costs["timestamp"] % 60
    sub_costs_merged_minute = sub_costs.groupby("timestamp", as_index=False). \
        agg({'update_cost': 'mean'})
    sub_costs_merged_minute.to_csv("data/sub_costs_merged_minute.csv", index=False)


def merge_cache_info_minute():
    cache_info = read_csv("cache_info")
    cache_info["timestamp"] = cache_info["timestamp"] - cache_info["timestamp"] % 600
    cache_info_merged_minute = cache_info.groupby(["timestamp", "ID"], as_index=False).first()
    cache_info_merged_minute.to_csv("data/cache_info_merged_minute.csv", index=False)


def calculate_latency_ratio():
    time_gap = 300

    global_latency = read_csv("global_latency")
    global_latency.loc[global_latency['latency'] > 0.1, 'latency_'] = ">100ms"
    global_latency.loc[(global_latency['latency'] > 0.01) & (global_latency['latency'] < 0.1), 'latency_'] = "10-100ms"
    global_latency.loc[global_latency['latency'] < 0.01, 'latency_'] = "<10ms"

    global_latency["timestamp"] = global_latency["timestamp"] - global_latency["timestamp"] % time_gap

    global_latency = global_latency.drop('latency', axis=1)

    global_latency['count'] = 0

    global_latency['count'] = global_latency.groupby(["timestamp", "latency_"]).transform('count')

    global_latency = global_latency.groupby(["timestamp", "latency_", "count"], as_index=False).mean()

    timestamp = global_latency["timestamp"].min()

    ed = global_latency["timestamp"].max()

    global_latency["ratio"] = 0

    while timestamp <= ed:
        counts = {}
        sum_count = 0
        for lt in ["<10ms", "10-100ms", ">100ms"]:
            number = len(global_latency[(global_latency['timestamp'] == timestamp) &
                                        (global_latency['latency_'] == lt)])
            counts[lt] = global_latency[(global_latency['timestamp'] == timestamp) &
                                        (global_latency['latency_'] == lt)]["count"]
            if len(counts[lt]) > 0:
                counts[lt] = counts[lt].iloc[0]
            else:
                counts[lt] = 0

            sum_count += counts[lt]
            if number == 0:
                new_row = pd.DataFrame({"timestamp": [timestamp], "latency_": [lt], "count": [0]})
                global_latency = pd.concat([global_latency, new_row], ignore_index=True)

        if sum_count == 0:
            continue
        for lt in ["<10ms", "10-100ms", ">100ms"]:
            global_latency.loc[(global_latency['timestamp'] == timestamp)
                               & (global_latency['latency_'] == lt), "ratio"] = counts[lt] / sum_count

        timestamp += time_gap

    global_latency = global_latency.sort_values(by="timestamp")

    global_latency = global_latency.rename(columns={'latency_': 'latency'})

    global_latency.to_csv("data/global_latency_merged.csv", index=False)


def calc_cache_updates():
    cu = read_csv("cache_updates")
    

    cu['insert_time'] = None
    cu['delete_time'] = None

    cu = cu.sort_values(by="msgID")

    it = {}
    dt = {}

    for index, row in cu.iterrows():
        if row["operation"] == "I":
            it[row["msgID"] + row["worker_id"]] = row["timestamp"]
        elif row["operation"] == "D":
            dt[row["msgID"] + row["worker_id"]] = row["timestamp"]

    for index, row in cu.iterrows():
        cu.at[index, "insert_time"] = it[row["msgID"] + row["worker_id"]]
        cu.at[index, "delete_time"] = dt[row["msgID"] + row["worker_id"]]

    cu = cu.groupby(["worker_id", "delete_time", "insert_time", "msgID"], as_index=False).first()

    cu.to_csv("data/cache_updates_calc.csv", index=False)


def id16_sub_info():
    sub_info = read_csv("sub_info")
    sub_info["ID16"] = sub_info.index.map(lambda x: hex(x)[2:].zfill(4).upper())
    np.random.seed(42)  
    sub_info['ID16'] = np.random.permutation(sub_info['ID16'])

    sub_info.to_csv("data/sub_info_id16.csv", index=False)


def id16_msg_info():
    sub_info = read_csv("msg_info")
    sub_info["ID16"] = sub_info.index.map(lambda x: hex(x)[2:].zfill(4).upper())
    np.random.seed(42)  
    sub_info['ID16'] = np.random.permutation(sub_info['ID16'])

    sub_info.to_csv("data/msg_info_id16.csv", index=False)


def calc_sub_map():

    sub_info = read_csv("sub_info")
    sub_info["target_id"] = ""
    more_sub_info = read_csv("more_sub_info")
    for index, row in sub_info.iterrows():
        nearest_row = more_sub_info.iloc[
            (more_sub_info['utilization_ratio'] - row['utilization_ratio']).abs().argsort()[:1]
        ]
        id = nearest_row.iloc[0]['ID']
        sub_info.at[index, "target_id"] = id

    sub_info["ID16"] = sub_info.index.map(lambda x: hex(x)[2:].zfill(4).upper())
    np.random.seed(42)  
    sub_info['ID16'] = np.random.permutation(sub_info['ID16'])

    sub_info.to_csv("data/sub_info_calc.csv", index=False)


def id16_cache_updates():
    cache_updates = read_csv("more_cache_updates")
    cache_updates = cache_updates.sort_values(by="worker_id")

    def mapper(x):
        if x > 16 ** 4:
            x = x % (16 ** 4)
        return hex(x)[2:].zfill(4).upper()

    cache_updates["msgID16"] = cache_updates.index.map(mapper=mapper)
    cache_updates.to_csv("data/cache_updates.csv", index=False)


if __name__ == '__main__':
    calc_cache_updates()
    pass
