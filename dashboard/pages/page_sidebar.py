import os

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

from .common import line_breaks

# BDA GitHub URL
bda_gitlab_url = "https://gitlab.gwdg.de/blood_data_analysis"
# Important URLs
imp_urls = {
    "hpc_pipeline_data": f"{bda_gitlab_url}/hpc_pipeline_data",
    "hpc_pipeline_requests": f"{bda_gitlab_url}/hpc_pipeline_requests",
    "hpc_pipeline_dashboard": f"{bda_gitlab_url}/hpc_pipeline_dashboard",
    "dcevent": "https://blood_data_analysis.pages.gwdg.de/dcevent/",
}


# Get the BASENAME_PREFIX from environment variables if not default
BASENAME_PREFIX = os.environ.get("BASENAME_PREFIX", "/local-dashboard/")


def wrong_page(pathname):
    return html.Div(
        children=[
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )


def sidebar_layout():
    return html.Div(
        children=[
            # Title for the dashboard
            dmc.Title("HPC Pipelines", order=1, align="center"),
            line_breaks(times=1),
            # Alert for the users
            dbc.Alert(
                children=[
                    # Warning icon
                    dmc.Stack(
                        children=[
                            html.I(
                                children="Warning!",
                                className="bi bi-exclamation-triangle-"
                                "fill me-2",
                            ),
                            # Warning text
                            "Running a pipeline is computationally expensive "
                            "so please do not trigger or create unnecessary "
                            "pipelines!",
                        ],
                        spacing=1,
                    ),
                ],
                color="warning",
                style={"color": "black", "width": "fit-content"},
            ),
            line_breaks(times=1),
            # Links for other pages
            dbc.Nav(
                children=[
                    dbc.NavLink(
                        children="Home",
                        href=BASENAME_PREFIX,
                        id="home_page_link",
                    ),
                    dbc.NavLink(
                        children="Simple Request",
                        href=f"{BASENAME_PREFIX}simple_request",
                        id="simple_page_link",
                    ),
                    dbc.NavLink(
                        children="Advanced Request",
                        href=f"{BASENAME_PREFIX}advanced_request",
                        id="advanced_page_link",
                    ),
                ],
                pills=True,
                style={"color": "red"},
                vertical=True,
            ),
            line_breaks(times=15),
            # Show HPC data link
            dmc.Anchor(
                align="end",
                color="green",
                children=[
                    DashIconify(
                        icon="material-symbols-light:docs-outline",
                        width=30,
                        height=30,
                        flip="horizontal",
                    ),
                    "dcevent docs",
                ],
                href=imp_urls["dcevent"],
            ),
            line_breaks(times=1),
            # Show HPC data link
            dmc.Anchor(
                align="end",
                color="green",
                children=[
                    DashIconify(
                        icon="famicons:logo-gitlab",
                        width=25,
                        height=25,
                        flip="horizontal",
                    ),
                    " hpc_pipeline_data",
                ],
                href=imp_urls["hpc_pipeline_data"],
            ),
            line_breaks(times=1),
            # Show HPC requests link
            dmc.Anchor(
                align="end",
                color="green",
                children=[
                    DashIconify(
                        icon="famicons:logo-gitlab",
                        width=25,
                        height=25,
                        flip="horizontal",
                    ),
                    " hpc_pipeline_requests",
                ],
                href=imp_urls["hpc_pipeline_requests"],
            ),
            line_breaks(times=1),
            # Show project link
            dmc.Anchor(
                align="end",
                color="green",
                children=[
                    DashIconify(
                        icon="famicons:logo-gitlab",
                        width=25,
                        height=25,
                        flip="horizontal",
                    ),
                    " source code",
                ],
                href=imp_urls["hpc_pipeline_dashboard"],
            ),
        ],
        id="sidebar",
    )
