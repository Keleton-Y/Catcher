from dash import dcc, html
from typing import List
import plotly.graph_objs as go
from globals import html_id
from globals.variable import BASE_LAYOUT
from dao.df import msg_info
from globals.variable import app
from dash.dependencies import Output, Input

msg_info = msg_info.sample(frac=0.3)


mapbox_access_token = "pk.eyJ1Ijoid2lsbGFyZC1zbmF5IiwiYSI6ImNrdjZsejd1YjAwdnQzMnI1bWVvZWhzdHQifQ.Z9z2Hoj6TS_sfouvBKP_OA"


map_msg = html.Div(
    style={
        "width": "100%",
        "height": "100%",
    },
    children=[
        dcc.Graph(
            id="map_msg",
            responsive=True,
            style={
                "width": "100%",
                "height": "100%",
            }
        )
    ]
)


last_begin = 0
last_end = 0
last_highlight_percent = 0
last_marker_size = 5





def update_data(begin=None, end=None, highlight_percent=None, marker_size=None) -> List[go.Scattermapbox]:
    global last_begin
    global last_end
    global last_highlight_percent
    global last_marker_size

    begin = begin if begin is not None else last_begin
    end = end if end is not None else last_end
    highlight_percent = highlight_percent if highlight_percent is not None else last_highlight_percent
    marker_size = marker_size if marker_size is not None else last_marker_size

    last_begin = begin
    last_end = end
    last_highlight_percent = highlight_percent
    last_marker_size = marker_size

    
    df = msg_info[(msg_info["expire_time"] > begin) & (msg_info["start_time"] < end)]

    pub_df1 = df[df["expire_time"] < end]

    df = df[df["expire_time"] >= end]

    
    
    df = df.sort_values(by="update_triggerd_insert")
    
    threshold = df["update_triggerd_insert"].quantile(1 - highlight_percent / 100)
    pub_df3 = df[df["update_triggerd_insert"] > threshold]

    
    pub_df2 = df[df["update_triggerd_insert"] <= threshold]

    pub_dfs = [pub_df1, pub_df2, pub_df3]
    names = ["Expired", "Arrived", "HighLight"]
    colors = ["#999999", "#009933", "#FFA500"]
    query_data = []

    for i in range(3):
        df = pub_dfs[i]
        df["color"] = colors[i]
        query_data.append(
            go.Scattermapbox(
                lon=df["longitude"],
                lat=df["latitude"],
                text=[
                    f"ID: {row['ID16']}<br>" +
                    f"Arrived_time: {row['start_time']}<br>" +
                    f"Affected_subscriptions_count: {row['update_triggerd_insert']}<br>"
                    for index, row in df.iterrows()
                ],
                name=names[i],
                marker=go.scattermapbox.Marker(
                    size=marker_size,
                    opacity=0.6,
                    color=df["color"],
                ),
                hoverinfo="text",
            )
        )

    return query_data


last_zoom = 10
last_lat = 30.66
last_lon = 104.07



def update_layout(
        zoom=None,
        lat=None,
        lon=None,
) -> go.Layout:
    global last_lon, last_lat, last_zoom

    zoom = zoom if zoom is not None else last_zoom
    lat = lat if lat is not None else last_lat
    lon = lon if lon is not None else last_lon

    last_lon = lon
    last_lat = lat
    last_zoom = zoom

    map_layout = go.Layout(
        **BASE_LAYOUT,
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            center=dict(
                lat=lat,
                lon=lon,
            ),
            zoom=zoom,


        ),
        title=go.layout.Title(
            text="Message",
            font=go.layout.title.Font(
                family="Microsoft YaHei"
            ),
            x=0.5,
            y=0.98,
        ),

    )
    return map_layout


last_clickData = {}


@app.callback(
    Output("map_msg", "figure"),
    [
        Input("slider_time_message", "value"),
        Input("highlight-percent", "value"),
        Input('map_sub', 'clickData'),
        Input('map_msg', 'relayoutData'),
        Input('dataset-dropdown', "value")
    ]
)
def update_by_slider(st, hp, clickData, relayoutData, value):
    
    global last_clickData


    if hp is not None and hp != "":
        hp = float(hp)
    else:
        hp = 0

    update_data(begin=st[0], end=st[1], highlight_percent=hp, marker_size=5)
    update_layout(zoom=10, lat=30.66, lon=104.07)


    if (clickData is not None) and (clickData != last_clickData):
        last_clickData = clickData
        update_layout(
            zoom=13.5,
            lon=clickData['points'][0]['lon'],
            lat=clickData['points'][0]['lat'],
        )

    elif relayoutData is not None:

        if 'mapbox.zoom' in relayoutData:
            update_layout(zoom=relayoutData['mapbox.zoom'])
        if 'mapbox.center' in relayoutData:
            update_layout(lon=relayoutData['mapbox.center']['lon'], lat=relayoutData['mapbox.center']['lat'])

    layout = update_layout()
    data = update_data(marker_size=5 + (layout.mapbox.zoom - 10) * 2.2)
    map_figure = go.Figure(data=data, layout=layout)

    if len(value) == 0:
        return go.Figure(data=[], layout=map_figure.layout)

    return map_figure
