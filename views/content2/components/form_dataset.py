import plotly.graph_objects as go
from dash import dcc, html
from globals.variable import BASE_LAYOUT

FONT_SIZE = "17px"

form_dataset = html.Div(
    className="components-container",
    style=dict(
        width="100%",
        height="100%"
    ),
    children=[
        html.Div(
            style=dict(
                width="100%",
            ),
            children=[
                dcc.Dropdown(
                    style=dict(
                        width="100%",
                        height="45px",
                    ),
                    placeholder="Select Databases...",
                    options=[
                        {
                            "label": html.Span(children="Tiny-Scale", style=dict(fontSize=FONT_SIZE)),
                            "value": 0
                        },
                    ],
                    multi=True,
                    value=[0],
                ),
            ]
        ),
        html.Div(
            className="card-border",
            style=dict(
                padding="10px 10px",
                width="100%",
                backgroundColor="white",
                borderRadius="3px"
            ),
            children=[
                html.Span(
                    style=dict(
                        marginRight="20%",
                        fontSize=FONT_SIZE,
                    ),
                    children="Subscriptions 3,002"
                ),
                html.Span(
                    children="Messages: 20,330",
                    style=dict(
                        fontSize=FONT_SIZE,
                    )
                )
            ]
        ),
    ]
)
