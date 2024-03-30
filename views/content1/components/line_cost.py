import copy
import random

import plotly.graph_objects as go
from dash import dcc, html
from globals.variable import app
from dash.dependencies import Input, Output
from globals.util import timestamp_to_3hour
from globals.variable import BASE_LAYOUT
from dao.df import global_time_cost
import numpy as np
from views.content1.components.form_sliders import minV, maxV

BASE_LAYOUT = copy.deepcopy(BASE_LAYOUT)
del BASE_LAYOUT["legend"]


def update_output(value):
    df = copy.deepcopy(global_time_cost)
    df = df[(df["timestamp"] > value[0]) & (df["timestamp"] < value[1])]

    ticktext, tickvals = timestamp_to_3hour(
        np.arange(
            df["timestamp"].min(),
            df["timestamp"].max() + 3600, 3600
        ).tolist()
    )

    line_data = [
        go.Scatter(
            mode="lines+markers",
            name="performance",
            x=df["timestamp"],
            y=df["high_cost"] / 1000,
            marker=go.scatter.Marker(
                color="#7cb79d",
                size=4,
            )
        ),
        go.Scatter(
            mode="lines+markers",
            name="lower bound",
            x=df["timestamp"],
            y=df["low_cost"] / 1000,
            marker=go.scatter.Marker(
                color="#EC7063",
                size=4,
            )
        )
    ]

    line_layout = go.Layout(
        **BASE_LAYOUT,
        title=go.layout.Title(
            text="Response Time (s) ",
            x=0.5,
            font=go.layout.title.Font(
                family="Microsoft YaHei"
            ),
        ),
        xaxis=go.layout.XAxis(
            tickvals=tickvals,
            ticktext=ticktext,
            gridcolor="lightgrey",
            range=[tickvals[4] - 3600, tickvals[7] + 3600]
        ),
        yaxis=go.layout.YAxis(
            gridcolor="#f9f9f9"
        ),
        legend=go.layout.Legend(
            x=0.02,
            y=1,
            orientation="h",
        )
    )

    line_figure = go.Figure(
        data=line_data,
        layout=line_layout
    )

    return line_figure


line_cost = html.Div(
    style={
        "width": "100%",
        "height": "100%",
    },
    children=[
        dcc.Graph(
            id="line_cost",
            responsive=True,
            style={
                "width": "100%",
                "height": "100%",
            },
            figure=update_output([minV, maxV])
        )
    ]
)


@app.callback(
    Output("line_cost", "figure"),
    [
        Input('dataset-dropdown', "value")
    ]
)
def update_by_slider(value):
    res = update_output([minV, maxV])
    if len(value) == 0:
        res.data = []
    return res
