
from dash import html, dcc
from globals.html_id import (
    APP_CONTAINER, PAGE_CONTENT,
    PAGE_ASIDE, PAGE_HEADER, ASIDE_CONTENT_CONTAINER
)
from views.aside import aside
from views.header import header
from globals.variable import app
from views.content1.content import content1
from views.content2.content import content2


app.layout = html.Div(

    id=APP_CONTAINER,
    children=[
        html.Div(
            id=PAGE_HEADER,
            children=[
                header
            ]
        ),
        html.Div(
            id=ASIDE_CONTENT_CONTAINER,
            children=[
                html.Div(
                    id=PAGE_ASIDE,
                    children=[
                        aside
                    ]
                ),
                html.Div(
                    id=PAGE_CONTENT,
                )
            ]
        ),

    ]
)


if __name__ == '__main__':
    
    
    app.config["suppress_callback_exceptions"] = True
    app.run_server(debug=True, port=8080)
