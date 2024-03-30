import plotly.graph_objects as go
from dash import dcc, html
from globals.variable import BASE_LAYOUT
import feffery_antd_components as fac
from globals.variable import app
from dash.dependencies import Input, Output
import json

names = ["Skype", "TkRs", "Race", "kmax", "PCL"]
descriptions = ["Threshold", "2Layer", "DRL-based", "Baseline", "Partial cell list"]
operations = [
    html.Div(
        children=[
            fac.AntdIcon(
                icon="antd-arrow-up"
            ),
            fac.AntdIcon(
                icon="antd-close"
            ),
            fac.AntdIcon(
                icon="antd-arrow-down"
            ),
        ]
    ) for i in range(len(names))
]

table = fac.AntdTable(

    id='table-row-selection-demo',
    columns=[
        {
            "title": "Name",
            "dataIndex": "Name",
        },
        {
            "title": "Description",
            "dataIndex": "Description",
        },
        {
            "title": "Operation",
            "dataIndex": "Operation",
        }
    ],
    data=[
        {
            'Name': names[i],
            'Description': descriptions[i],
            'Operation': operations[i],
            "key": f"rows_{i}"
        } for i in range(len(names))
    ],
    rowSelectionType='checkbox',
    size="large",
    bordered=True,
),


@app.callback(
    Output('table-row-selection-demo-output', 'children'),
    [Input('table-row-selection-demo', 'selectedRowKeys'),
     Input('table-row-selection-demo', 'selectedRows')],
    prevent_initial_call=True
)
def table_row_selection_demo(selectedRowKeys, selectedRows):
    return json.dumps(
        dict(
            selectedRowKeys=selectedRowKeys,
            selectedRows=selectedRows
        ),
        indent=4,
        ensure_ascii=False
    )


cache_manager = html.Div(
    className="components-container",
    style=dict(
        height="100%"
    ),
    children=[
        html.H1(
            children="Cache Manager",
            className="h-center",
        ),
        html.Div(
            className="ant-table-cell",
            style=dict(
                width="95%",
            ),
            children=table,
        ),
        html.Div(
            style=dict(
                width="95%",
                display="flex",
                justifyContent="right",
            ),
            children=[
                html.Button(
                    className="btn",
                    children="Perform"
                )
            ]
        )
    ]
)
