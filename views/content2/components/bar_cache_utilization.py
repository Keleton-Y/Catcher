import plotly.graph_objects as go
from dash import dcc, html
from globals.variable import BASE_LAYOUT
from dao.df import all_utilization_ratio
from globals.util import timestamp_to_15min
from globals.variable import app
from dash.dependencies import Input, Output
import dash

colors = ["#2980B9", "#F39C12", "#27AE60"]
tickText, tickVals = timestamp_to_15min(all_utilization_ratio["timestamp"])


time_min_max = [all_utilization_ratio["timestamp"].min(), all_utilization_ratio["timestamp"].max()]
time_range = [time_min_max[0], time_min_max[0] - 1]
x_range = [time_min_max[0] - 180, tickVals[8]]

@app.callback(
    Output('bar-cache-utilization', 'figure'),
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
    
    if time_range[1] > x_range[1]:
        x_range[1] += 600
        x_range[0] += 600

    
    figure = go.Figure(data=update_data(), layout=update_layout())
    return figure


fig = go.Figure()
def update_data():
    df = all_utilization_ratio[
        (all_utilization_ratio["timestamp"] <= time_range[1]) &
        (all_utilization_ratio["timestamp"] >= time_range[0])
        ]


    ratio_data1 = go.Bar(
        x=df["timestamp"],
        y=df["kmax_rate"],
        name='Kmax',
        marker=go.bar.Marker(
            color=colors[0]
        ),
    )

    ratio_data2 = go.Bar(
        x=df["timestamp"],
        y=df["tkrs_rate"],
        name='TKRS',
        marker=go.bar.Marker(
            color=colors[1]
        )
    )

    ratio_data3 = go.Bar(
        x=df["timestamp"],
        y=df["recap_rate"],
        name='ReCap',
        marker=go.bar.Marker(
            color=colors[2]
        )
    )
    return [ratio_data1, ratio_data2, ratio_data3]

def update_layout():
    ratio_layout = go.Layout(
        title=go.layout.Title(
            text='Cache Utilization Ratio (%)',
            x=0.5,
            y=0.92,
            font=go.layout.title.Font(
                family="Microsoft YaHei",
                size=20
            ),
        ),
        xaxis=go.layout.XAxis(
            tickvals=tickVals,
            ticktext=tickText,
            range=x_range,

        ),
        yaxis=go.layout.YAxis(
            tickvals=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
            ticktext=["0", "20%", "40%", "60%", "80%", "100%"],
            gridcolor="lightgrey",
            range=[0, 1.2]
        ),
        plot_bgcolor="#f9f9f9",
        paper_bgcolor='#f9f9f9',

        legend=go.layout.Legend(
            x=0,
            y=0.95,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)',
            orientation="h"
        ),
        margin=go.layout.Margin(
            r=10,
            l=0,
            b=10,
            t=40,
            pad=0,
        ),
        barmode='group',
        bargap=0.4,  
        bargroupgap=0.  
    )
    return ratio_layout

ratio_figure = go.Figure(
    data=update_data(),
    layout=update_layout(),
)

bar_cache_utilization = html.Div(
    style={
        "width": "100%",
        "height": "100%",
    },
    children=[
        dcc.Graph(
            id="bar-cache-utilization",
            className="my-graph",
            figure=ratio_figure,
            responsive=True,
            style={
                "width": "100%",
                "height": "100%",
            }
        )
    ]
)
