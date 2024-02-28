import re

from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, State, MATCH, no_update, dcc

from ..components import (
    line_breaks, paragraph_comp, group_accordion, group_items, button_comp,
    chat_box, loading_comp, web_link, progressbar_comp, popup_comp, header_comp
)
from ..global_variables import request_gitlab, PATHNAME_PREFIX, DCEVENT_DOCS

PROGRESS_COMMENTS = [
    "STATE: setup",
    "STATE: queued",
    "STATE: done"
]

JOB_COMMENTS = [
    r"^Completed job",
    r"^We have (\d+) pipeline",
    "Access your data at"
]


def find_results_path(issue_notes):
    result_path = "No result path"
    for cmt in issue_notes["comments"]:
        if JOB_COMMENTS[2] in cmt:
            result_path = cmt.split("main/")[1]
            break
    return result_path


def find_job_stats(issue_notes):
    """Fetch total & completed no of pipelines info from issue comments"""
    # Initialize variables to hold total and finished job counts
    total_jobs = 0

    # Find the total number of pipelines
    for cmt in issue_notes["comments"]:
        if re.match(JOB_COMMENTS[1], cmt):
            total_jobs_match = re.search(JOB_COMMENTS[1], cmt)
            if total_jobs_match:
                total_jobs = int(total_jobs_match.group(1))
            break

    # Count the number of finished job comments
    finished_jobs = len([cmt for cmt in issue_notes["comments"] if
                         re.match(JOB_COMMENTS[0], cmt)])

    return total_jobs, finished_jobs


def welcome_tab_content():
    return [
        line_breaks(2),
        html.Div(
            html.Img(
                src="assets/pipeline_logo.jfif",
                style={"width": "800px", "height": "700px",
                       "marginLeft": "40px"}
            )
        ),
        line_breaks(2),
        dbc.Alert(
            [
                # Warning icon
                html.I(className="bi bi-info-circle-fill me-2"),
                paragraph_comp(
                    text="If you want to segment or/and classify your data, "
                         "use the Simple Request on the left.",
                    comp_id="dummy2"
                ),
            ],
            color="info",
            className="d-flex align-items-inline",
            style={"color": "black", "width": "fit-content",
                   "marginLeft": "40px", "height": "60px"},
        ),

        dbc.Alert(
            [
                # Warning icon
                html.I(className="bi bi-info-circle-fill me-2"),
                dcc.Markdown(
                    f"If you are an advanced user use the Advanced Request. "
                    f"More information at [dcevent pages]({DCEVENT_DOCS})."
                )
            ],
            color="info",
            className="d-flex align-items-inline",
            style={"color": "black", "width": "fit-content",
                   "marginLeft": "40px", "height": "60px"},
        ),
        line_breaks(2)
    ]


def workflow_tab_content():
    return [
        line_breaks(2),
        html.Div(
            html.Img(
                src="assets/hpc_workflow.jpg",
                style={"width": "1000px", "height": "900px"}
            ),
            className="row justify-content-center"
        ),
        line_breaks(2)
    ]


