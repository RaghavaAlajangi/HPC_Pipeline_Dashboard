import os

from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

from .pages import (advanced_page_layout, home_page_layout, sidebar_layout,
                    simple_page_layout, wrong_page)

# Dash Bootstrap CSS URL
DBC_CSS = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap"
           "-templates@V1.0.1/dbc.min.css")

# Get the BASENAME_PREFIX from environment variables if not default
BASENAME_PREFIX = os.environ.get("BASENAME_PREFIX", "/local-dashboard/")

# Initialise the app
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY, DBC_CSS, dbc.icons.BOOTSTRAP],
    requests_pathname_prefix=BASENAME_PREFIX,
    routes_pathname_prefix=BASENAME_PREFIX,
    suppress_callback_exceptions=True
)

server = app.server

# Build the main layout of the app
app.layout = html.Div([
    sidebar_layout(),
    dcc.Location(id="url", refresh=False),
    html.Div(
        id="page-content",
        style={"align-items": "center", "overflowX": "hidden"}
    )
])


@app.callback(
    Output("page-content", "children"),
    Output("home_page_link", "active"),
    Output("simple_page_link", "active"),
    Output("advanced_page_link", "active"),
    Input("url", "pathname"),
)
def render_page_content(pathname):
    """Renders the page content when the user clicks on the page link"""
    if pathname == BASENAME_PREFIX:
        return home_page_layout(), True, False, False
    elif pathname == f"{BASENAME_PREFIX}simple_request":
        return simple_page_layout(pathname), False, True, False
    elif pathname == f"{BASENAME_PREFIX}advanced_request":
        return advanced_page_layout(pathname), False, False, True
    # Return a 404 message, if user tries to reach undefined page
    return wrong_page(pathname), False, False, False
