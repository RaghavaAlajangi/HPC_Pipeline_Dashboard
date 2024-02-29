import re

from dash import callback, dcc, html, Input, MATCH, no_update, Output, State
import dash_bootstrap_components as dbc
from dash import callback_context as ctx
import dash_mantine_components as dmc

from ..components import (button_comp, chat_box, create_list_group,
                          group_accordion, header_comp,
                          line_breaks, loading_comp, paragraph_comp,
                          progressbar_comp, popup_comp, web_link
                          )
from ..global_variables import request_gitlab, PATHNAME_PREFIX, DCEVENT_DOCS

PROGRESS_COMMENTS = [
    "STATE: setup",
    "STATE: queued",
    "STATE: done"
]

JOB_COMMENTS = [
    re.compile(r"^Completed job"),
    re.compile(r"^We have (\d+) pipeline"),
    re.compile(r"Access all your experiments at:\s*(https?://\S+)")
]


def parse_job_stats(issue_notes):
    """Fetch total & completed no of pipelines info and results path from
    issue comments"""
    # Initialize variables
    total_jobs = 0
    finished_jobs = 0
    results_path = "No result path"

    # Iterate over comments
    for cmt in issue_notes["comments"]:
        # Check for total number of pipelines
        total_match = JOB_COMMENTS[1].match(cmt)
        if total_match:
            total_jobs = int(total_match.group(1))

        # Check for completed job
        if JOB_COMMENTS[0].match(cmt):
            finished_jobs += 1

        # Check for results path
        results_match = JOB_COMMENTS[2].search(cmt)
        if results_match:
            results_path = f"P:/{results_match.group(1).split('main/')[1]}"

    return total_jobs, finished_jobs, results_path


def welcome_tab_content():
    """Welcome tab content"""
    return dbc.ListGroup(
        children=dbc.ListGroupItem(
            children=[
                line_breaks(2),
                html.Img(
                    src="assets/pipeline_logo.jfif",
                    style={"width": "800px", "height": "700px",
                           "marginLeft": "40px"}
                ),
                line_breaks(2),
                dbc.Alert(
                    children=[
                        # Warning icon
                        html.I(className="bi bi-info-circle-fill me-2"),
                        paragraph_comp(
                            text="If you want to segment or/and classify your "
                                 "data, use the Simple Request on the left.",
                            comp_id="dummy2"
                        ),
                    ],
                    className="d-flex align-items-inline",
                    color="info",
                    style={"color": "black", "width": "fit-content",
                           "marginLeft": "40px", "height": "60px"}
                ),
                dbc.Alert(
                    children=[
                        # Warning icon
                        html.I(className="bi bi-info-circle-fill me-2"),
                        dcc.Markdown(
                            f"If you are an advanced user use the Advanced "
                            f"Request. More information at [dcevent pages]"
                            f"({DCEVENT_DOCS})."
                        )
                    ],
                    className="d-flex align-items-inline",
                    color="info",
                    style={"color": "black", "width": "fit-content",
                           "marginLeft": "40px", "height": "60px"},
                ),
                line_breaks(2)
            ]
        )
    )


def workflow_tab_content():
    """Workflow tab content"""
    return dbc.ListGroup(
        children=dbc.ListGroupItem(
            children=[
                line_breaks(2),
                html.Div(
                    children=html.Img(
                        src="assets/hpc_workflow.jpg",
                        style={"width": "1000px", "height": "900px"}
                    ),
                    className="row justify-content-center"
                ),
                line_breaks(2)
            ]
        )
    )