def create_accord_item_for_issue(issue):
    """Create an accordion item for a given issue"""
    return dbc.AccordionItem(
        [
            popup_comp(
                comp_id={"type": "stop_pipeline_popup",
                         "index": issue['iid']},
                refresh_path=PATHNAME_PREFIX,
                text="Pipeline request has been canceled!"
            ),
            html.H6("Pipeline Details:"),
            group_items([
                paragraph_comp(text=f"Created by: {issue['author']}"),
                paragraph_comp(text=f"Username: {issue['user']}"),
                paragraph_comp(text=f"Pipeline ID: {issue['id']}"),
                paragraph_comp(text=f"Date of Creation: {issue['date']}"),
                web_link(label=f"Go to GitLab issue - #{issue['iid']}",
                         url=issue["web_url"]),
                web_link(label="Download RTDC csv (Not Implemented)",
                         url="https://google.com"),
                button_comp(
                    label="Stop Pipeline", type="danger",
                    comp_id={"type": "accord_item_stop",
                             "index": issue['iid']},
                    disabled=True
                )
            ]),
            line_breaks(1),
            html.H6("Pipeline Status:"),
            dbc.ListGroup(
                [
                    dbc.ListGroupItem(
                        html.Div(
                            id={"type": "pipeline_status",
                                "index": issue['iid']},
                            style={'display': 'inline'}
                        ),
                        style={"width": "15%", "color": "#10e84a"}
                    ),
                    dbc.ListGroupItem(
                        progressbar_comp(
                            comp_id={"type": "accord_item_bar",
                                     "index": issue['iid']},
                            width=95
                        ),
                        style={"width": "85%"}
                    )
                ],
                horizontal=True
            ),
            line_breaks(1),
            html.H6("Result Path: (path to find results on S3-proxy)"),
            dbc.ListGroup(
                [
                    dbc.ListGroupItem(
                        html.P(
                            id={"type": "results_path", "index": issue['iid']},
                            style={'display': 'inline'}
                        ),
                        style={"color": "#10e84a"}
                    ),
                    dbc.ListGroupItem(
                        dcc.Clipboard(
                            target_id={"type": "results_path",
                                       "index": issue['iid']},
                            title="Copy Path",
                            style={
                                "display": "inline-block",
                                "fontSize": 20,
                                "verticalAlign": "top",
                            }
                        )
                    )
                ],
                horizontal=True,
            ),

            line_breaks(1),
            html.H6("Comments:"),
            loading_comp(
                html.Div(id={"type": "accord_item_div", "index": issue['iid']})
            )
        ],
        title=f"#{issue['iid']} {issue['name']}",
        item_id=f"accord_item{issue['iid']}"
    )


def get_pipeline_accords(issue_data):
    """Take GitLab issue metadata list and create a group of accordion items"""
    accord_items = [create_accord_item_for_issue(issue) for issue in issue_data]
    return [
        html.Div(
            group_accordion(
                accord_items,
                middle=True, comp_id="issue_accord"
            ),
            style={"max-height": "70rem", "overflow-y": "scroll",
                   "overflow-x": "hidden"},
        ),
        line_breaks(2)
    ]


def home_page_layout():
    """Create home page layout"""
    pagination = dbc.ListGroup(
        [
            dbc.ListGroupItem(
                loading_comp(
                    dbc.Pagination(
                        id="issues_pagination",
                        min_value=1,
                        max_value=1,
                        active_page=1,
                        first_last=True,
                        previous_next=True,
                        fully_expanded=False,
                        class_name="my-custom-pagination",
                    )
                )
            )
        ],
        horizontal=True, style={"justify-content": "center"}
    )
    return dbc.Card([
        dbc.Tabs(
            [
                dbc.Tab(
                    label="Welcome",
                    tab_id="welcome",
                    active_label_style={"color": "#10e84a"}
                ),
                dbc.Tab(
                    pagination,
                    label="Open requests",
                    tab_id="opened",
                    active_label_style={"color": "#10e84a"}
                ),
                dbc.Tab(
                    pagination,
                    label="Closed requests",
                    tab_id="closed",
                    active_label_style={"color": "#10e84a"}
                ),
                dbc.Tab(
                    label="Work Flow",
                    tab_id="workflow",
                    active_label_style={"color": "#10e84a"}
                )
            ],
            id="tabs",
            active_tab="welcome",
            persistence=True
        ),
        html.Div(id="tab_content")
    ])


@callback(
    Output("tab_content", "children"),
    Input("tabs", "active_tab"),
    Input("issues_pagination", "active_page")
)
def switch_tabs(active_tab, page):
    """Allow user to switch between welcome, opened, and closed tabs"""
    if active_tab == "welcome":
        return welcome_tab_content()
    elif active_tab == "workflow":
        return workflow_tab_content()
    else:
        issue_meta = request_gitlab.get_issues_meta(active_tab, page)
        if len(issue_meta) == 0:
            return html.Div([
                line_breaks(1),
                header_comp("⦿ No open requests!", indent=40),
                line_breaks(25)
            ])
        else:
            return get_pipeline_accords(issue_meta)


