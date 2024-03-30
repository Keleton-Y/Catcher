
from dash import dcc, html
from views.content2.components.form_dataset import form_dataset
from views.content2.components.cache_compare import cache_compare
from views.content2.components.line_cost import line_cost
from views.content2.components.line_memory import line_memory
from views.content2.components.bar_cache_utilization import bar_cache_utilization
import feffery_utils_components as fuc
left_content = html.Div(
    className="components-container card-border",
    style=dict(
        margin="0 10px 0 0",
        width="calc(35% - 20px)",
        height="calc(100% - 20px)",
        display="flex",
        flexWrap="wrap",
        alignContent="space-between",
        backgroundColor="#f9f9f9",
    ),
    children=[
        html.Div(
            className="components-container",
            style=dict(
                width="100%",
                height="15%",
                paddingTop="20px"
            ),
            children=[
                form_dataset
            ]
        ),
        html.Div(
            className="components-container",
            style=dict(
                width="100%",
                height="85%",
            ),
            children=[
                cache_compare
            ]
        )
    ]
)

comparison_results = html.Div(
    className="card-border components-container",
    style=dict(
        margin="0 10px 0 0",
        width="calc(65% - 10px)",
        height="calc(100% - 20px)",
        backgroundColor="#f9f9f9",
        padding="10px 10px"
    ),
    children=[
        html.Div(
            style=dict(
                width="50%",
                height="calc(50% - 35px)",
            ),
            children=[
                line_cost
            ]
        ),
        html.Div(
            style=dict(
                width="50%",
                height="calc(50% - 35px)",
            ),
            children=[
                line_memory
            ]
        ),
        html.Div(
            style=dict(
                width="100%",
                height="calc(50% - 35px)",
            ),
            children=[
                bar_cache_utilization
            ]
        ),

        html.Div(
            style=dict(
                width="95%",
                display="flex",
                justifyContent="right",
            ),
            children=[
                fuc.FefferyFancyButton(
                    type="primary",
                    ripple=True,
                    children="Download",
                )
            ]
        )
    ]
)

content2 = html.Div(
    className="components-container",
    style={
        "width": "100%",
        "height": "100%",
    },
    children=[
        left_content,
        comparison_results,
    ]
)
