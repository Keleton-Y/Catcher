import copy

import dash
import plotly.graph_objects as go
from dash import dcc, html
from globals.variable import BASE_LAYOUT
from dao.df import all_computational_time
from globals.util import timestamp_to_15min
from globals.variable import app
from dash.dependencies import Input, Output
from service.algorithm.main.env import *

BASE_LAYOUT = copy.deepcopy(BASE_LAYOUT)
del BASE_LAYOUT["legend"]
tickTexts, tickVals = timestamp_to_15min(all_computational_time["timestamp"])

colors = ["#2980B9", "#F39C12", "#27AE60"]


env = scEnv(learn=False)
time_min_max = [all_computational_time["timestamp"].min(), all_computational_time["timestamp"].max()]
time_range = [time_min_max[0], time_min_max[0] - 1]
x_range = [time_min_max[0], tickVals[3]]


@app.callback(
    Output('line-cost', 'figure'),
    [Input('interval-2s', 'n_intervals'),
     Input('perform-button', 'nClicks')]
)
def update(n, n_clicks):
    global time_range, x_range

    
    if n_clicks is None or n_clicks == 0:
        return dash.no_update

    if time_range[1] > time_min_max[1]:
        return dash.no_update

    time_range[1] += 600
    x_range[1] = max(x_range[1], time_range[1])

    
    figure = go.Figure(data=update_data(), layout=update_layout())
    return figure


def get_markers():
    return go.scatter.Marker(
        size=4
    )


def update_data():
    df = all_computational_time[
        (all_computational_time["timestamp"] <= time_range[1]) &
        (all_computational_time["timestamp"] >= time_range[0])
        ]
    line_data1 = go.Scatter(
        mode="lines+markers",
        name="Kmax",
        x=df["timestamp"],
        y=df["kmax_cost"],
        line=go.scatter.Line(
            color=colors[0]
        ),
        marker=get_markers(),
    )

    line_data2 = go.Scatter(
        mode="lines+markers",
        name="TKRS",
        x=df["timestamp"],
        y=df["tkrs_cost"],
        line=go.scatter.Line(
            color=colors[1]
        ),
        marker=get_markers()
    )

    line_data3 = go.Scatter(
        mode="lines+markers",
        name="Recap",
        x=df["timestamp"],
        y=df["recap_cost"],
        line=go.scatter.Line(
            color=colors[2]
        ),
        marker=get_markers(
        )
    )
    return [line_data1, line_data2, line_data3]


def update_layout():
    line_layout = go.Layout(
        **BASE_LAYOUT,
        xaxis=go.layout.XAxis(
            tickvals=tickVals,
            ticktext=tickTexts,
            range=x_range
        ),
        yaxis=go.layout.YAxis(
            range=[-50, 500],
            gridcolor="lightgrey"
        ),
        legend=go.layout.Legend(
            x=0,
            y=1.01,
            orientation="h",
        ),
        title=go.layout.Title(
            text="Computational Time Cost (ms)",
            x=0.5,
            font=go.layout.title.Font(
                family="Microsoft YaHei",
                size=20,
            ),
        )
    )
    return line_layout


line_figure = go.Figure(
    data=update_data(),
    layout=update_layout()
)

line_cost = html.Div(
    style={
        "width": "100%",
        "height": "100%",
    },
    children=[
        dcc.Graph(
            id="line-cost",
            className="my-graph",
            figure=line_figure,
            responsive=True,
            style={
                "width": "100%",
                "height": "100%",
            }
        )
    ]
)
