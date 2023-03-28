import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, MATCH

from ..components import line_breaks, paragraph_comp, group_accordion, \
    dropdown_menu_comp, groupby_columns, header_comp, button_comp, \
    chat_box
from ..gitlab_api import gitlab_api

# Get the issue meta from gitlab API to store in dash cache memory
opened = gitlab_api.get_issues_meta(state="opened")
closed = gitlab_api.get_issues_meta(state="closed")


def main_tab_layout():
    dropdown_menu1 = dbc.DropdownMenuItem([
        dbc.NavLink("Simple",
                    href="/hpc_pipelines/simple",
                    id="open_simple_request_page",
                    active=True)
    ])
    dropdown_menu2 = dbc.DropdownMenuItem([
        dbc.NavLink("Advanced",
                    href="/hpc_pipelines/advanced",
                    id="open_advance_request_page",
                    active=True),
    ])
    return dbc.Card([
        line_breaks(times=1),
        paragraph_comp("⦿ This page is responsible for running RTDC "
                       "dataset processing pipelines on MPCDF gpu "
                       "clusters (HPC)",
                       indent=40),
        line_breaks(times=1),
        dropdown_menu_comp(name="New Request",
                           components=[dropdown_menu1, dropdown_menu2],
                           indent=40),
    ],
        className="mt-3",
        style={"height": "50rem", 'background-color': "#424447"}
    )


def open_close_tab_layout(pipelines):
    return dbc.Card([
        line_breaks(times=2),
        html.Div(id='test', children=[]),
        html.Div(
            pipelines,
            style={"max-height": "50rem", "overflow-y": "scroll",
                   "overflowX": "hidden"},
        ),
        line_breaks(times=2),
    ],
        className="mt-3",
        style={"height": "50rem", 'background-color': "#424447"}
    )


def tabs_layout():
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
        tabs_layout(),
        dcc.Store(id='store_gitlab_issues',
                  data={"opened": opened,
                        "closed": closed}),
    ])


def get_issue_accord(data, accord_id="issue_accord"):
    return group_accordion([
        dbc.AccordionItem([
            paragraph_comp(text="Request created by: {}".format(c["author"])),
            paragraph_comp(text=f"Pipeline ID: {c['id']}"),
            groupby_columns([
                html.A("See the issue on GitLab",
                       href=c["web_url"], target='_blank',
                       style={"text-decoration": "none"}
                       ),
                line_breaks(times=1),
                button_comp(label="Stop Pipeline",
                            type="danger",
                            comp_id=f"accord_item_stop_{c['iid']}"),

                line_breaks(times=2),
                header_comp(text="Comments:"),

                # This is a special way of creating id's for components
                # (dynamically changing) that are created via a callback
                # function. We can refer these id's in a different callback
                # (as output id's) to do actions like show/store
                html.Div(id={'type': 'accord_item_div', 'index': c['iid']})
            ]),
        ],
            title=c["name"],
            item_id=f"accord_item{c['iid']}"
        ) for c in data
    ],
        middle=True, width=70, comp_id=accord_id
    )


def switch_tab_content(active_tab, dash_cache):
    new_issue_meta = gitlab_api.get_issues_meta(state=active_tab)

    if len(new_issue_meta) == 0:
        issues = paragraph_comp(text="⦿ We do not have opened "
                                     "requests!", indent=40)
        return [open_close_tab_layout(issues), dash_cache]
    else:
        if len(dash_cache[active_tab]) != len(new_issue_meta):
            dash_cache[active_tab] = new_issue_meta
        issues = get_issue_accord(dash_cache[active_tab])
        return [open_close_tab_layout(issues), dash_cache]


@callback([Output("tab_content", "children"),
           Output("store_gitlab_issues", "data")],
          Input("tabs", "active_tab"),
          State("store_gitlab_issues", "data"))
def switch_tabs(active_tab, stored_issue_meta):
    if active_tab == "main_tab":
        return [main_tab_layout(), stored_issue_meta]
    elif active_tab == "opened_tab":
        return switch_tab_content("opened", stored_issue_meta)
    elif active_tab == "closed_tab":
        return switch_tab_content("closed", stored_issue_meta)
    return html.P("This shouldn't ever be displayed...")


@callback(Output({'type': 'accord_item_div', 'index': MATCH}, 'children'),
          Input("issue_accord", "active_item"),
          State({'type': 'accord_item_div', 'index': MATCH}, 'id'))
def show_selected_issue_comments(accord_item, match_id):

    if accord_item is not None:
        issue_iid = int(accord_item.split("item")[1])
        comments = gitlab_api.get_comments(issue_iid)

        if len(comments) != 0:
            comment_cards = chat_box(comments)
        else:
            comment_cards = chat_box(["No Activity!"])

        if issue_iid == match_id["index"]:
            return comment_cards
