
import feffery_antd_components as fac
from dash import dcc, html
from dash.dependencies import Input, Output
from dao.df import global_latency_sampled
from globals.util import timestamp_to_3hour
from globals.variable import app


minV, maxV = [global_latency_sampled["timestamp"].min(), global_latency_sampled["timestamp"].max()]
msg_begin, msg_end = [minV, maxV]

tickTexts, tickVals = timestamp_to_3hour(global_latency_sampled["timestamp"])
marksDic = {}

for i in range(len(tickTexts)):
    marksDic[tickVals[i]] = dict(label=tickTexts[i])

slider_time_message = dcc.RangeSlider(
    id='slider_time_message',
    min=minV,
    max=maxV,
    step=60,
    value=[msg_begin, msg_end],
    marks=marksDic,
    vertical=False,
    tooltip={
        "transform": "timeFormat",
        "placement": "top",
        "style": {"color": "white", "fontSize": "20px"}
    },
)

slider_time_transaction = dcc.RangeSlider(
    id='slider_time_transaction',
    min=minV,
    max=maxV,
    step=60,
    value=[minV, maxV],
    marks=marksDic,
    vertical=False,
    tooltip={
        "transform": "timeFormat",
        "placement": "top",
        "style": {"color": "white", "fontSize": "20px"}
    },
)

last_click = {}


@app.callback(
    Output("slider_time_message", "value"),
    [
        Input("scatter_bar_message_update", "selectedData"),
        Input('bar-cache', 'clickData'),
    ]
)
def update_scatter_bar(time_windows_graph_selected, clickData):
    global msg_begin
    global msg_end
    global last_click

    if time_windows_graph_selected is not None:
        nums = [int(point["x"]) for point in time_windows_graph_selected["points"]]
        if len(nums) > 0:
            msg_begin, msg_end = [min(nums), max(nums)]

    if (clickData is not None) and (clickData != last_click):
        
        timestamp = clickData['points'][0]['x']
        last_click = clickData
        return [max(minV, timestamp - 1800), min(maxV, timestamp + 1800)]

    return [msg_begin, msg_end]
