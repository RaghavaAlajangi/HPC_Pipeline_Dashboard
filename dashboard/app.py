import flask
import json
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html

from .components import (groupby_columns, line_breaks, paragraph_comp)
from .hpc_pipeine_app import (main_layout, simple_request, advanced_request,
                              extract_rows_from_data)

DBC_CSS = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap"
           "-templates@V1.0.1/dbc.min.css")

PROJECT_REPO_URL = "https://gitlab.gwdg.de/blood_data_analysis/" \
                   "hpc_pipeline_dashboard"
GITLAB_LOGO_URL = "https://about.gitlab.com/images/press" \
                  "/logo/png/gitlab-icon-rgb.png"

PATHNAME_PREFIX = "/hpc-pipelines/"

# HSMFS drive path
HSMFS_PATH = Path(__file__).parents[2] / "HSMFS"


def wrong_page(pathname):
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3"
    )


def sidebar_menu():
    return html.Div([
        groupby_columns([
            html.H3("HPC Pipelines", style={"font-weight": "bold"}),
            line_breaks(times=1)
        ]),
        dbc.Alert([
            # Warning icon
            html.I(className="bi bi-exclamation-triangle-fill me-2"),
            "Note:",
            paragraph_comp(
                text="Please be aware that running a pipeline is "
                     "computationally expensive so please do not trigger or "
                     "create unnecessary pipelines!",
                comp_id="dummy2", indent=1
            ),
        ],
            style={"color": "black", "width": "fit-content"},
            color="warning",
        ),
        groupby_columns([
            line_breaks(times=1),
            dbc.Nav([
                dbc.NavLink("Home",
                            href="/hpc-pipelines/",
                            id="home_active"),
                dbc.NavLink("Simple request",
                            href="/hpc-pipelines/simple_request",
                            id="simple_request_active"),
                dbc.NavLink("Advanced request",
                            href="/hpc-pipelines/advanced_request",
                            id="advanced_request_active"),
            ],
                vertical=True,
                pills=True,
            ),
            line_breaks(times=1),
        ]),

        html.Div([
            line_breaks(times=5),
            html.A([
                html.Img(src=GITLAB_LOGO_URL, height=50),
                " Source code"
            ],
                href=PROJECT_REPO_URL,
                target="_blank",
                style={"text-decoration": "none"}
            )
        ])
    ],
        id="sidebar"
    )


def main_content_block():
    return html.Div(
        id="page-content",
        style={"align-items": "center",
               "overflowX": "hidden"}
    )


# Initialise the app
app = dash.Dash(
    assets_folder="assets",
    suppress_callback_exceptions=True,
    routes_pathname_prefix=PATHNAME_PREFIX,
    requests_pathname_prefix=PATHNAME_PREFIX,
    external_stylesheets=[dbc.themes.DARKLY, DBC_CSS, dbc.icons.BOOTSTRAP],
    # these meta_tags ensure content is scaled correctly on different devices
    # see: https://www.w3schools.com/css/css_rwd_viewport.asp for more
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])

server = app.server


@server.route("/hpc-pipelines/api/serverData", methods=["POST"])
def server_data():
    response = extract_rows_from_data(flask.request.json["groupKeys"],
                                      HSMFS_PATH)
    return json.dumps(response)


# Build the layout of the app
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar_menu(),
    main_content_block(),
])


@app.callback(
    [Output("page-content", "children"),
     Output("home_active", "active"),
     Output("simple_request_active", "active"),
     Output("advanced_request_active", "active")],
    Input("url", "pathname"),
)
def render_page_content(pathname):
    if pathname == "/hpc-pipelines/":
        return [main_layout(), True, False, False]
    elif pathname == "/hpc-pipelines/simple_request":
        return [simple_request(), False, True, False]
    elif pathname == "/hpc-pipelines/advanced_request":
        return [advanced_request(), False, False, True]
    # Return a 404 message, if user tries to reach undefined page
    return wrong_page(pathname)
