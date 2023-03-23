from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc


# from .. import gitlab_api
#
# issues_opened = gitlab_api.get_issues(status="opened")
# issues_closed = gitlab_api.get_issues(status="closed")
# meta_data_open = gitlab_api.get_issues_metadata(issues_opened)
# meta_data_close = gitlab_api.get_issues_metadata(issues_closed)


def main_request_card():
    return dbc.Card([
        html.Br(),
        html.P("⦿ This page is responsible for running RTDC dataset "
               "processing pipelines on MPCDF gpu clusters (HPC)"),
        html.Br(),

        dbc.DropdownMenu([
            dbc.DropdownMenuItem([
                dbc.NavLink("Simple",
                            href="/hpc_pipelines/simple",
                            id="open_simple_request_page",
                            active=True),
            ]),
            dbc.DropdownMenuItem([
                dbc.NavLink("Advanced",
                            href="/hpc_pipelines/advanced",
                            id="open_advance_request_page",
                            active=True),
            ]),
        ],
            label="New Request",
        )
    ],
        className="mt-3",
        style={"height": "50rem", 'background-color': "#424447"}
    )


def opened_request_card(open_issues):
    return dbc.Card([
        dbc.CardBody(
            html.Div(
                open_issues,
                id="open_issue_card",
                # style={"max-height": "50rem", "overflow-y": "scroll"},
            ),
        )
    ],
        className="mt-3",
        style={"height": "50rem", 'background-color': "#424447"}
    )


def closed_request_card():
    return dbc.Card(
        dbc.CardBody([
            html.P("This is tab 2!", className="card-text"),
            dbc.Button("Don't click here", color="danger"),
        ]),
        id="close_issue_card",
        className="mt-3",
        style={"height": "50rem", 'background-color': "#424447"}
    )


def request_tabs():
    return dbc.Card([
        dbc.CardHeader(
            dbc.Tabs([
                dbc.Tab(label="Main tab",
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
        dcc.Store(id='store_gitlab_issues', data={})
        # data={"closed_metadata": meta_data_close,
        #       "opened_metadata": meta_data_open}),
    ])


@callback([Output("tab_content", "children"),
           Output("store_gitlab_issues", "data")],
          Input("tabs", "active_tab"),
          State("store_gitlab_issues", "data"))
def switch_tab(click_tab, issue_data):
    if click_tab == "main_tab":
        return [main_request_card(), issue_data]
    elif click_tab == "opened_tab":
        # opened_issues = gitlab_api.get_issues(status="opened")
        # opened_issues_meta = gitlab_api.get_issues_metadata(opened_issues)
        # stored_opened_meta = issue_data["opened_metadata"]
        #
        # if len(stored_opened_meta) == len(opened_issues_meta):
        #     issue_data["opened_metadata"] = stored_opened_meta
        # else:
        #     issue_data["opened_metadata"] = opened_issues_meta
        #
        # toasts = dbc.Accordion([
        #     dbc.AccordionItem([
        #         html.P(c["author"], style={"color": "white"}),
        #         html.P(c["web_url"], style={"color": "white"}),
        #     ],
        #         title=c["name"],
        #     ) for c in issue_data["opened_metadata"]
        # ])
        return [opened_request_card([]), issue_data]

    elif click_tab == "closed_tab":
        # closed_issues = gitlab_api.get_issues(status="closed")
        # closed_issues_meta = gitlab_api.get_issues_metadata(closed_issues)
        # stored_opened_meta = issue_data["closed_metadata"]
        return [closed_request_card(), issue_data]
    return html.P("This shouldn't ever be displayed...")
