
import feffery_antd_components as fac
from dash import html
from globals.variable import app
from dash.dependencies import Input, Output
from views.content1.components.bar_cache import bar_cache
from views.content1.components.bar_cache_detail import bar_cache_detail
from views.content1.components.cache_detail import cache_detail
from views.content1.components.form import dataset_form, period_form, cache_filter
from views.content1.components.form_sliders import slider_time_message
from views.content1.components.line_cost import line_cost
from views.content1.components.map_msg import map_msg
from views.content1.components.map_sub import map_sub
from views.content1.components.scatter_bar_message_update import scatter_bar_message_update


forms = html.Div(

    style=dict(
        padding="0 10px 10px 10px",
        margin="0 10px",
        width="100%",
        height="40%",
        display="flex",
        flexWrap="wrap",
        alignContent="space-around"
    ),
    children=[
        html.Div(
            children=dataset_form,
        ),
        html.Div(
            
            children=period_form
        ),

        html.Div(
            style=dict(
                width="100%",
                height="40px",
            ),
            children=[
                html.Div(
                    className="info-span",
                    style=dict(
                        width="100%",
                        paddingLeft="10px",
                    ),
                    id="sub-msg-count",
                    children="31081 subscriptions, 206,423 messages"
                )
            ]
        ),
        html.Div(
            style=dict(
                width="100%",
                display="flex",
                flexWrap="wrap",
                justifyContent="center",
            ),
            children=[
                html.Div(
                    className="form-label",
                    style=dict(
                        width="100%",
                    ),
                    children="Select time range of message in dataset"
                ),
                slider_time_message,
            ]
        ),
        html.Div(
            className="form-label",
            children="Filter: ",
        ),
        html.Div(
            style=dict(
                width="80%",
                padding="0px 10px 10px 10px",
                backgroundColor="#f7f7f7",
                borderRadius="5px",
            ),
            children=[
                cache_filter
            ]
        ),
        html.Div(
            className="info-span",
            style=dict(
                width="100%",
                paddingLeft="10px",
            ),
            id="sub-filter-count",
            children="Get 6632 Subscriptions"
        ),

        html.Div(
            className="form-label",
            children=[
                html.Span(
                    children="Highlight: Mark most "
                ),
                fac.AntdInput(
                    id="highlight-percent",
                    className="filter-input",
                    defaultValue="10",
                ),
                html.Span(
                    children="% popular Messages"
                )
            ]
        )
    ]
)


performance_monitor = html.Div(

    style=dict(
        padding="0 10px 10px 10px",
        margin="0 10px",
        width="100%",
        height="calc(60% - 10px)",
        display="flex",
        flexWrap="wrap",
        alignContent="space-around",
        backgroundColor="#f9f9f9",
    ),
    children=[


        html.Div(
            style=dict(
                marginTop="10px",
                height="calc(55% - 35px)",
                width="100%",
            ),
            children=[
                line_cost
            ]
        ),

        html.Div(
            style=dict(
                height="45%",
                width="100%",
            ),
            children=[
                scatter_bar_message_update
            ]
        ),
    ]
)


maps = html.Div(
    className="card-border",
    style={
        "padding": "0 10px 10px 10px",
        "width": "100%",
        "height": "calc(50% - 5px)",
        "display": "flex",
        "flexWrap": "wrap",
        "justifyContent": "space-around",
        "alignContent": "space-around",
        "backgroundColor": "#f9f9f9",
    },
    children=[

        html.Div(
            style=dict(
                width="calc(50% - 10px)",
                height="100%",
                display="flex",
                alignItems="center",
                backgroundColor="#f9f9f9",
            ),
            children=[

                html.Div(
                    style=dict(
                        flex=1,
                        height="100%",
                    ),
                    children=[
                        map_sub
                    ]
                )
            ]
        ),
        html.Div(
            style=dict(
                width="calc(50% - 10px)",
                height="100%",
            ),
            children=[
                map_msg
            ]
        ),
    ]
)


cache_analysis = html.Div(
    className="card-border",
    style={
        "padding": "0 10px 10px 10px",
        "width": "100%",
        "height": "calc(50% - 5px)",
        "display": "flex",
        "flexWrap": "wrap",
        "justifyContent": "space-around",
        "alignContent": "space-around",
        "backgroundColor": "#f9f9f9",
    },
    children=[

        html.Div(
            className="components-container",
            style=dict(
                width="calc(50% - 10px)",
                height="100%",
            ),
            children=[
                html.H2(
                    className="h-center",
                    id="cache-uti-ratio"
                ),
                html.Div(
                    style=dict(
                        width="100%",
                        height="calc(50% - 20px)",
                    ),
                    children=bar_cache,
                ),
                html.Div(
                    style=dict(
                        width="100%",
                        height="calc(50% - 20px)",
                    ),
                    children=bar_cache_detail,
                )
            ]
        ),

        html.Div(
            style=dict(
                width="calc(50% - 10px)",
                height="100%",
                display="flex",
                alignItems="center",
            ),
            children=[
                html.Div(
                    style=dict(
                        flex="1",
                        height="100%",
                    ),
                    children=[
                        cache_detail,
                    ]
                )
            ]
        ),
    ]
)

@app.callback(
    Output('cache-uti-ratio', 'children'),
    [
        Input('map_sub', 'clickData'),
    ]
)
def update_sub_filter_count(clickData):
    if clickData:
        ID16 = clickData['points'][0]['customdata']['ID16']
        return f"Cache #{ID16} Utilization ratio"
    return "Please Click the Subscription Data Point"



left_content = html.Div(
    className="card-border",
    style=dict(
        margin="0 10px 0 0",
        width="calc(35% - 10px)",
        height="calc(100% - 10px)",
        display="flex",
        flexWrap="wrap",
        alignContent="space-between",
        backgroundColor="#f9f9f9",
    ),
    children=[
        forms,
        fac.AntdDivider(
            direction="horizontal",
            lineColor="grey",
            className="left-content-divider"
        ),
        performance_monitor
    ]
)


right_content = html.Div(
    style=dict(
        margin="0 10px 0 0",
        width="calc(65% - 10px)",
        height="calc(100% - 10px)",
        display="flex",
        flexWrap="wrap",
        alignContent="space-between"
    ),
    children=[
        maps,
        cache_analysis,
    ]
)


content1 = html.Div(
    className="components-container",
    style={
        "width": "100%",
        "height": "100%",
    },
    children=[
        left_content,
        right_content
    ]
)
