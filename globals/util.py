

import datetime
from typing import List



def remove_duplicates_and_keep_order(input_list):
    seen = set()
    output_list = []

    for item in input_list:
        if item not in seen:
            seen.add(item)
            output_list.append(item)

    return output_list



def timestamp_normalized(timestamps: List[int], step: int) -> tuple[List[str], List[int]]:
    timestamps = [timestamp - timestamp % step for timestamp in timestamps]
    timestamps = remove_duplicates_and_keep_order(timestamps)
    datetimes = [
        datetime.datetime.fromtimestamp(timestamp)
        for timestamp in timestamps
    ]
    return [f"{dt.hour}:{str(dt.minute).zfill(2)}" for dt in datetimes], \
        [timestamp for timestamp in timestamps]


def timestamp_to_hour(timestamps: List[int]) -> tuple[List[str], List[int]]:
    return timestamp_normalized(timestamps, 60 * 60)


def timestamp_to_3hour(timestamps: List[int]) -> tuple[List[str], List[int]]:
    return timestamp_normalized(timestamps, 60 * 60 * 3)


def timestamp_to_15min(timestamps: List[int]) -> tuple[List[str], List[int]]:
    return timestamp_normalized(timestamps, 60 * 15)


def timestamp_to_30min(timestamps: List[int]) -> tuple[List[str], List[int]]:
    return timestamp_normalized(timestamps, 60 * 30)


def timestamp_to_2min(timestamps: List[int]) -> tuple[List[str], List[int]]:
    return timestamp_normalized(timestamps, 60 * 2)


def timestamp_to_1min(timestamps: List[int]) -> tuple[List[str], List[int]]:
    return timestamp_normalized(timestamps, 60 * 1)