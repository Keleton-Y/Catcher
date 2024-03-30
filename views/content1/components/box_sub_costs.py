import copy
from globals.util import timestamp_to_hour
import plotly.graph_objects as go
import numpy as np
from dash import html, dcc
from globals.variable import BASE_LAYOUT
from dao.df import sub_costs

BASE_LAYOUT = copy.deepcopy(BASE_LAYOUT)
del BASE_LAYOUT['legend']
del BASE_LAYOUT['margin']

sub_costs = copy.deepcopy(sub_costs)
sub_costs["timestamp"] = sub_costs["timestamp"] - sub_costs["timestamp"] % 3600
sub_costs["update_cost"] = sub_costs["update_cost"] * 1000

tickText, tickVals = timestamp_to_hour(sub_costs["timestamp"])


c = ['hsl(' + str(h) + ',50%' + ',50%)' for h in np.linspace(0, 360, len(tickVals))]

box_plot_data = [
    go.Box(
        y=sub_costs[sub_costs["timestamp"] == tickVals[i]]["update_cost"],
        marker=dict(
            color=c[i],
        ),
        name=tickText[i],
    )
    for i in range(len(tickText))
]

box_plot_layout = go.Layout(
    **BASE_LAYOUT,
    xaxis=go.layout.XAxis(
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        ticktext=tickText
    ),
    margin=go.layout.Margin(l=30, r=10, b=0, t=30, pad=0),
    yaxis=dict(zeroline=False, gridcolor='lightgrey'),
    title="Average update cost (ms)"
)

box_plot_figure = {'data': box_plot_data, 'layout': box_plot_layout}

box_sub_costs = html.Div(
    style={
        "width": "100%",
        "height": "100%",
    },
    children=[
        dcc.Graph(
            figure=box_plot_figure,
            responsive=True,
            style={
                "width": "100%",
                "height": "100%",
            }
        )
    ]
)
