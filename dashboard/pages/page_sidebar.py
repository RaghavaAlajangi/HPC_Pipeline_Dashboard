import os
from pathlib import Path

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

from .common_components import hover_card, line_breaks

CHANGELOG_PATH = Path(__file__).parents[2] / "CHANGELOG"

# BDA GitHub URL
bda_gitlab_url = "https://gitlab.gwdg.de/blood_data_analysis"
# Important URLs
imp_urls = {
    "hpc_pipeline_data": f"{bda_gitlab_url}/hpc_pipeline_data",
    "hpc_default_params": f"{bda_gitlab_url}/hpc_pipeline_requests/-/blob"
    "/main/dashboard_dcevent_defaults.yaml",
    "hpc_pipeline_dashboard": f"{bda_gitlab_url}/hpc_pipeline_dashboard",
    "dcevent": "https://blood_data_analysis.pages.gwdg.de/dcevent/",
}


# Get the BASENAME_PREFIX from environment variables if not default
BASENAME_PREFIX = os.environ.get("BASENAME_PREFIX", "/local-dashboard/")


def get_latest_version():
    """Read the latest version from the CHANGELOG"""
    with open(CHANGELOG_PATH, "r", encoding="utf-8") as file:
        return file.readline().strip()


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
    """Creates the sidebar layout for the dashboard."""
    sidebar_menu = dbc.Nav(
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
    )

    dcevent_docs_link = dmc.Anchor(
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
    )

    hpc_data_repo_link = dmc.Anchor(
        align="end",
        color="green",
        children=[
            DashIconify(
                icon="famicons:logo-gitlab",
                width=25,
                height=25,
                flip="horizontal",
            ),
            " pipeline data",
        ],
        href=imp_urls["hpc_pipeline_data"],
    )

    hpc_params_link = dmc.Anchor(
        align="end",
        color="green",
        children=[
            DashIconify(
                icon="famicons:logo-gitlab",
                width=25,
                height=25,
                flip="horizontal",
            ),
            " default params",
        ],
        href=imp_urls["hpc_default_params"],
    )

    hpc_dashboard_repo_link = dmc.Anchor(
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
    )

    return html.Div(
        children=[
            # Title for the dashboard
            dmc.Title("HPC Pipeline Dashboard", order=2),
            # Dashboard version (from changelog)
            dmc.Code(f"v{get_latest_version()}", fz=15),
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
            dbc.ListGroup(
                [
                    # Links for other pages
                    dbc.ListGroupItem(
                        [
                            sidebar_menu,
                        ],
                        color="#017b70",
                    ),
                    dbc.ListGroupItem(
                        [
                            # Show HPC data link
                            hover_card(
                                target=dcevent_docs_link,
                                notes="Documentation for the dcevent package."
                                "",
                                width=200,
                            ),
                            line_breaks(times=1),
                            # Show HPC data link
                            hover_card(
                                target=hpc_data_repo_link,
                                notes="Pipeline data repository. Here you "
                                "can find the input data, pipeline results, "
                                "and ML models used in the pipeline.",
                                width=200,
                            ),
                            line_breaks(times=1),
                            # Show HPC requests link
                            hover_card(
                                target=hpc_params_link,
                                notes="You can update the dashboard default "
                                "parameters here. If you change the default "
                                "parameters, the dashboard fetches them "
                                "automatically.",
                                width=200,
                            ),
                            line_breaks(times=1),
                            # Show project link
                            hover_card(
                                target=hpc_dashboard_repo_link,
                                notes="Source code for the dashboard.",
                                width=200,
                            ),
                        ],
                        color="#017b70",
                    ),
                ]
            ),
        ],
        id="sidebar",
    )
