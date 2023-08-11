from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, MATCH

from ..components import (
    line_breaks, paragraph_comp, group_accordion, groupby_columns,
    header_comp, button_comp, chat_box, loading_comp, web_link,
    progressbar_comp, divider_line_comp
)
from ..gitlab_api import get_gitlab_obj

PROGRESS_COMMENTS = [
    "STATE: setup",
    "STATE: queued",
    "STATE: done"
]

gitlab_obj = get_gitlab_obj()


def fetch_issues(state):
    return gitlab_obj.get_issues_meta(state=state)


opened_issues = fetch_issues(state="opened")
closed_issues = fetch_issues(state="closed")


def main_tab_layout():
    text = "⦿ This page is responsible for running RTDC dataset " \
           "processing pipelines on MPCDF gpu clusters (HPC)"
    return dbc.Card(
        [
            line_breaks(times=1),
            paragraph_comp(text=text, indent=2)
        ],
        style={"height": "80rem", "background-color": "#424447"}
    )


def open_close_tab_layout(pipelines):
    return dbc.Card(
        [
            line_breaks(times=2),
            html.Div(id="test", children=[]),
            html.Div(
                pipelines,
                style={"max-height": "70rem", "overflow-y": "scroll",
                       "overflow-x": "hidden"},
            ),
            line_breaks(times=2)
        ],
        style={"height": "80rem", "background-color": "#424447"}
    )


def tabs_layout():
    return dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs(
                    [
                        # dbc.Tab(label="Main", tab_id="main_tab",
                        #         active_label_style={"color": "#017b70"}),
                        dbc.Tab(label="Open requests", tab_id="opened",
                                active_label_style={"color": "#017b70"}),
                        dbc.Tab(label="Closed requests", tab_id="closed",
                                active_label_style={"color": "#017b70"}),
                    ],
                    id="tabs",
                    active_tab="opened"
                )
            ),
            html.Div(id="tab_content")
        ]
    )


def main_layout():
    return html.Div(
        [
            tabs_layout(),
            dcc.Store(
                id="store_gitlab_issues",
                data={"opened": opened_issues,
                      "closed": closed_issues}
            )
        ]
    )


def get_issue_accord(active_tab, data):
    def create_accordion_item(c):
        web_url = c["web_url"]
        return dbc.AccordionItem(
            [
                paragraph_comp(text=f"Request created by: {c['author']}"),
                paragraph_comp(text=f"Pipeline ID: {c['id']}"),
                groupby_columns(
                    [
                        web_link(label=f"GitLab issue - #{c['iid']}",
                                 url=web_url),
                        line_breaks(times=1),
                        web_link(label="Download RTDC csv",
                                 url="https://google.com"),
                        line_breaks(
                            times=1) if active_tab == "opened" else None,
                        button_comp(
                            label="Stop Pipeline", type="danger",
                            comp_id={"type": "accord_item_stop",
                                     "index": c['iid']}
                        ) if active_tab == "opened" else None,
                        line_breaks(times=2) if active_tab == "opened" else None
                    ]
                ),
                divider_line_comp(),
                line_breaks(times=1),
                progressbar_comp(
                    comp_id={"type": "accord_item_bar", "index": c['iid']}),
                line_breaks(times=2),
                divider_line_comp(),
                header_comp(text="Comments:"),
                loading_comp(
                    html.Div(id={"type": "accord_item_div", "index": c['iid']})
                )
            ],
            title=f"#{c['iid']} {c['name']}",
            item_id=f"accord_item{c['iid']}"
        )

    return group_accordion([create_accordion_item(com) for com in data],
                           middle=True, comp_id="issue_accord")


def switch_tab_content(active_tab, dash_cache):
    new_issue_meta = fetch_issues(active_tab)

    if not new_issue_meta:
        issues = paragraph_comp(text="⦿ No opened requests!", indent=2)
        return [open_close_tab_layout(issues), dash_cache]

    if len(dash_cache[active_tab]) != len(new_issue_meta):
        dash_cache[active_tab] = new_issue_meta

    issues = get_issue_accord(active_tab, dash_cache[active_tab])
    return open_close_tab_layout(issues), dash_cache


@callback(
    Output("tab_content", "children"),
    Output("store_gitlab_issues", "data"),
    Input("tabs", "active_tab"),
    State("store_gitlab_issues", "data")
)
def switch_tabs(active_tab, stored_issue_meta):
    # if active_tab == "main_tab":
    #     return [main_tab_layout(), stored_issue_meta]
    return switch_tab_content(active_tab, stored_issue_meta)


@callback(
    Output({"type": "accord_item_div", "index": MATCH}, "children"),
    Output({"type": "accord_item_bar", "index": MATCH}, "value"),
    Output({"type": "accord_item_bar", "index": MATCH}, "label"),
    Input("issue_accord", "active_item"),
    State({"type": "accord_item_div", "index": MATCH}, "id")
)
def show_pipeline_comments(accord_item, match_id):
    if accord_item:
        issue_iid = int(accord_item.split("item")[1])
        comments = gitlab_obj.get_comments(issue_iid)
        match_len = len(set(PROGRESS_COMMENTS).intersection(comments))
        progress = (match_len / len(PROGRESS_COMMENTS)) * 100

        comment_cards = chat_box(comments if comments else ["No Activity!"])

        if issue_iid == match_id["index"]:
            return comment_cards, progress, f"{progress:.1f} %"

    raise PreventUpdate


@callback(
    Output({"type": "accord_item_stop", "index": MATCH}, "disabled"),
    Input("issue_accord", "active_item"),
    Input({"type": "accord_item_stop", "index": MATCH}, "n_clicks"),
    State({"type": "accord_item_stop", "index": MATCH}, "disabled")
)
def cancel_pipeline(accord_item, click, enable_click):
    if accord_item:
        issue_iid = int(accord_item.split("item")[1])
        issue_obj = gitlab_obj.get_issue_obj(issue_iid)
        if click:
            issue_obj.notes.create({"body": "Cancel"})
            issue_obj.state_event = "close"
            issue_obj.save()
            return True
    raise PreventUpdate
