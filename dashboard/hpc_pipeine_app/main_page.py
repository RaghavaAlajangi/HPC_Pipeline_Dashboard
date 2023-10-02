from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, State, MATCH

from ..components import (
    line_breaks, paragraph_comp, group_accordion, group_items,
    header_comp, button_comp, chat_box, loading_comp, web_link,
    progressbar_comp, popup_comp
)
from ..global_variables import request_gitlab, PATHNAME_PREFIX

PROGRESS_COMMENTS = [
    "STATE: setup",
    "STATE: queued",
    "STATE: done"
]


def welcome_tab_content():
    return [
        line_breaks(2),
        html.Div(
            html.Img(src='assets/overview.PNG', alt='My Image',
                     style={'width': '800px', 'height': '500px'}),
            className="row justify-content-center"
        ),
        line_breaks(2),
    ]


def open_close_tab_layout(pipelines):
    """Create open and close tab layout"""
    return [
        html.Div(
            pipelines,
            style={"max-height": "70rem", "overflow-y": "scroll",
                   "overflow-x": "hidden"},
        ),
        line_breaks(2)
    ]


def main_layout():
    """Create home page layout"""
    pagination = dbc.Pagination(
        id="issues_pagination",
        min_value=1,
        max_value=1,
        active_page=1,
        first_last=True,
        previous_next=True,
        fully_expanded=False,
        style={"justify-content": "center"},
    )
    return dbc.Card(
        [
            dbc.Tabs(
                [
                    dbc.Tab(label="Welcome", tab_id="welcome",
                            active_label_style={"color": "#10e84a"}),
                    dbc.Tab(pagination, label="Open requests",
                            tab_id="opened",
                            active_label_style={"color": "#10e84a"}),
                    dbc.Tab(pagination, label="Closed requests",
                            tab_id="closed",
                            active_label_style={"color": "#10e84a"}),
                ],
                id="tabs",
                active_tab="welcome",
            ),
            html.Div(id="tab_content"),
        ],
    )


def create_accord_item_for_issue(issue):
    """Create an accordion item for a given issue"""
    web_url = issue["web_url"]
    return dbc.AccordionItem(
        [
            popup_comp(
                comp_id={"type": "stop_pipeline_popup",
                         "index": issue['iid']},
                refresh_path=PATHNAME_PREFIX,
                text="Pipeline request has been canceled!"
            ),
            header_comp(text="Pipeline Details:"),

            group_items(
                [
                    paragraph_comp(text=f"Created by: {issue['author']}"),
                    paragraph_comp(text=f"Pipeline ID: {issue['id']}"),
                    paragraph_comp(text=f"Date of Creation: {issue['date']}"),
                    web_link(label=f"Go to GitLab issue - #{issue['iid']}",
                             url=web_url),
                    web_link(label="Download RTDC csv (Not Implemented)",
                             url="https://google.com"),
                    button_comp(
                        label="Stop Pipeline", type="danger",
                        comp_id={"type": "accord_item_stop",
                                 "index": issue['iid']},
                        disabled=True
                    )
                ]
            ),
            line_breaks(1),
            header_comp(text="Progress Bar:"),
            group_items([
                progressbar_comp(
                    comp_id={"type": "accord_item_bar",
                             "index": issue['iid']}
                )
            ]),
            line_breaks(1),
            header_comp(text="Comments:"),
            loading_comp(
                html.Div(id={"type": "accord_item_div", "index": issue['iid']})
            )
        ],
        title=f"#{issue['iid']} {issue['name']}",
        item_id=f"accord_item{issue['iid']}"
    )


def get_issues_accord(issue_data):
    """Take GitLab issue list and create a group of accordion items"""
    return group_accordion(
        [create_accord_item_for_issue(issue) for issue in issue_data],
        middle=True, comp_id="issue_accord"
    )


@callback(
    Output("tab_content", "children"),
    Input("tabs", "active_tab"),
    Input("issues_pagination", "active_page"),
)
def switch_tabs(active_tab, page):
    """Allow user to switch between welcome, opened, and closed tabs"""
    if active_tab == "welcome":
        return welcome_tab_content()
    else:
        issue_meta = request_gitlab.get_issues_meta(active_tab, page)
        issue_accords = get_issues_accord(issue_meta)
        return open_close_tab_layout(issue_accords)


@callback(
    Output({"type": "accord_item_div", "index": MATCH}, "children"),
    Output({"type": "accord_item_bar", "index": MATCH}, "value"),
    Output({"type": "accord_item_bar", "index": MATCH}, "label"),
    Input("issue_accord", "active_item"),
    State({"type": "accord_item_div", "index": MATCH}, "id")
)
def show_pipeline_comments(accord_item, match_id):
    """Show the content of an issue only when the user clicks on issue
    accordian item otherwise do not load"""
    if accord_item:
        issue_iid = int(accord_item.split("item")[1])
        notes = request_gitlab.get_comments(issue_iid)
        match_len = len(set(PROGRESS_COMMENTS).intersection(notes["comments"]))
        progress = (match_len / len(PROGRESS_COMMENTS)) * 100

        comment_cards = chat_box(notes)

        if issue_iid == match_id["index"]:
            return comment_cards, progress, f"{progress:.1f} %"

    raise PreventUpdate


@callback(
    Output({"type": "accord_item_stop", "index": MATCH}, "disabled"),
    Input({"type": "accord_item_div", "index": MATCH}, "children"),
    Input("tabs", "active_tab"),
    State({"type": "accord_item_stop", "index": MATCH}, "disabled"),
)
def toggle_stop_pipeline_button(issue_content, tab, disable):
    """Enable the stop pipeline button in an issue only after the comments
    of that issue are loaded and for issues in opened tab"""
    if isinstance(issue_content, dict) and tab == "opened":
        return not disable
    return disable


@callback(
    Output({"type": "stop_pipeline_popup", "index": MATCH}, "is_open"),
    Input("issue_accord", "active_item"),
    Input({"type": "accord_item_stop", "index": MATCH}, "n_clicks"),
    Input({"type": "stop_pipeline_popup", "index": MATCH}, "n_clicks"),
    State({"type": "stop_pipeline_popup", "index": MATCH}, "is_open")
)
def cancel_pipeline(active_issue, stop_issue, close_popup, popup):
    """Cancel pipeline, close GitLab issue, and refresh page"""
    if active_issue:
        issue_iid = int(active_issue.split("item")[1])
        if stop_issue:
            request_gitlab.cancel_pipeline(issue_iid)
            return not popup
    if close_popup:
        return not popup
    raise PreventUpdate


@callback(
    Output("issues_pagination", "max_value"),
    Input("tabs", "active_tab"),
)
def update_pagination_max_value(active_tab):
    """Get the no of pages from GitLab and update the pagination max value"""
    if active_tab == "welcome":
        raise PreventUpdate
    else:
        return request_gitlab.get_num_pages(active_tab)
