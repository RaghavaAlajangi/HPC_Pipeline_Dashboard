import os

from dash import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from .common import line_breaks

# GitLab repo URL
PROJECT_REPO_URL = "https://gitlab.gwdg.de/blood_data_analysis/" \
                   "hpc_pipeline_dashboard"

# GitLab logo image
GITLAB_LOGO_URL = "https://about.gitlab.com/images/press" \
                  "/logo/png/gitlab-icon-rgb.png"

# Get the BASENAME_PREFIX from environment variables if not default
BASENAME_PREFIX = os.environ.get("BASENAME_PREFIX", "/local-dashboard/")


def wrong_page(pathname):
    return html.Div(
        children=[
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised...")
        ],
        className="p-3 bg-light rounded-3"
    )


def sidebar_layout():
    return html.Div(
        children=[
            # Title for the dashboard
            dmc.Title("HPC Pipelines", order=1),
            line_breaks(times=1),
            # Alert for the users
            dbc.Alert(
                children=[
                    # Warning icon
                    dmc.Stack(
                        children=[
                            html.I(
                                children="Warning!",
                                className="bi bi-exclamation-triangle-fill me-2"
                            ),
                            # Warning text
                            "Running a pipeline is computationally expensive "
                            "so please do not trigger or create unnecessary "
                            "pipelines!",
                        ],
                        spacing=1
                    ),

                ],
                color="warning",
                style={"color": "black", "width": "fit-content"}
            ),
            line_breaks(times=1),
            # Links for other pages
            dbc.Nav(
                children=[
                    dbc.NavLink(
                        children="Home",
                        href=BASENAME_PREFIX,
                        id="home_page_link"
                    ),
                    dbc.NavLink(
                        children="Simple Request",
                        href=f"{BASENAME_PREFIX}simple_request",
                        id="simple_page_link"
                    ),
                    dbc.NavLink(
                        children="Advanced Request",
                        href=f"{BASENAME_PREFIX}advanced_request",
                        id="advanced_page_link"
                    )
                ],
                pills=True,
                style={"color": "red"},
                vertical=True
            ),
            line_breaks(times=6),
            # Show project link
            html.A(
                children=[
                    html.Img(src=GITLAB_LOGO_URL, height=50),
                    " Source Code"
                ],
                className="custom-link",
                href=PROJECT_REPO_URL,
                target="_blank"
            )
        ],
        id="sidebar"
    )
