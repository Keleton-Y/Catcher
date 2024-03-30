
import dash
import plotly.graph_objects as go


app = dash.Dash(name="VLDB-demo", assets_folder="./assets")
app.title = "Cache Analyse"


BASE_PATH = "D:\workplace\python\paper_codes\cache-analysisi-vldb-demo"


BASE_LAYOUT = dict(
    plot_bgcolor="#f9f9f9",
    paper_bgcolor="#f9f9f9",
    margin=go.layout.Margin(l=10, r=10, b=0, t=30, pad=0),
    autosize=True,
    hovermode="closest",
    legend=go.layout.Legend(
        font=go.layout.legend.Font(size=13),
        orientation="h",
        x=0,
        y=0
    ),
)




