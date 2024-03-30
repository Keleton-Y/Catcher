import copy

import plotly.graph_objects as go
from dash import html, dcc
from dash.dependencies import Input, Output

from dao.df import cache_info_merged_minute
from globals.util import timestamp_to_3hour
from globals.variable import BASE_LAYOUT
from globals.variable import app

BASE_LAYOUT = copy.deepcopy(BASE_LAYOUT)
del BASE_LAYOUT["legend"]

df = cache_info_merged_minute

tickText, tickVals = timestamp_to_3hour(df["timestamp"])

highlight_color = ["#CB4335", "#F5B7B1"]

defaultColor = ["#196F3D", "#D4EFDF"]


def update_data(target_id: str):
    global df
    df = cache_info_merged_minute[cache_info_merged_minute["ID"] == target_id]
    df['valid_size'] = df['valid_size'].apply(lambda x: max(0, x - 3))
    bar_data = [
        go.Bar(
            x=df["timestamp"],
            y=df["valid_size"],
            name='valid',
            marker=go.bar.Marker(
                color=[defaultColor[0]] * len(df),
            )
        ),
        go.Bar(
            x=df["timestamp"],
            y=df["invalid_size"],
            name='invalid',
            marker=go.bar.Marker(
                color=[defaultColor[1]] * len(df),
            ),
        ),

    ]
    return bar_data


bar_layout = go.Layout(
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
        range=[tickVals[5] - 3600, tickVals[8] + 3600]
    ),
    
    
    
    
    
    
    
    
    **BASE_LAYOUT
)


bar_cache = html.Div(
    style={
        "width": "100%",
        "height": "100%",
    },
    children=[
        dcc.Graph(
            id="bar-cache",
            responsive=True,
            style={
                "width": "100%",
                "height": "100%",
            }
        )
    ]
)

last_m_click = {}

@app.callback(
    Output('bar-cache', 'figure'),
    [
        Input('bar-cache', 'clickData'),
        Input('map_sub', 'clickData'),
    ]
)
def display_click_data(clickData, m_clickData):
    global last_m_click

    if m_clickData is None:
        return go.Figure(data=[], layout=bar_layout)
    else:
        if m_clickData != last_m_click:
            
            clickData = None
        last_m_click = m_clickData

    target_id = m_clickData['points'][0]['customdata']['targetId']
    bar_figure = go.Figure(data=update_data(target_id), layout=bar_layout)

    if clickData is not None:
        
        idx = clickData['points'][0]['pointIndex']

        
        color0 = [defaultColor[0]] * len(df)
        color0[idx] = highlight_color[0]
        bar_figure.data[0].marker.color = color0

        color1 = [defaultColor[1]] * len(df)
        color1[idx] = highlight_color[1]
        bar_figure.data[1].marker.color = color1

    return bar_figure



