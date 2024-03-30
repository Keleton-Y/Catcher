
import os.path
import numpy as np
import pandas as pd
from globals.variable import BASE_PATH
import warnings
import colorama
from colorama import Fore, Style


colorama.init()
warnings.filterwarnings('ignore')


def read_csv(filename: str) -> pd.DataFrame:
    try:
        res = pd.read_csv(os.path.join(BASE_PATH, "dao/data/" + filename + ".csv"))
        return res
    except Exception as e:

        print(f"{Fore.RED}File not found: {filename}.csv, " +
              f"please run TkPS simulator first to generate indispensable data files.")

        return pd.DataFrame()



sub_info = read_csv("sub_info_calc")

msg_info = read_csv("msg_info_id16")

msg_info_merged_minute = read_csv("msg_info_merged_minute")


global_latency_sampled = read_csv("global_latency_sampled")

global_latency_merged = read_csv("global_latency_merged")

_global_costs = read_csv("global_costs")
_global_costs["timestamp"] = _global_costs["timestamp"].astype(np.int64)
global_costs = _global_costs

_global_time_cost = read_csv("global_time_cost")
_global_time_cost["timestamp"] = _global_time_cost["timestamp"].astype(np.int64)
global_time_cost = _global_time_cost


sub_costs = read_csv("sub_costs_merged_minute")

cache_info = read_csv("cache_info")
cache_info_merged_minute = read_csv("cache_info_merged_minute")

cache_updates = read_csv("cache_updates_calc")


all_utilization_ratio = read_csv("all_utilization_ratio")

all_memory_costs = read_csv("all_memory_costs")
all_computational_time = read_csv("all_computational_time")
