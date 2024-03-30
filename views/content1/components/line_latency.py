import copy

import pandas as pd
from dash.dependencies import Input, Output
from globals.variable import app
import plotly.graph_objects as go
import numpy as np
from dash import html, dcc
from globals.variable import BASE_LAYOUT
from dao.df import global_latency_merged
from globals.util import timestamp_to_3hour
from views.content1.components.form_sliders import minV, maxV

BASE_LAYOUT = copy.deepcopy(BASE_LAYOUT)

del BASE_LAYOUT["legend"]


def update_data(
        start: int = 0,
        end: int = 1e18,
):
    df = copy.deepcopy(global_latency_merged)
    df = df[(df["timestamp"] > start) & (df["timestamp"] < end)]

    data1 = df[df["latency"] == "<10ms"].reset_index(drop=True)
    data2 = df[df["latency"] == "10-100ms"].reset_index(drop=True)
    data2["ratio"] = data1["ratio"] + data2["ratio"]
    data3 = df[df["latency"] == ">100ms"].reset_index(drop=True)
    data3["ratio"] = data2["ratio"] + data3["ratio"]

    bar_data = [
        go.Scatter(
            mode="lines",
            x=data1["timestamp"],
            y=data1["ratio"],
            line=go.scatter.Line(shape='spline'),
            name='<10ms',
            marker=go.scatter.Marker(
                color="#8ECFC9",
            ),
            fill="tozeroy",
        ),
        go.Scatter(
            mode="lines",
            x=data2["timestamp"],
            y=data2["ratio"],
            line=go.scatter.Line(shape='spline'),
            name='10-100ms',
            marker=go.scatter.Marker(
                color="#FFBE7A",
            ),
            fill="tonexty",
        ),
        go.Scatter(
            mode="lines",
            x=data3["timestamp"],
            y=data3["ratio"],
            line=go.scatter.Line(shape='spline'),
            name='>100ms',
            marker=go.scatter.Marker(
                color="#FA7F6F",
            ),
            fill="tonexty",
        ),
    ]

    return bar_data


def update_layout():
    tickText, tickVals = timestamp_to_3hour(global_latency_merged["timestamp"])

    bar_layout = go.Layout(
        title=go.layout.Title(
            font=go.layout.title.Font(
                family="Microsoft YaHei"
            ),
            text="Response time ratio",
            x=0.5,
        ),
        legend=go.layout.Legend(
            font=go.layout.legend.Font(size=12),
            orientation="h",
            x=0.5,
            y=1.02,
        ),
        xaxis=go.layout.XAxis(
            ticktext=tickText,
            tickvals=tickVals,
        ),
        yaxis=go.layout.YAxis(
            ticktext=["0%", "20%", "40%", "60%", "80%", "100%"],
            tickvals=[0, 0.2, 0.4, 0.6, 0.8, 1.]
        ),
        **BASE_LAYOUT
    )
    return bar_layout






def update_output(value):
    bar_data = update_data(value[0], value[1])
    bar_layout = update_layout()

    bar_figure = go.Figure(data=bar_data, layout=bar_layout)

    return bar_figure


line_latency = html.Div(
    style={
        "width": "100%",
        "height": "100%",
    },
    children=[
        dcc.Graph(
            id="bar_latency",
            responsive=True,
            style={
                "width": "100%",
                "height": "100%",
            },
            figure=update_output([minV, maxV])
        )
    ]
)
