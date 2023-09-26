from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, State, MATCH

from ..components import (
    line_breaks, paragraph_comp, group_accordion, groupby_columns,
    header_comp, button_comp, chat_box, loading_comp, web_link,
    progressbar_comp, divider_line_comp, popup_comp
)
from ..global_variables import gitlab_obj, PATHNAME_PREFIX

PROGRESS_COMMENTS = [
    "STATE: setup",
    "STATE: queued",
    "STATE: done"
]


def open_close_tab_layout(pipelines):
    """Create open and close tab layout"""
    return html.Div(
        [
            line_breaks(times=2),
            html.Div(
                pipelines,
                style={"max-height": "70rem", "overflow-y": "scroll",
                       "overflow-x": "hidden"},
            )
        ],
        style={"height": "80rem", "background-color": "#424447"}
    )


def main_layout():
    """Create home page layout"""
    return dbc.Card(
        [
            dbc.CardHeader([
                dbc.Tabs(
                    [
                        dbc.Tab(label="Open requests", tab_id="opened",
                                active_label_style={"color": "#10e84a"}),
                        dbc.Tab(label="Closed requests", tab_id="closed",
                                active_label_style={"color": "#10e84a"}),
                    ],
                    id="tabs",
                    active_tab="opened",
                ),
            ]),
            dbc.Pagination(
                id="issues_pagination",
                min_value=1,
                max_value=1,
                active_page=1,
                first_last=True,
                previous_next=True,
                fully_expanded=False,
                style={"justify-content": "center"},
            ),
            html.Div(id="tab_content"),
        ],
    )


def create_accord_item_for_issue(isu, active_tab):
    """Create an accordion item for a given issue"""
    web_url = isu["web_url"]
    return dbc.AccordionItem(
        [
            paragraph_comp(text=f"Request created by: {isu['author']}"),
            paragraph_comp(text=f"Pipeline ID: {isu['id']}"),
            groupby_columns(
                [
                    web_link(label=f"GitLab issue - #{isu['iid']}",
                             url=web_url),
                    line_breaks(times=1),
                    web_link(label="Download RTDC csv",
                             url="https://google.com"),
                    line_breaks(times=1) if active_tab == "opened" else None,
                    button_comp(
                        label="Stop Pipeline", type="danger",
                        comp_id={"type": "accord_item_stop",
                                 "index": isu['iid']},
                        disabled=True
                    ) if active_tab == "opened" else None,
                    popup_comp(
                        comp_id={"type": "stop_pipeline_popup",
                                 "index": isu['iid']},
                        refresh_path=PATHNAME_PREFIX,
                        text="Pipeline request has been canceled!"
                    ) if active_tab == "opened" else None,
                    line_breaks(times=2) if active_tab == "opened" else None
                ]
            ),
            divider_line_comp(),
            line_breaks(times=1),
            progressbar_comp(
                comp_id={"type": "accord_item_bar", "index": isu['iid']}),
            line_breaks(times=2),
            divider_line_comp(),
            header_comp(text="Comments:"),
            loading_comp(
                html.Div(id={"type": "accord_item_div", "index": isu['iid']})
            )
        ],
        title=f"#{isu['iid']} {isu['name']}",
        item_id=f"accord_item{isu['iid']}"
    )


def get_issues_accord(active_tab, issue_data):
    """Take GitLab issue list and create a group of accordion items"""
    return group_accordion(
        [create_accord_item_for_issue(isu, active_tab) for isu in issue_data],
        middle=True, comp_id="issue_accord"
    )


@callback(
    Output("tab_content", "children"),
    Input("tabs", "active_tab"),
    Input("issues_pagination", "active_page"),
)
def switch_tabs(active_tab, page):
    """Allow user to switch between opened and closed tabs"""
    issue_meta = gitlab_obj.get_issues_meta(active_tab, page)
    issues = get_issues_accord(active_tab, issue_meta)
    return open_close_tab_layout(issues)


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
        notes = gitlab_obj.get_comments(issue_iid)
        match_len = len(set(PROGRESS_COMMENTS).intersection(notes["comments"]))
        progress = (match_len / len(PROGRESS_COMMENTS)) * 100

        comment_cards = chat_box(notes)

        if issue_iid == match_id["index"]:
            return comment_cards, progress, f"{progress:.1f} %"

    raise PreventUpdate


@callback(
    Output({"type": "accord_item_stop", "index": MATCH}, "disabled"),
    Input({"type": "accord_item_div", "index": MATCH}, "children"),
    State({"type": "accord_item_stop", "index": MATCH}, "disabled"),
)
def toggle_stop_pipeline_button(issue_content, disable):
    """Enable the stop pipeline button in an issue only after the comments
    of that issue are loaded"""
    if isinstance(issue_content, dict):
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
            gitlab_obj.cancel_pipeline(issue_iid)
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
    return gitlab_obj.get_num_pages(active_tab)
