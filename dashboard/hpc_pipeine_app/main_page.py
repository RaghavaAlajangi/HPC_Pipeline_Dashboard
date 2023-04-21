import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, MATCH

from ..components import (line_breaks, paragraph_comp, group_accordion,
                          dropdown_menu_comp, groupby_columns, header_comp,
                          button_comp, chat_box, loading_comp, web_link,
                          progressbar_comp, divider_line_comp)
from ..gitlab_api import gitlab_api

# Get the issue meta from gitlab API to store in dash cache memory
opened_issues = gitlab_api.get_issues_meta(state="opened")
closed_issues = gitlab_api.get_issues_meta(state="closed")


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
                       indent=2),
        line_breaks(times=1),
        dropdown_menu_comp(name="New Request",
                           options=[dropdown_menu1, dropdown_menu2],
                           indent=40),
    ],
        className="mt-3",
        style={"height": "50rem", "background-color": "#424447"}
    )


def open_close_tab_layout(pipelines):
    return dbc.Card([
        line_breaks(times=2),
        html.Div(id="test", children=[]),
        html.Div(
            pipelines,
            style={"max-height": "50rem", "overflow-y": "scroll",
                   "overflowX": "hidden"},
        ),
        line_breaks(times=2),
    ],
        className="mt-3",
        style={"height": "50rem", "background-color": "#424447"}
    )


def tabs_layout():
    return dbc.Card([
        dbc.CardHeader(
            dbc.Tabs([
                dbc.Tab(label="Main",
                        tab_id="main_tab",
                        active_label_style={"color": "#017b70"}),
                dbc.Tab(label="Open requests",
                        tab_id="opened",
                        active_label_style={"color": "#017b70"}),
                dbc.Tab(label="Closed requests",
                        tab_id="closed",
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
        dcc.Store(id="store_gitlab_issues",
                  data={"opened": opened_issues,
                        "closed": closed_issues}),
    ])


def get_issue_accord(active_tab, data):
    return group_accordion([
        dbc.AccordionItem([
            paragraph_comp(text="Request created by: {}".format(c["author"])),
            paragraph_comp(text=f"Pipeline ID: {c['id']}"),
            groupby_columns([
                web_link(label=f"GitLab issue - #{c['iid']}",
                         url=c["web_url"]),
                line_breaks(times=1),
                web_link(label="Download RTDC csv",
                         url="https://google.com"),
                # dcc.Download(id="download_rtdc_csv"),
                line_breaks(times=1),
                # Remove button component for closed pipelines
                button_comp(label="Stop Pipeline", type="danger",
                            comp_id={"type": "accord_item_stop", "index": c[
                                'iid']}) if active_tab == "opened" else "",

                line_breaks(times=2) if active_tab == "opened" else "",
            ]),
            divider_line_comp(),
            line_breaks(times=1),
            # Progress bar
            progressbar_comp(comp_id={"type": "accord_item_bar",
                                      "index": c['iid']}),
            line_breaks(times=2),
            divider_line_comp(),
            header_comp(text="Comments:"),

            # This is a special way of creating id's for components
            # (dynamically changing) that are created via a callback
            # function. We can refer these id's in a different callback
            # (as output id's) to do actions like show/store
            loading_comp(html.Div(id={"type": "accord_item_div",
                                      "index": c['iid']})),
        ],
            title=c["name"],
            item_id=f"accord_item{c['iid']}"
        ) for c in data
    ],
        middle=True, comp_id="issue_accord"
    )


def switch_tab_content(active_tab, dash_cache):
    new_issue_meta = gitlab_api.get_issues_meta(state=active_tab)

    if len(new_issue_meta) == 0:
        issues = paragraph_comp(text="⦿ No opened requests!", indent=2)
        return [open_close_tab_layout(issues), dash_cache]
    else:
        if len(dash_cache[active_tab]) != len(new_issue_meta):
            dash_cache[active_tab] = new_issue_meta
        issues = get_issue_accord(active_tab, dash_cache[active_tab])
        return [open_close_tab_layout(issues), dash_cache]


@callback([Output("tab_content", "children"),
           Output("store_gitlab_issues", "data")],
          Input("tabs", "active_tab"),
          State("store_gitlab_issues", "data"))
def switch_tabs(active_tab, stored_issue_meta):
    if active_tab == "main_tab":
        return [main_tab_layout(), stored_issue_meta]
    else:
        return switch_tab_content(active_tab, stored_issue_meta)


@callback(Output({"type": "accord_item_div", "index": MATCH}, "children"),
          Output({"type": "accord_item_bar", "index": MATCH}, "value"),
          Output({"type": "accord_item_bar", "index": MATCH}, "label"),
          Input("issue_accord", "active_item"),
          State({"type": "accord_item_div", "index": MATCH}, "id"))
def show_pipeline_comments(accord_item, match_id):
    progress_comments = [
        "STATE: setup",
        "STATE: queued",
        "STATE: done",
    ]
    if accord_item is not None:
        issue_iid = int(accord_item.split("item")[1])
        comments = gitlab_api.get_comments(issue_iid)

        match_len = len(set(progress_comments).intersection(comments))
        progress = (match_len / len(progress_comments)) * 100

        if len(comments) != 0:
            comment_cards = chat_box(comments)
        else:
            comment_cards = chat_box(["No Activity!"])

        if issue_iid == match_id["index"]:
            return comment_cards, progress, f"{progress:.1f} %"
        else:
            return dash.no_update
    else:
        return dash.no_update


@callback(Output({"type": "accord_item_stop", "index": MATCH}, "disabled"),
          Input("issue_accord", "active_item"),
          Input({"type": "accord_item_stop", "index": MATCH}, "n_clicks"),
          State({"type": "accord_item_stop", "index": MATCH}, "disabled"))
def cancel_pipeline(accord_item, click, enable_click):
    if accord_item is not None:
        issue_iid = int(accord_item.split("item")[1])
        issue_obj = gitlab_api.get_issue_obj(issue_iid)
        if click is not None and click > 0:
            issue_obj.notes.create({"body": "Cancel"})
            return True
        else:
            return False

    return dash.no_update
