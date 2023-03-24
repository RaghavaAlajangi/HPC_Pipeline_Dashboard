import pathlib

import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State

from ..components import dropdown_menu_comp, paragraph_comp, group_accordion
from ..gitlab_api import GitLabAPI

token_path = pathlib.Path(__file__).parents[1] / "SECRETS.txt"

with open(token_path) as f:
    token = f.readlines()[0]

gitlab = GitLabAPI(token=token)

opened = gitlab.get_issues_meta(state="opened")
closed = gitlab.get_issues_meta(state="closed")

# print(closed)
print(opened)


def main_tab_content():
    dropdown_comp1 = dbc.DropdownMenuItem([
        dbc.NavLink("Simple",
                    href="/hpc_pipelines/simple",
                    id="open_simple_request_page",
                    active=True)
    ])
    dropdown_comp2 = dbc.DropdownMenuItem([
        dbc.NavLink("Advanced",
                    href="/hpc_pipelines/advanced",
                    id="open_advance_request_page",
                    active=True),
    ])
    return dbc.Card([
        html.Br(), html.Br(),
        paragraph_comp("⦿ This page is responsible for running RTDC "
                       "dataset processing pipelines on MPCDF gpu "
                       "clusters (HPC)",
                       indent=40),
        html.Br(),
        dropdown_menu_comp(name="New Request",
                           components=[dropdown_comp1, dropdown_comp2],
                           indent=40),
    ],
        className="mt-3",
        style={"height": "50rem", 'background-color': "#424447"}
    )


def opened_tab_content(open_issues):
    return dbc.Card([
        html.Br(), html.Br(),
        html.Div(
            open_issues,
            style={"max-height": "50rem", "overflow-y": "scroll",
                   "overflowX": "hidden"},
        ),
        html.Br(), html.Br(),
    ],
        className="mt-3",
        style={"height": "50rem", 'background-color': "#424447"}
    )


def closed_tab_content(close_issues):
    return dbc.Card([
        html.Br(), html.Br(),
        html.Div(
            close_issues,
            style={"max-height": "50rem", "overflow-y": "scroll",
                   "overflowX": "hidden"},
        ),
        html.Br(), html.Br(),
    ],
        className="mt-3",
        style={"height": "50rem", 'background-color': "#424447"}
    )


def request_tabs():
    return dbc.Card([
        dbc.CardHeader(
            dbc.Tabs([
                dbc.Tab(label="Main",
                        tab_id="main_tab",
                        active_label_style={"color": "#017b70"}),
                dbc.Tab(label="Open requests",
                        tab_id="opened_tab",
                        active_label_style={"color": "#017b70"}),
                dbc.Tab(label="Closed requests",
                        tab_id="closed_tab",
                        active_label_style={"color": "#017b70"}),
            ],
                id="tabs",
                active_tab="main_tab",
            )
        ),
        html.Div(id="tab_content")
    ])


def main_layout():
    return html.Div([
        request_tabs(),
        dcc.Store(id='store_gitlab_issues',
                  data={"opened": opened,
                        "closed": closed}),
    ])


def get_issue_accord(data):
    return group_accordion([
        dbc.AccordionItem([
            paragraph_comp(text="Issue created by: {}".format(c["author"])),
            html.A(
                "See the issue on GitLab",
                href=c["web_url"],
                target='_blank',
                style={"text-decoration": "none"}
            ),
            # html.Br(), html.Br(),
            # dbc.Card([
            #     dbc.Card(co) for co in c["comments"]
            # ]),
        ],
            title=c["name"],
        ) for c in data
    ],
        middle=True, width=60
    )


@callback([Output("tab_content", "children"),
           Output("store_gitlab_issues", "data")],
          Input("tabs", "active_tab"),
          State("store_gitlab_issues", "data"))
def switch_tab(click_tab, stored_issue_meta):
    if click_tab == "main_tab":
        return [main_tab_content(), stored_issue_meta]
    elif click_tab == "opened_tab":
        open_issues_meta = gitlab.get_issues_meta(state="opened")

        if len(open_issues_meta) == 0:
            open_issues = paragraph_comp(text="⦿ We do not have opened "
                                              "requests!", indent=40)
            return [opened_tab_content(open_issues), stored_issue_meta]
        else:
            stored_open_meta = stored_issue_meta["opened"]
            if len(stored_open_meta) == len(open_issues_meta):
                stored_issue_meta["opened"] = stored_open_meta
            else:
                stored_issue_meta["opened"] = open_issues_meta

            open_issues = get_issue_accord(stored_issue_meta["opened"])

            return [opened_tab_content(open_issues), stored_issue_meta]

    elif click_tab == "closed_tab":
        close_issues_meta = gitlab.get_issues_meta(state="closed")

        if len(close_issues_meta) == 0:
            close_issues = paragraph_comp(text="⦿ We do not have closed "
                                               "requests!", indent=40)
            return [closed_tab_content(close_issues), stored_issue_meta]
        else:
            stored_open_meta = stored_issue_meta["closed"]
            if len(stored_open_meta) == len(close_issues_meta):
                stored_issue_meta["closed"] = stored_open_meta
            else:
                stored_issue_meta["closed"] = close_issues_meta

            close_issues = get_issue_accord(stored_issue_meta["closed"])
        return [closed_tab_content(close_issues), stored_issue_meta]
    return html.P("This shouldn't ever be displayed...")