@callback(
    Output({"type": "accord_item_div", "index": MATCH}, "children"),
    Output({"type": "pipeline_status", "index": MATCH}, "children"),
    Output({"type": "results_path", "index": MATCH}, "children"),
    Output({"type": "accord_item_bar", "index": MATCH}, "value"),
    Output({"type": "accord_item_bar", "index": MATCH}, "label"),
    Input("issue_accord", "active_item"),
    State({"type": "accord_item_div", "index": MATCH}, "id"),
    prevent_initial_call=True
)
def show_pipeline_comments(accord_item, match_id):
    # Check if there is an active_item selected
    if not accord_item:
        return no_update, no_update, no_update, no_update, no_update

    # Parse issue_iid from active_item
    issue_iid = int(accord_item.split("item")[1])

    # Check if the active_item matches the current item
    if issue_iid == match_id["index"]:
        # Fetch comments for the issue from GitLab
        notes = request_gitlab.get_comments(issue_iid)
        comment_cards = chat_box(notes)
        # Get the result path from issue notes
        result_path = find_results_path(notes)
        # Get the total jobs and finished jobs numbers
        total_jobs, finished_jobs = find_job_stats(notes)
        # Show only comments if total jobs equal to zero
        if total_jobs == 0:
            return comment_cards, "Jobs: [0 / 0]", result_path, None, None

        # Calculate the progress percentage
        progress = (finished_jobs / total_jobs) * 85

        # Add 5% progress for specific state comments
        for state_comment in PROGRESS_COMMENTS:
            if state_comment in notes["comments"]:
                progress += 5

        return (
            comment_cards,
            f"Jobs: [{finished_jobs} / {total_jobs}]",
            result_path,
            progress,
            f"{progress:.0f} %"
        )
    else:
        return no_update, no_update, no_update, no_update, no_update


@callback(
    Output({"type": "accord_item_stop", "index": MATCH}, "disabled"),
    Output({"type": "stop_pipeline_popup", "index": MATCH}, "is_open"),
    Input("tabs", "active_tab"),
    Input({"type": "accord_item_div", "index": MATCH}, "children"),
    Input({"type": "accord_item_stop", "index": MATCH}, "n_clicks"),
    Input({"type": "stop_pipeline_popup", "index": MATCH}, "n_clicks"),
    State({"type": "accord_item_div", "index": MATCH}, "id"),
    State({"type": "stop_pipeline_popup", "index": MATCH}, "is_open"),
    prevent_initial_call=True
)
def toggle_stop_pipeline_button_and_cancel_pipeline(active_tab, issue_content,
                                                    stop_issue, close_popup,
                                                    match_id, popup):
    """Enable stop pipeline button for an opened issue only after the comments
    of that issue are loaded. Also, open a popup notification when the user
    cancel the pipeline (close GitLab issue), and refresh the page."""
    # Enable stop pipeline button for opened issue only if comments are loaded
    if active_tab != "opened" or not isinstance(issue_content, dict):
        return no_update, no_update
    # Get the issue comments
    comments = request_gitlab.get_comments(match_id["index"])["comments"]

    # Enable/Disable stop button based on 'cancel' comment in issue
    is_disabled = comments and comments[0].lower() == "cancel"

    # Stop pipeline and open a popup
    if stop_issue:
        request_gitlab.cancel_pipeline(match_id["index"])
        is_open = not popup
    # Close popup and refresh the page
    elif close_popup:
        is_open = not popup
    else:
        is_open = False
    return is_disabled, is_open


@callback(
    Output("issues_pagination", "max_value"),
    Input("tabs", "active_tab")
)
def update_pagination_max_value(active_tab):
    """Get the no of pages from GitLab and update the pagination max value"""
    if active_tab == "welcome" or active_tab == "workflow":
        raise PreventUpdate
    else:
        return request_gitlab.get_num_pages(active_tab)
