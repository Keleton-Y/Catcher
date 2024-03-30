import uuid

import plotly.graph_objects as go
from dash import dcc, html
from globals.variable import BASE_LAYOUT
import feffery_antd_components as fac
from datetime import datetime
from globals.variable import app
from dash.dependencies import Input, Output
import feffery_utils_components as fuc


class Info_Parameters:
    def __init__(self, max_threshold_score, k_num):
        self.max_threshold_score = max_threshold_score
        self.k_num = k_num


class Info_Colors:
    def __init__(self, lines_color, bar_color):
        self.lines_color = lines_color
        self.bar_color = bar_color


class Info_Cache:
    def __init__(self, id, name, description, parameters: Info_Parameters, colors: Info_Colors):
        self.id = id
        self.name = name
        self.description = description
        self.parameters = parameters
        self.colors = colors


style_l1 = dict(
    fontSize="larger",
    margin="5px 0",
)

style_l2 = dict(
    paddingLeft="30px",
    fontSize="larger",
    margin="5px 0",
    display="flex",
    alignItems="center"
)

style_icon1 = dict(
    marginRight="5px",
    color="#05B9E2",
)
style_icon2 = dict(
    marginRight="5px",
    color="#FFBE7A",
)

style_input = dict(width="180px", display="inline-block", marginLeft="10px")

names = ["Recap", "TkRS", "kmax"]

ids = ["1", "2", "3"]

descriptions = [
    "(Default model) Our deep reinforcement learning based method.",
    "(Default model) A two-level cache model with k-skyband.",
    "(Default model) A baseline cache model that buffer extra."
]


def update_cache_item1(info_cache: Info_Cache = None):
    idx = 0
    id_prefix = f"{uuid.uuid4()}-"
    cache_item = fac.AntdCollapse(
        id=id_prefix + "collapse-board",
        bordered=False,
        collapsible="icon",
        style=dict(
            marginBottom="10px",
            border="1px solid lightgrey",
            padding="10px",
            borderRadius="3px"
        ),
        title=html.Div(
            children=[
                html.Div(
                    style=style_l1,
                    children=[
                        fac.AntdIcon(
                            icon="antd-idcard",
                            style=style_icon1,
                        ),
                        f"Cache Model Name: {names[idx]} (ID: {ids[idx]})"
                    ]
                ),
                
                
                
                
                
                
                
                
                
                
                html.Div(
                    style=style_l1,
                    children=[
                        fac.AntdIcon(
                            style=style_icon1,
                            icon="antd-file-text",
                        ),
                        f"Description: {descriptions[idx]}"
                    ]
                ),
            ]

        ),
        children=[
            html.Div(
                style=style_l1,
                children=[
                    fac.AntdIcon(
                        style=style_icon1,
                        icon="antd-apartment"
                    ),
                    "Parameters:",
                ]
            ),

            html.Div(
                style=style_l2,
                children=[
                    fac.AntdIcon(
                        style=style_icon2,
                        icon="antd-repair"
                    ),
                    "L1_refresh_frequency: ",
                    html.Div(
                        style=style_input,
                        children=fac.AntdInput(
                            defaultValue="0.03",
                        ),
                    )
                ]
            ),
            html.Div(
                style=style_l2,
                children=[
                    fac.AntdIcon(
                        style=style_icon2,
                        icon="antd-repair"
                    ),
                    "initial_cache_size: ",
                    html.Div(
                        style=style_input,
                        children=fac.AntdInput(
                            defaultValue="5",
                        ),
                    ),
                ]
            ),
            html.Div(
                style=style_l2,
                children=[
                    fac.AntdIcon(
                        style=style_icon2,
                        icon="antd-repair"
                    ),
                    "exploration rate:",
                    html.Div(
                        style=style_input,
                        children=fac.AntdInput(
                            defaultValue="0",
                        ),
                    )
                ]
            ),

            html.Div(
                style=style_l1,
                children=[
                    fac.AntdIcon(
                        style=style_icon1,
                        icon="antd-highlight"
                    ),
                    "Colors:",
                ]
            ),

            html.Div(
                style=style_l2,
                children=[
                    fac.AntdIcon(
                        style=style_icon2,
                        icon="antd-repair"
                    ),
                    "lines_color: ",
                    html.Div(
                        style=style_input,
                        children=fac.AntdInput(
                            defaultValue="#2980B9"
                        ),
                    )
                ]
            ),
            html.Div(
                style=style_l2,
                children=[
                    fac.AntdIcon(
                        style=style_icon2,
                        icon="antd-repair"
                    ),
                    "bar_color: ",
                    html.Div(
                        style=style_input,
                        children=fac.AntdInput(
                            defaultValue="#2980B9"
                        ),
                    )
                ]
            ),
            html.Div(
                style=dict(
                    position="absolute",
                    right="10px",
                    bottom="5px",
                ),
                title="delete",
                children=fac.AntdIcon(
                    className="hover-cursor-pointer",
                    icon="antd-close",
                )
            )
        ]
    )

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    #
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    
    
    
    
    
    
    
    
    
    
    

    return cache_item


