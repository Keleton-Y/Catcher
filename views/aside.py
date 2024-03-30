import feffery_antd_components as fac
from dash import dcc, html
from dash.dependencies import Input, Output, State, ClientsideFunction
from globals.variable import app
from globals import html_id
from views.content1.content import content1
from views.content2.content import content2


fac.AntdDivider(
    "基于AntdSider的自定义折叠触发",
    innerTextOrientation="left"
),

aside = html.Div(
    [
        fac.AntdLayout(
            [
                fac.AntdSider(
                    [
                        
                        fac.AntdButton(
                            id="menu-collapse-sider-custom-demo-trigger",
                            icon=fac.AntdIcon(
                                id="menu-collapse-sider-custom-demo-trigger-icon",
                                icon="antd-arrow-left",
                                style={
                                    "fontSize": "14px"
                                }
                            ),
                            shape="circle",
                            type="text",
                            style={
                                "position": "absolute",
                                "zIndex": 1,
                                "top": 25,
                                "right": -13,
                                "boxShadow": "rgb(0 0 0 / 10%) 0px 4px 10px 0px",
                                "background": "white"
                            }
                        ),

                        fac.AntdMenu(
                            menuItems=[
                                {
                                    "component": "Item",
                                    "props": {
                                        "key": "content1",
                                        "title": "Analysis",
                                        "icon": "antd-bar-chart"
                                    }
                                },
                                {
                                    "component": "Item",
                                    "props": {
                                        "key": "content2",
                                        "title": "Evaluation",
                                        "icon": "antd-schedule"
                                    }
                                },
                            ],
                            
                            defaultSelectedKey="content1",
                            mode="inline",
                            style={
                                "height": "100%",
                                "overflow": "hidden auto"
                            },
                            id="aside-menu"
                        )
                    ],
                    id="menu-collapse-sider-custom-demo",
                    collapsible=True,
                    collapsedWidth=60,
                    trigger=None,
                    style={
                        "height": "100%",
                        "position": "relative",
                    },
                    
                    width="200px"
                ),

                fac.AntdContent(
                    style={
                        "background": "#f8f9fa"
                    }
                )
            ],
        )
    ],
    style={
        "height": "100%",
        "border": "2px solid rgb(241, 241, 241)"
    }
)

app.clientside_callback(
    """(nClicks, collapsed) => {
        return [!collapsed, collapsed ? "antd-arrow-left" : "antd-arrow-right"];
    }""",
    [Output("menu-collapse-sider-custom-demo", "collapsed"),
     Output("menu-collapse-sider-custom-demo-trigger-icon", "icon")],
    Input("menu-collapse-sider-custom-demo-trigger", "nClicks"),
    State("menu-collapse-sider-custom-demo", "collapsed"),
    prevent_initial_call=True
)


@app.callback(
    Output(html_id.PAGE_CONTENT, "children"),
    Input("aside-menu", "currentKey")
)
def menu_callback_demo(currentKey):
    if currentKey == "content1":
        return content1
    if currentKey == "content2":
        return content2