def get_tab_content(tab_id, load_id):
    """Placeholder for opened and closed tab content. This function has
    search bar to find specific pipeline and `Previous` and `Next` buttons
    for the pagination.
    """
    return dbc.CardBody([
        dbc.ListGroup([
            # Pipeline search bar
            dbc.ListGroupItem(
                children=dbc.Input(
                    class_name="custom-placeholder",
                    id="issue_filter",
                    placeholder="Filter pipelines with username or "
                                "title or keywords...",
                    style={"width": "100%", "color": "black"},
                    type="text",
                ),
                style={"width": "80%"}
            ),
            dbc.ListGroupItem(
                children=dcc.Loading(
                    color="#10e84a", id=load_id,
                    parent_style={"position": "center"}
                ),
                style={"width": "20%"}
            ),
        ], horizontal=True),
        # Placeholder for pipeline data to be displayed
        dbc.ListGroup([
            dbc.ListGroupItem(id=tab_id)
        ]),
        # Previous and next buttons
        dbc.ListGroup([
            dbc.ListGroupItem(
                dbc.Button(
                    children="< Prev", color="info", disabled=True,
                    id="prev_button", n_clicks=0
                )
            ),
            dbc.ListGroupItem(
                dbc.Button(
                    children="Next >", color="info", disabled=True,
                    id="next_button", n_clicks=0
                )
            ),
            # Cache page number on the browser
            dcc.Store(id="store_page_num", storage_type="memory", data=1)
        ],
            horizontal=True,
            style={"justify-content": "center"}
        )
    ])


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
            create_list_group([
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
        title=f"#{issue['iid']} {issue['title']}",
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
    """Creates home page layout"""
    return dbc.Card([
        dmc.Tabs(
            children=[
                dmc.TabsList([
                    dmc.Tab(
                        children="Welcome",
                        value="welcome",
                        style={"color": "white"},
                    ),
                    dmc.Tab(
                        children="Open requests",
                        value="opened",
                        style={"color": "white"},
                        rightSection=dbc.Badge(
                            color="#10e84a", id="open_tab_badge",
                            pill=True, text_color="black"
                        )
                    ),
                    dmc.Tab(
                        children="Closed requests",
                        rightSection=dbc.Badge(
                            color="#10e84a", id="close_tab_badge",
                            pill=True, text_color="black"
                        ),
                        style={"color": "white"},
                        value="closed"
                    ),
                    dmc.Tab(
                        children="Work Flow",
                        style={"color": "white"},
                        value="workflow"
                    )
                ]),
                dmc.TabsPanel(
                    children=welcome_tab_content(),
                    value="welcome"
                ),
                dmc.TabsPanel(
                    children=get_tab_content(tab_id="opened_content",
                                             load_id="opened_loading"),
                    value="opened"
                ),
                dmc.TabsPanel(
                    children=get_tab_content(tab_id="closed_content",
                                             load_id="closed_loading"),
                    value="closed"
                ),
                dmc.TabsPanel(
                    children=workflow_tab_content(),
                    value="workflow"
                ),

                dcc.Store(data={}, id="store_pipeline_notes",
                          storage_type="memory")
            ],
            color="green",
            id="main_tabs",
            persistence=True,
            value="welcome",
            variant="outline"
        )
    ])


@callback(
    Output("store_page_num", "data"),
    Output("prev_button", "disabled"),
    Input("prev_button", "n_clicks"),
    Input("next_button", "n_clicks"),
    State("store_page_num", "data")
)
def update_page(pclick, nclick, page_num):
    """Cache page number when user click on `Previous` and `Next` buttons"""
    triggered_id = ctx.triggered_id

    if triggered_id == "next_button":
        page_num += 1
    elif triggered_id == "prev_button":
        page_num -= 1
    is_disable = page_num < 2
    return page_num, is_disable


@callback(
    Output("open_tab_badge", "children"),
    Output("close_tab_badge", "children"),
    Input("main_tabs", "value"),
)
def show_pipeline_number(active_tab):
    """Display how many pipelines available in opened and closed tabs"""
    open_num = request_gitlab.total_issues(state="opened")
    close_num = request_gitlab.total_issues(state="closed")
    return open_num, close_num


@callback(
    Output("opened_content", "children"),
    Output("closed_content", "children"),
    Output("next_button", "disabled"),
    Output("opened_loading", "parent_style"),
    Output("closed_loading", "parent_style"),
    Input("main_tabs", "value"),
    Input("store_page_num", "data"),
    Input("issue_filter", "value"),
)
def switch_tabs(active_tab, page_num, search_term):
    """Allow user to switch between welcome, opened, and closed tabs"""
    load_style = {"position": "center"}
    ISSUE_PER_PAGE = 10

    if active_tab in ["welcome", "workflow"]:
        return no_update, no_update, no_update, no_update, no_update

    if active_tab in ["opened", "closed"]:
        issue_meta = request_gitlab.get_issues_meta(state=active_tab,
                                                    page=page_num,
                                                    per_page=ISSUE_PER_PAGE,
                                                    search_term=search_term)

        is_disabled = len(issue_meta) != ISSUE_PER_PAGE
        if len(issue_meta) == 0:
            return (
                html.Div([
                    line_breaks(1),
                    header_comp(f"⦿ No {active_tab} requests!", indent=40),
                    line_breaks(5)
                ]),
                no_update,
                True,
                no_update,
                no_update
            )
        else:
            if active_tab == "opened":
                return get_pipeline_accords(
                    issue_meta), no_update, is_disabled, load_style, no_update
            elif active_tab == "closed":
                return no_update, get_pipeline_accords(
                    issue_meta), is_disabled, no_update, load_style


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
        # Get the total jobs, finished jobs, and result path from issue notes
        total_jobs, finished_jobs, result_path = parse_job_stats(notes)
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
    Input("main_tabs", "value"),
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
