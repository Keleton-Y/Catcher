import feffery_antd_components as fac
from dash import dcc, html
from dash.dependencies import Input, Output, State, ClientsideFunction
from globals.html_id import PAGE_HEADER

header = html.Div(
    style=dict(
        display="flex",
        alignItems="center",
    ),
    children=[
        html.Img(
            src="assets/image/cache.svg",
            style=dict(
                height="35px",
                margin="0 10px 0 20px"
            )
        ),
        html.Span(
            "Catcher",
            style={
                "fontSize": "24px",

            }
        ),
        dcc.Interval(
            id='interval-1s',
            interval=1 * 1000,
            n_intervals=0
        ),
        dcc.Interval(
            id='interval-2s',
            interval=2 * 1000,
            n_intervals=0
        ),
    ]
)
