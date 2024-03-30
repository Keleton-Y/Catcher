import copy
from typing import List
from globals.variable import app
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
from dash import dcc, html
import plotly.graph_objs as go
from globals import html_id
from globals.variable import BASE_LAYOUT
from dao.df import sub_info

sub_info = copy.deepcopy(sub_info)
sub_info = sub_info[sub_info["utilization_ratio"] >= 0.001]
sub_info = sub_info.sort_values(by="average_cost")


mapbox_access_token = "pk.eyJ1Ijoid2lsbGFyZC1zbmF5IiwiYSI6ImNrdjZsejd1YjAwdnQzMnI1bWVvZWhzdHQifQ.Z9z2Hoj6TS_sfouvBKP_OA"

cache_utilization_ratio = 0
refill_frequency = 0
refill_frequency_checkbox = False
and_or = "OR"
update_cost_top_ratio = 0
update_cost_top_ratio_checkbox = False

last_marker_size = 0


def update_data(marker_size: float | None = None):
    global last_marker_size
    if marker_size is None:
        marker_size = last_marker_size
    last_marker_size = marker_size

    colors = ["#999999", "#23AE00"]
    names = ["Unfiltered", "Filtered"]

    sb = sub_info

    if update_cost_top_ratio_checkbox:
        sb = sb.head(int(len(sb) * update_cost_top_ratio / 100)).copy()

    if refill_frequency_checkbox and (and_or == "OR"):
        filtered = sb[
            (sb["utilization_ratio"] <= cache_utilization_ratio / 100) |
            (sb["refill_times"] >= refill_frequency)
            ]
    elif refill_frequency_checkbox and (and_or == "AND"):
        filtered = sb[
            (sb["utilization_ratio"] <= cache_utilization_ratio / 100) &
            (sb["refill_times"] >= refill_frequency)
            ]
    else:
        filtered = sb[sb["utilization_ratio"] <= cache_utilization_ratio / 100]

    unfiltered = sub_info.drop(filtered.index, axis=0)

    df = [unfiltered, filtered]

    data = []

    for i in range(2):
        data.append(
            go.Scattermapbox(
                lon=df[i]["longitude"],
                lat=df[i]["latitude"],
                text=[
                    f"ID: {row['ID16']}  k_num: {row['k']}<br>" +
                    f"Location: (Lat: {round(row['latitude'], 5)}, Lnt: {round(row['longitude'], 5)})<br>" +
                    f"Update_times: {row['update_times']}<br>" +
                    f"Utilization_ratio: {round(row['utilization_ratio'] * 100, 2)}%<br>" +
                    f"Average_update_cost: {round(row['average_cost'] * 1000, 2)}ms"
                    for index, row in df[i].iterrows()
                ],

                name=names[i],
                marker=go.scattermapbox.Marker(
                    size=marker_size,
                    opacity=0.6,
                    color=colors[i],
                ),
                customdata=[
                    dict(
                        targetId=row["target_id"],
                        ID16=row["ID16"],
                    )
                    for index, row in df[i].iterrows()
                ],
                
                hoverinfo="text"
            )
        )

    return data



map_layout = go.Layout(
    **BASE_LAYOUT,
    mapbox=go.layout.Mapbox(
        accesstoken=mapbox_access_token,
        center=dict(
            lat=30.66,
            lon=104.07
        ),
        zoom=10,
        style="light"
    ),
    title=go.layout.Title(
        text="Subscription",
        font=go.layout.title.Font(
            family="Microsoft YaHei"
        ),
        y=0.98,
        x=0.5,
    ),
    showlegend=True,
)


@app.callback(
    Output('map_sub', 'figure'),
    [
        Input('cache_utilization_ratio', 'value'),
        Input('refill_frequency', 'value'),
        Input('refill_frequency_checkbox', 'checked'),
        Input('map_sub', 'relayoutData'),
        Input('dataset-dropdown', "value"),
        Input('refill-frequency-and-or', "value"),
        Input("update-cost-top-ratio", "value"),
        Input("update-cost-top-ratio-checkbox", "checked")
    ]
)
def update_map_sub(cur, rf, rfc, relayoutData, dd, rfao, uctr, uctrc):
    global cache_utilization_ratio
    global refill_frequency_checkbox
    global refill_frequency
    global map_layout
    global and_or
    global update_cost_top_ratio
    global update_cost_top_ratio_checkbox

    if cur is not None and cur != "":
        cache_utilization_ratio = float(cur)

    refill_frequency_checkbox = rfc

    and_or = rfao

    update_cost_top_ratio_checkbox = uctrc
    if uctrc:
        if (uctr is not None) and (uctr != ""):
            update_cost_top_ratio = float(uctr)
        else:
            update_cost_top_ratio_checkbox = False

    if rfc:
        if (rf is not None) and (rf != ""):
            refill_frequency = float(rf)
        else:
            refill_frequency_checkbox = False

    if relayoutData is not None:
        if 'mapbox.zoom' in relayoutData:
            map_layout.mapbox.zoom = relayoutData['mapbox.zoom']
        if 'mapbox.center' in relayoutData:
            map_layout.mapbox.center.lon = relayoutData['mapbox.center']['lon']
            map_layout.mapbox.center.lat = relayoutData['mapbox.center']['lat']

    data = update_data(marker_size=5 + (map_layout.mapbox.zoom - 10) * 2.2)
    map_figure = go.Figure(data=data, layout=map_layout)

    if len(dd) == 0:
        map_figure.data = []

    return map_figure


@app.callback(
    Output('sub-filter-count', 'children'),
    [
        Input('cache_utilization_ratio', 'value'),
        Input('refill_frequency', 'value'),
        Input('refill_frequency_checkbox', 'checked'),
        Input('interval-1s', 'n_intervals'),
        Input('dataset-dropdown', "value")
    ]
)
def update_sub_filter_count(cur, rf, rfc, n_intervals, value):
    data = update_data()
    num = len(data[1].lon)
    if len(value) == 0:
        num = 0
    return f"Get {num} Subscriptions"


@app.callback(
    Output('sub-msg-count', 'children'),
    [
        Input('dataset-dropdown', "value")
    ]
)
def update_sub_filter_count(value):
    if len(value) == 0:
        return "0 subscriptions, 0 messages"
    return f"31,081 subscriptions, 206,423 messages"



map_sub = html.Div(
    style={
        "width": "100%",
        "height": "100%",
    },
    children=[
        dcc.Graph(
            id="map_sub",
            responsive=True,
            style={
                "width": "100%",
                "height": "100%",
            }
        ),
    ]
)
