import plotly.graph_objects as go
from dash import dcc, html
from globals.variable import BASE_LAYOUT

years = [1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,
         2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012]

fig = go.Figure()
ratio_data1 = go.Bar(
    x=years,
    y=[219, 146, 112, 127, 124, 180, 236, 207, 236, 263,
       350, 430, 474, 526, 488, 537, 500, 439],
    name='Rest of world',
    marker=go.bar.Marker(
        color='rgb(55, 83, 109)'
    )
)

ratio_data2 = go.Bar(
    x=years,
    y=[16, 13, 10, 11, 28, 37, 43, 55, 56, 88, 105, 156, 270,
       299, 340, 403, 549, 499],
    name='China',
    marker=go.bar.Marker(
        color='rgb(55, 83, 109)'
    )
)

ratio_layout = go.Layout(
    title='US Export of Plastic Scrap',
    xaxis=go.layout.XAxis(
        tickfont=go.layout.xaxis.Tickfont(
            size=14
        )
    ),
    yaxis=go.layout.YAxis(
        tickfont=go.layout.yaxis.Tickfont(
            size=14
        ),
        title=go.layout.yaxis.Title(
            text='USD (millions)',
            font=go.layout.yaxis.title.Font(
                size=14,
                family="Microsoft YaHei"
            )
        )
    ),
    paper_bgcolor='rgba(255, 255, 255, 0)',
    legend=go.layout.Legend(
        x=0,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
    ),
    margin=go.layout.Margin(
        r=10,
        l=0,
        b=10,
        t=40,
        pad=0,
    ),
    barmode='group',
    bargap=0.15,  
    bargroupgap=0.1  
)

ratio_figure = go.Figure(
    data=[ratio_data1, ratio_data2],
    layout=ratio_layout
)

response_time_ratio = html.Div(
    style={
        "width": "100%",
        "height": "100%",
    },
    children=[
        dcc.Graph(
            figure=ratio_figure,
            responsive=True,
            style={
                "width": "100%",
                "height": "100%",
            }
        )
    ]
)
