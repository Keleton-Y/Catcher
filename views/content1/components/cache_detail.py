import copy
import datetime
import time
from typing import List
import numpy as np
from dash import html
from dash.dependencies import Input, Output
from pandas import DataFrame

from dao.df import cache_updates
from globals.variable import app
from dash.dependencies import Input, Output
from dao.df import cache_info

id_map = dict()
counter = 0






def time_format(timestamp):
    
    dt = datetime.datetime.fromtimestamp(timestamp)
    return f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"


def get_messages(timestamp: int, target_id: str):
    cu = copy.deepcopy(cache_updates)
    cu = cu[cu["worker_id"] == target_id]
    
    valid_messages = cu[
        (cu["delete_time"] > timestamp) &
        (cu["insert_time"] <= timestamp) &
        (cu["type"] == "T")
        ]
    valid_messages = valid_messages.sort_values(by="score", ascending=False).reset_index(drop=True)
    top3_messages = valid_messages.head(3)
    valid_messages = valid_messages.drop(top3_messages.index)

    invalid_messages = cu[
        (cu["delete_time"] > timestamp) &
        (cu["insert_time"] <= timestamp) &
        (cu["type"] == "F")
        ]
    invalid_messages = invalid_messages.sort_values(by="score", ascending=False).reset_index(drop=True)
    return top3_messages, valid_messages, invalid_messages


def to_list(df: DataFrame):
    return df["msgID16"].tolist(), df["score"].tolist()


def update_messages(
        id_list: List[str],
        score_List: List[float],
        header: str,
        background_color: str,
        height: str
):
    mg = 20

    children = [
        html.Div(
            children=f"{header}({len(id_list)}):",
            style=dict(
                width="100%",
                paddingLeft=f"{mg}px",
                fontSize="15px",
            )
        )
    ]

    children.extend(
        [
            html.Div(
                className="button",
                children=f"#{id_list[i]} ({round(score_List[i], 3)})",
                style=dict(
                    width=f"calc((100% - {mg * 4}px) / 3)",
                    color="white",
                    backgroundColor=background_color,
                    marginLeft=f"{mg}px",
                    marginTop="10px",
                    padding="5px",
                    borderRadius="5px"
                )
            )
            for i in range(len(id_list))
        ]
    )

    res = html.Div(
        className="hidden-scroll",
        style=dict(
            display="flex",
            justifyContent="flex-start",
            flexWrap="wrap",
            alignContent="flex-start",
            width="100%",
            marginBottom="10px",
            backgroundColor="#efebe5",
            padding="10px 0",
            borderRadius="5px",
            overflow="auto",
            height=height,
        ),
        children=children
    )
    return res


def update_cache_detail(timestamp: int, noMapClick: bool = False, id16: str = None, target_id: str = None):
    tip = html.H2(
        style=dict(
            position="absolute",
            top=0
        ),
        className="h-center",
        children=f"Please Click the Subscription Data Point",
    )

    top3_messages, valid_messages, invalid_messages = get_messages(timestamp, target_id)

    top3_id_list, top3_score_list = to_list(top3_messages)
    valid_id_list, valid_score_list = to_list(valid_messages)
    invalid_id_list, invalid_score_list = to_list(invalid_messages)
    res = html.Div(
        style=dict(
            width="100%",
            height="100%",
            position="relative"
        ),
        children=[
            html.H2(
                className="h-center",
                children=f"Cache #{id16} at {time_format(timestamp)}",
            ),
            update_messages(top3_id_list, top3_score_list, "Top-3 Results", "#8f4c00", "auto"),
            update_messages(valid_id_list, valid_score_list, "Valid Messages", "#bb7b30", "30%"),
            update_messages(invalid_id_list, invalid_score_list, "Invalid Messages", "#b9915f", "40%")
        ]
    )

    if noMapClick:
        res.children = tip
    return res


cache_detail = html.Div(
    id="cache_detail",
    className="components-container",
    style=dict(
        width="100%",
        height="100%",
    ),
    children=update_cache_detail(1477968816)
)

last_click = {}



@app.callback(
    Output('cache_detail', 'children'),
    [
        Input('bar-cache-detail', 'hoverData'),
        Input('bar-cache', 'clickData'),
        Input('map_sub', 'clickData'),
    ]
)
def display_click_data(hoverData, clickData, m_clickData):

    global last_click
    if m_clickData == None:
        return update_cache_detail(0, noMapClick=True)
    target_id = m_clickData['points'][0]['customdata']['targetId']
    id16 = m_clickData['points'][0]['customdata']['ID16']

    if clickData:
        timestamp = clickData['points'][0]['x']
        
        result = cache_info.loc[cache_info['timestamp'] >= timestamp, 'timestamp'].iloc[0]
        
        if clickData != last_click:
            last_click = clickData
            return update_cache_detail(timestamp=result, id16=id16, target_id=target_id)
    if hoverData:
        
        timestamp = hoverData['points'][0]['customdata']
        return update_cache_detail(timestamp=timestamp, id16=id16, target_id=target_id)

    return update_cache_detail(timestamp=1477968816, id16=id16, target_id=target_id)
