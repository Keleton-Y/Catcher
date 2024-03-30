import copy
import datetime
import uuid

import plotly.graph_objects as go
from dash import html, dcc
from dash.dependencies import Input, Output

from dao.df import cache_info
from globals.util import timestamp_to_1min
from globals.variable import BASE_LAYOUT
from globals.variable import app


def format(timestamp: int):
    if timestamp % 60 != 0:
        return ""
    dt = datetime.datetime.fromtimestamp(timestamp)
    return f"{dt.hour:02d}: {dt.minute:02d}"


BASE_LAYOUT = copy.deepcopy(BASE_LAYOUT)
del BASE_LAYOUT["legend"]

tickText, tickVals = [], []
x_range = []

highlight_color = ["#CB4335", "#F5B7B1"]

default_color = ["#17A589", "#D5F5E3"]


def update_data(
        target_id: str = None,
        start_t: int = 1477961012,
        end_t: int = 1477961012 + 600,
):
    global tickText, tickVals, x_range

    df = copy.deepcopy(cache_info)

    df = df[df["ID"] == target_id]

    df['valid_size'] = df['valid_size'].apply(lambda x: max(0, x - 3))

    df = df[(df["timestamp"] >= start_t) & (df["timestamp"] < end_t)]

    tickText, tickVals = timestamp_to_1min(df["timestamp"])

    time_set = set()

    x_values = []

    
    for index, row in df.iterrows():
        ts = row['timestamp']
        ts -= ts % 60
        if ts in time_set:
            x_values.append(f"000000000000000000{uuid.uuid4()}")
        else:
            time_set.add(ts)
            x_values.append(format(ts))

    tickVals = x_values
    
    tickText = [xv if len(xv) < 10 else "" for xv in x_values]

    x_range = [0, min(66, len(x_values))]

    bar_data = [
        go.Bar(
            x=x_values,
            y=df["valid_size"],
            name='valid',
            marker=go.bar.Marker(
                color=default_color[0],
            ),
            customdata=df["timestamp"],
        ),
        go.Bar(
            x=x_values,
            y=df["invalid_size"],
            name='invalid',
            marker=go.bar.Marker(
                color=default_color[1],
            ),
            customdata=df["timestamp"],
        ),
    ]

    return bar_data


def update_layout():
    bar_layout = go.Layout(
        bargap=0.2,
        barmode='stack',
        legend=go.layout.Legend(
            font=go.layout.legend.Font(size=12),
            orientation="h",
            x=0,
            y=1.1,
        ),
        xaxis=go.layout.XAxis(
            ticktext=tickText,
            tickvals=tickVals,
            range=x_range
        ),
        **BASE_LAYOUT
    )
    return bar_layout


bar_figure = go.Figure(data=update_data(), layout=update_layout())

bar_cache_detail = html.Div(
    style={
        "width": "100%",
        "height": "100%",
    },
    children=[
        dcc.Graph(
            id="bar-cache-detail",
            figure=bar_figure,
            responsive=True,
            style={
                "width": "100%",
                "height": "100%",
            }
        )
    ]
)

last_click = {}

last_m_click = {}
last_hover = {}

target_id = ""
ts = 1477968816


idx = -1

last_data = None
@app.callback(
    Output('bar-cache-detail', 'figure'),
    [
        Input('bar-cache', 'clickData'),
        Input('bar-cache-detail', 'hoverData'),
        Input('map_sub', 'clickData'),
    ]
)
def display_click_data(clickData, hoverData, m_clickData):
    global bar_figure, default_color, last_click, last_m_click, last_hover, target_id, ts, idx, last_data

    bar_data = last_data

    if m_clickData is None:
        return go.Figure(data=[], layout=update_layout())

    if (m_clickData is not None) and (m_clickData != last_m_click):
        target_id = m_clickData['points'][0]['customdata']['targetId']
        last_m_click = m_clickData
        idx = -1
        bar_data = update_data(start_t=ts, end_t=ts + 600, target_id=target_id)

    if (hoverData is not None) and hoverData != last_hover:
        
        idx = hoverData['points'][0]['pointIndex']
        last_hover = hoverData

    if (clickData is not None) and (clickData != last_click):
        
        ts = clickData['points'][0]['x']
        last_click = clickData
        idx = -1
        bar_data = update_data(start_t=ts, end_t=ts + 600, target_id=target_id)

    if bar_data is None:
        bar_data = update_data(start_t=ts, end_t=ts + 600, target_id=target_id)

    last_data = bar_data
    bar_figure = go.Figure(data=bar_data, layout=update_layout())
    if idx >= 0:
        
        color0 = [default_color[0]] * len(tickText)
        color0[idx] = highlight_color[0]
        bar_figure.data[0].marker.color = color0

        color1 = [default_color[1]] * len(tickText)
        color1[idx] = highlight_color[1]
        bar_figure.data[1].marker.color = color1

    return bar_figure
