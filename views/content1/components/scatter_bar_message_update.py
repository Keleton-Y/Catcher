import copy
import numpy as np
import plotly.graph_objects as go
import numpy as np
from dash import html, dcc
from globals.variable import BASE_LAYOUT
from dao.df import msg_info_merged_minute
from globals.util import timestamp_to_hour
from globals.variable import app
from dash.dependencies import Output, Input

BASE_LAYOUT = copy.deepcopy(BASE_LAYOUT)
del BASE_LAYOUT['margin']
del BASE_LAYOUT['legend']
BASE_LAYOUT = copy.deepcopy(BASE_LAYOUT)

msg_info = msg_info_merged_minute

msg_info = copy.deepcopy(msg_info).reset_index(drop=True)

ticktext, tickvals = timestamp_to_hour(
    np.arange(msg_info["start_time"].min(), msg_info["start_time"].max() + 3600, 3600).tolist()
)

ticktext = ticktext[::3]
tickvals = tickvals[::3]

scatter_bar_message_update = html.Div(
    style={
        "width": "100%",
        "height": "100%",
    },
    children=[
        dcc.Graph(
            id="scatter_bar_message_update",
            responsive=True,
            style={
                "width": "100%",
                "height": "100%",
            }
        )
    ]
)


@app.callback(
    Output("scatter_bar_message_update", "figure"),
    [
        Input("slider_time_message", "value"),
        Input('dataset-dropdown', "value"),
    ]
)
def update_by_slider(value, value1):
    time_begin, time_end = [value[0], value[1]]

    
    bar_colors = []

    
    scatter_colors = []

    for i in range(msg_info.shape[0]):
        if time_begin <= int(msg_info["start_time"][i]) < time_end:
            
            
            
            
            bar_colors.append("rgb(235, 152, 78)")
            scatter_colors.append("rgb(36, 113, 163)")
        else:
            
            
            bar_colors.append("rgba(235, 152, 78 , 0.2)")
            scatter_colors.append("rgba(36, 113, 163 ,0.2)")

    bar_data = go.Bar(
        x=msg_info["start_time"],
        y=msg_info["count"],
        name="message",
        yaxis='y2',
        marker=go.bar.Marker(color=bar_colors),
    )

    scatter_data = go.Scatter(
        mode="markers",
        x=msg_info["start_time"],
        y=msg_info["update_triggerd_insert"] + msg_info["update_triggered_delete"],
        name="update",
        
        opacity=1,
        marker=go.scatter.Marker(color=scatter_colors),
    )

    scatter_bar_data = [scatter_data, bar_data]

    scatter_bar_layout = go.Layout(
        **BASE_LAYOUT,
        title=go.layout.Title(
            text="Message & Update Number Per 10min",
            font=go.layout.title.Font(
                family="Microsoft YaHei"
            ),
            x=0.5
        ),
        dragmode="select",
        showlegend=True,
        margin=go.layout.Margin(l=10, r=10, b=0, t=30, pad=0),
        legend=go.layout.Legend(
            font=go.layout.legend.Font(size=12),
            orientation="h",
            x=0,
            y=1
        ),
        xaxis=go.layout.XAxis(
            
            tickmode='array',
            tickvals=tickvals,
            ticktext=ticktext,
        ),
        yaxis=go.layout.YAxis(
            side='right',
            color='rgb(36, 113, 163)',
            gridcolor="#f9f9f9",
            range=[0, 180000],
        ),
        
        yaxis2=go.layout.YAxis(
            overlaying='y',
            side='left',
            color="rgb(235, 152, 78)",
            gridcolor="#f9f9f9",
            range=[0, 700]
        ),
    )

    scatter_bar_figure = go.Figure(
        data=scatter_bar_data,
        layout=scatter_bar_layout
    )

    if len(value1) == 0:
        scatter_bar_figure.data = []

    return scatter_bar_figure
