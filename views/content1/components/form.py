
from datetime import date

import feffery_antd_components as fac
from dash import dcc, html
from dash.dependencies import Input, Output
from globals.variable import app

dataset_form = html.Div(
    className="form-container",
    style=dict(
        width="100%"
    ),
    children=[
        html.Span(
            className="form-label",
            children="Dataset",
        ),
        dcc.Dropdown(
            style=dict(
                width="450px",
            ),
            options=[
                {"label": "Chengdu-161101", "value": 0},
                {"label": "Chengdu-161102", "value": 1},
                {"label": "NewYork-160201", "value": 2},
                
                {"label": "NewYork-160202", "value": 3},
            ],
            multi=True,
            value=[],
            id="dataset-dropdown",
        ),
    ]
),

period_form = html.Div(
    className="form-container",
    style=dict(
        width="100%"
    ),
    children=[
        html.Span(
            children="Time Period",
            className="form-label",
        ),

        dcc.DatePickerSingle(
            month_format='MMM Do, YY',
            placeholder='MMM Do, YY',
            id="data-picker",
            style=dict(
                height="40px",
                fontSize="16px",
            ),
        ),
    ]
),


@app.callback(
    Output('data-picker', 'date'),
    [
        Input('dataset-dropdown', "value")
    ]
)
def update_sub_filter_count(value):
    if len(value) == 0:
        return None
    return date(2016, 11, 1)


cache_monitor_form = html.Div(
    style=dict(
        width="100%",
        height="100%",
        display="flex",
        justifyContent="left",
        alignItems="center",
    ),
    children=[
        html.Div(
            className="form-container",
            children=[
                html.Span(
                    children="Search cache",
                    className="form-label",
                ),
                fac.AntdInput(
                    placeholder='Cache #',
                    mode='search',
                    style=dict(
                        width="200px",
                        marginRight="10px"
                    ),
                ),
            ]
        ),
        html.Div(
            className="form-container",
            children=[
                fac.AntdSpace(
                    [
                        fac.AntdCheckbox(
                            label='label1'
                        ),

                        fac.AntdCheckbox(
                            label='label2',
                            checked=True
                        ),
                        fac.AntdCheckbox(
                            label='label3',
                            checked=True
                        )
                    ]
                )
            ]
        ),

    ]
)


def update_table_rows():
    row_style = dict(
        height="45px",
        borderBottom="1px #A9A9A9 dashed",

    )
    options = ["AND", "OR"]
    col2_div_style = dict(
        paddingLeft="30px",
        display="flex",
        alignItems="center"
    )

    col_group = html.Colgroup(
        children=[
            html.Col(
                style=dict(width="80px"),
            ),
            html.Col(
                style=dict(
                    width="calc(100% - 180px)",
                ),
            ),
            html.Col(
                style=dict(
                    width="80px",
                    padddingLeft="30px",
                ),
            ),
        ]
    )

    r1 = html.Tr(
        style=row_style,
        children=[
            html.Td(),
            html.Td(
                children=html.Div(
                    style=col2_div_style,
                    children=[
                        html.Span("Cache Utilization Ratio ≤ "),
                        fac.AntdInput(
                            className="filter-input",
                            defaultValue="100",
                            id="cache_utilization_ratio",
                        ),
                        html.Span("%")
                    ]
                )
            ),
            html.Td(
                children=[
                    fac.AntdCheckbox(
                        label='',
                        checked=True,
                    ),
                ]
            )
        ]
    )

    r2 = html.Tr(
        style=row_style,
        children=[
            html.Td(
                children=[
                    fac.AntdSelect(
                        id="refill-frequency-and-or",
                        options=[
                            {
                                'label': options[i],
                                'value': options[i]
                            }
                            for i in range(len(options))
                        ],
                        defaultValue="OR",
                        allowClear=False,
                        style=dict(
                            width="80px"
                        )
                    )
                ]
            ),
            html.Td(
                children=html.Div(
                    style=col2_div_style,
                    children=[
                        html.Span("Refill  Frequency ≥ "),
                        fac.AntdInput(
                            className="filter-input",
                            id="refill_frequency",
                            defaultValue="35",
                        ),
                        html.Span("/h")
                    ]
                )
            ),
            html.Td(
                children=[
                    fac.AntdCheckbox(
                        label='',
                        id="refill_frequency_checkbox"
                    ),
                ]
            )
        ]
    )

    r3 = html.Tr(
        style=row_style,
        children=[
            html.Td(
                children=[
                    fac.AntdSelect(
                        options=[
                            {
                                'label': options[i],
                                'value': options[i]
                            }
                            for i in range(len(options))
                        ],
                        defaultValue="AND",
                        allowClear=False,
                        style=dict(
                            width="80px"
                        )
                    )
                ]
            ),
            html.Td(
                children=html.Div(
                    style=col2_div_style,
                    children=[
                        html.Span("Average Update Cost in Top"),
                        fac.AntdInput(
                            className="filter-input",
                            defaultValue="50",
                            id="update-cost-top-ratio"
                        ),
                        html.Span("%")
                    ]
                )
            ),
            html.Td(
                children=[
                    fac.AntdCheckbox(
                        label='',
                        id="update-cost-top-ratio-checkbox"
                    ),
                ]
            )
        ]
    )
    return [col_group, r1, r2, r3]


cache_filter = html.Table(
    id="cache_filter",
    style=dict(
        width="100%",
    ),
    children=update_table_rows(),
)