def update_cache_item2(info_cache: Info_Cache = None):
    idx = 1
    id_prefix = f"{uuid.uuid4()}-"
    cache_item = fac.AntdCollapse(
        id=id_prefix + "collapse-board",
        bordered=False,
        collapsible="icon",
        style=dict(
            marginBottom="10px",
            border="1px solid lightgrey",
            padding="10px",
            borderRadius="3px"
        ),
        title=html.Div(
            children=[
                html.Div(
                    style=style_l1,
                    children=[
                        fac.AntdIcon(
                            icon="antd-idcard",
                            style=style_icon1,
                        ),
                        f"Cache Model Name: {names[idx]} (ID: {ids[idx]})"
                    ]
                ),

                html.Div(
                    style=style_l1,
                    children=[
                        fac.AntdIcon(
                            style=style_icon1,
                            icon="antd-file-text",
                        ),
                        f"Description: {descriptions[idx]}"
                    ]
                ),

            ]

        ),
        children=[
            html.Div(
                style=style_l1,
                children=[
                    fac.AntdIcon(
                        style=style_icon1,
                        icon="antd-apartment"
                    ),
                    "Parameters:",
                ]
            ),

            html.Div(
                style=style_l2,
                children=[
                    fac.AntdIcon(
                        style=style_icon2,
                        icon="antd-repair"
                    ),
                    "initial_score_threshold: ",
                    html.Div(
                        style=style_input,
                        children=fac.AntdInput(
                            defaultValue="0.05",
                        ),
                    )
                ]
            ),
            html.Div(
                style=style_l2,
                children=[
                    fac.AntdIcon(
                        style=style_icon2,
                        icon="antd-repair"
                    ),
                    "reset_threshold_by_scanning: ",
                    html.Div(
                        style=style_input,
                        children=fac.AntdInput(
                            defaultValue="false",
                        ),
                    ),

                ]
            ),
            html.Div(
                style=style_l2,
                children=[
                    fac.AntdIcon(
                        style=style_icon2,
                        icon="antd-repair"
                    ),
                    "k_num:",
                    html.Div(
                        style=style_input,
                        children=fac.AntdInput(
                            defaultValue="self.subscription.k_num",
                            disabled=True,
                        ),
                    ),
                    html.Div(
                        className="uneditable",
                        children="UNEDITABLE",
                    )
                ]
            ),

            html.Div(
                style=style_l1,
                children=[
                    fac.AntdIcon(
                        style=style_icon1,
                        icon="antd-highlight"
                    ),
                    "Colors:",
                ]
            ),

            html.Div(
                style=style_l2,
                children=[
                    fac.AntdIcon(
                        style=style_icon2,
                        icon="antd-repair"
                    ),
                    "lines_color: ",
                    html.Div(
                        style=style_input,
                        children=fac.AntdInput(
                            defaultValue="#F39C12"
                        ),
                    )
                ]
            ),
            html.Div(
                style=style_l2,
                children=[
                    fac.AntdIcon(
                        style=style_icon2,
                        icon="antd-repair"
                    ),
                    "bar_color: ",
                    html.Div(
                        style=style_input,
                        children=fac.AntdInput(
                            defaultValue="#F39C12"
                        ),
                    )
                ]
            ),
            html.Div(
                style=dict(
                    position="absolute",
                    right="10px",
                    bottom="5px",
                ),
                title="delete",
                children=fac.AntdIcon(
                    className="hover-cursor-pointer",
                    icon="antd-close",
                )
            )
        ]
    )

    return cache_item


