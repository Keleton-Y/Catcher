import copy

import dash

from globals.variable import app
import plotly.graph_objects as go
from dash import dcc, html
from globals.variable import BASE_LAYOUT
from dao.df import all_memory_costs
from globals.util import timestamp_to_15min, timestamp_to_2min
from dash.dependencies import Input, Output

BASE_LAYOUT = copy.deepcopy(BASE_LAYOUT)
del BASE_LAYOUT["legend"]

tickText, tickVals = timestamp_to_15min(all_memory_costs["timestamp"])
colors = ["#2980B9", "#F39C12", "#27AE60"]



time_min_max = [all_memory_costs["timestamp"].min(), all_memory_costs["timestamp"].max()]
time_range = [time_min_max[0], time_min_max[0] - 1]
x_range = [time_min_max[0], tickVals[3]]


@app.callback(
    Output('line-memory', 'figure'),
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


def update_data():
    df = all_memory_costs[
        (all_memory_costs["timestamp"] >= time_range[0]) &
        (all_memory_costs["timestamp"] <= time_range[1])
    ]
    line_data1 = go.Scatter(
        mode="lines",
        name="Kmax",
        x=df["timestamp"],
        y=df["kmax_cost"],
        line=go.scatter.Line(
            color=colors[0]
        ),
    )

    line_data2 = go.Scatter(
        mode="lines",
        name="TKRS",
        x=df["timestamp"],
        y=df["skype_cost"],
        line=go.scatter.Line(
            color=colors[1]
        ),
    )

    line_data3 = go.Scatter(
        mode="lines",
        name="Recap",
        x=df["timestamp"],
        y=df["trks_cost"],
        line=go.scatter.Line(
            color=colors[2]
        ),
    )

    return [line_data1, line_data2, line_data3]


def update_layout():
    line_layout = go.Layout(
        **BASE_LAYOUT,

        xaxis=go.layout.XAxis(
            ticktext=tickText,
            tickvals=tickVals,
            range=x_range
        ),
        yaxis=go.layout.YAxis(
            gridcolor="lightgrey",
        ),
        legend=go.layout.Legend(
            x=0,
            y=1.01,
            orientation="h",
        ),
        title=go.layout.Title(
            text="Memory Consumption (Byte)",
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

line_memory = html.Div(
    style={
        "width": "100%",
        "height": "100%",
    },
    children=[
        dcc.Graph(
            className="my-graph",
            figure=line_figure,
            id="line-memory",
            responsive=True,
            style={
                "width": "100%",
                "height": "100%",
            }
        )
    ]
)



