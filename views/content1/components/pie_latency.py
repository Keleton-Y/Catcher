import copy
import random

import plotly.graph_objects as go
import numpy as np
from dash import html, dcc
import plotly.express as px
from globals.variable import BASE_LAYOUT
from globals.variable import app
from dash.dependencies import Input, Output
import feffery_antd_components as fac
from dao.df import global_latency_sampled

pie_latency = html.Div(
    style={
        "width": "100%",
        "height": "100%",
    },
    children=[
        dcc.Graph(
            id="pie_latency",
            responsive=True,
            style={
                "width": "100%",
                "height": "100%",
            }
        )
    ]
)
@app.callback(
    Output('pie_latency', 'figure'),
    Input('slider_time_transaction', 'value'))
def update_output(value):

    df = copy.deepcopy(global_latency_sampled)
    df = df[(df["timestamp"] > value[0]) & (df["timestamp"] < value[1])]

    pie_data = go.Pie(
        labels=["<10ms", "10-100ms", ">100ms"],
        values=[
            len(df[df['latency'] < 1e-2]) * 200 + random.randint(0, 200),
            len(df[(df['latency'] > 1e-2) & (df['latency'] < 1e-1)]) * 200 + random.randint(0, 200),
            len(df[df['latency'] > 1e-1]) * 200 + random.randint(0, 200),
        ],
        showlegend=True,
        marker=go.pie.Marker(
            colors=["rgb(135, 207, 165)", "rgb(253, 185, 106)", "#ffcccc"]
        )

    )

    pie_layout = go.Layout(
        **BASE_LAYOUT,
        title=go.layout.Title(
            y=0.98,
            x=0.5,
            text="Latency Ratio",
            font=go.layout.title.Font(
                family="Microsoft YaHei"
            ),
        )
    )

    pie_figure = go.Figure(
        data=pie_data,
        layout=pie_layout,
    )

    return pie_figure