def update_cache_item3(info_cache: Info_Cache = None):
    idx = 2
    id_prefix = f"{uuid.uuid4()}-"
    cache_item = fac.AntdCollapse(
        id=id_prefix + "collapse-board",
        bordered=False,
        collapsible="icon",
        style=dict(
            marginBottom="10px",
            border="1px solid lightgrey",
            padding="10px",
            borderRadius="3px"
        ),
        title=html.Div(
            children=[
                html.Div(
                    style=style_l1,
                    children=[
                        fac.AntdIcon(
                            icon="antd-idcard",
                            style=style_icon1,
                        ),
                        f"Cache Model Name: {names[idx]} (ID: {ids[idx]})"
                    ]
                ),

                html.Div(
                    style=style_l1,
                    children=[
                        fac.AntdIcon(
                            style=style_icon1,
                            icon="antd-file-text",
                        ),
                        f"Description: {descriptions[idx]}"
                    ]
                ),

            ]

        ),
        children=[
            html.Div(
                style=style_l1,
                children=[
                    fac.AntdIcon(
                        style=style_icon1,
                        icon="antd-apartment"
                    ),
                    "Parameters:",
                ]
            ),

            html.Div(
                style=style_l2,
                children=[
                    fac.AntdIcon(
                        style=style_icon2,
                        icon="antd-repair"
                    ),
                    "max_k_prime: ",
                    html.Div(
                        style=style_input,
                        children=fac.AntdInput(
                            defaultValue="20",
                        ),
                    )
                ]
            ),

            html.Div(
                style=style_l1,
                children=[
                    fac.AntdIcon(
                        style=style_icon1,
                        icon="antd-highlight"
                    ),
                    "Colors:",
                ]
            ),

            html.Div(
                style=style_l2,
                children=[
                    fac.AntdIcon(
                        style=style_icon2,
                        icon="antd-repair"
                    ),
                    "lines_color: ",
                    html.Div(
                        style=style_input,
                        children=fac.AntdInput(
                            defaultValue="#27AE60"
                        ),
                    )
                ]
            ),
            html.Div(
                style=style_l2,
                children=[
                    fac.AntdIcon(
                        style=style_icon2,
                        icon="antd-repair"
                    ),
                    "bar_color: ",
                    html.Div(
                        style=style_input,
                        children=fac.AntdInput(
                            defaultValue="#27AE60"
                        ),
                    )
                ]
            ),
            html.Div(
                style=dict(
                    position="absolute",
                    right="10px",
                    bottom="5px",
                ),
                title="delete",
                children=fac.AntdIcon(
                    className="hover-cursor-pointer",
                    icon="antd-close",
                )
            )
        ]
    )

    return cache_item


new_cache = html.Div(
    className="hover-cursor-pointer",
    style=dict(
        fontSize="larger",
        display="flex",
        alignItems="center"
    ),
    children=[
        fac.AntdIcon(
            style=dict(
                marginRight="5px"
            ),
            icon="antd-plus-circle-two-tone"
        ),
        html.Div(
            children="New Compared Cache Models",
            id="new-model"
        ),
        dcc.Dropdown(
            style=dict(
                width="220px",
                marginLeft="5px",
            ),
            placeholder="model name",
            options=[
                {"label": "Recap", "value": 0},
                {"label": "TkRS", "value": 1},
                {"label": "kmax", "value": 2},
                
                {"label": "PCL", "value": 3},
            ],
            value=[],

        ),
    ]
)

count = 0


@app.callback(
    Output('cache-list', 'children'),
    [
        Input('new-model', "n_clicks")
    ],
    prevent_initial_call=True
)
def update_list(value):
    global count
    count += 1
    items = [update_cache_item1(), update_cache_item2(), update_cache_item3()]
    res = items[0:count]
    res.append(new_cache)
    return res


@app.callback(
    Output('cache-compare-title', 'children'),
    [
        Input('new-model', "n_clicks")
    ],
)
def update_title(value):
    return f"Compared cache models ({count} caches)"


cache_compare = html.Div(
    className="components-container",
    style=dict(
        height="100%",
        width="100%",
        padding="0 20px",
        alignContent="space-between",
    ),
    children=[
        html.H2(
            style=dict(
                width="100%",
                margin="0",
            ),
            children="Compared cache models (0 caches)",
            id="cache-compare-title",
        ),
        html.Div(
            id="cache-list",
            style=dict(
                height="calc(100% - 120px)",
                width="100%",
                overflowY="auto",
                position="relative",
                bottom="10px"
            ),
            children=[new_cache]
        ),
        html.Div(
            style=dict(
                width="100%",
                position="relative",
            ),
            children=[
                fuc.FefferyFancyButton(
                    type="secondary",
                    ripple=True,
                    children="Dataset",
                    style=dict(marginRight="20px"),
                ),
                fuc.FefferyFancyButton(
                    type="secondary",
                    ripple=True,
                    children="Caches",
                ),
                fuc.FefferyFancyButton(
                    type="primary",
                    ripple=True,
                    id="perform-button",
                    children="Perform",
                    style=dict(
                        
                        position="absolute",
                        right="20px"
                    ),
                )
            ]
        )

    ]
)
