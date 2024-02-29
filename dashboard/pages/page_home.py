import os
import re

from dash import callback, dcc, html, Input, MATCH, no_update, Output, State
from dash import callback_context as ctx
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from ..components import (button_comp, chat_box, create_list_group,
                          header_comp, line_breaks, paragraph_comp,
                          progressbar_comp, popup_comp, web_link)
from ..global_variables import request_gitlab, DCEVENT_DOCS

# Get the BASENAME_PREFIX from environment variables if not default
BASENAME_PREFIX = os.environ.get("BASENAME_PREFIX", "/local-dashboard/")

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


def create_issue_accordion_item(issue, mode):
    """Creates an accordion item for a given issue"""
    if mode == "opened":
        icon_flag = "fluent-mdl2:processing-run"
    else:
        icon_flag = "fluent-mdl2:processing-cancel"

    return dmc.AccordionItem(
        children=[
            dmc.AccordionControl(
                children=[
                    # Pipeline title
                    html.P(
                        children=f"(#{issue['iid']}) {issue['title']}",
                        style={"color": "white", "display": "inline"}
                    ),
                    html.Br(),
                    # Badge for type of pipeline (simple/advanced)
                    dbc.Badge(
                        children=issue["type"][0], color=issue["type"][1],
                        className="me-2", text_color="black"
                    ),
                    # Badge for user
                    dbc.Badge(
                        children=issue["user"], className="me-2",
                        color="success", text_color="black",
                    ),
                    # Badge for date
                    dbc.Badge(
                        children=issue["date"], color="info",
                        className="me-2", text_color="black"
                    ),
                ],
                # Pipeline icon
                icon=DashIconify(
                    color="white", icon=icon_flag, height=30, width=30
                )
            ),
            dmc.AccordionPanel(
                children=[
                    popup_comp(
                        comp_id={"type": "pipeline_stop_popup",
                                 "index": issue["iid"]},
                        refresh_path=BASENAME_PREFIX,
                        text="Pipeline request has been canceled!"
                    ),
                    html.Strong("Pipeline Details:"),
                    create_list_group(
                        children=[
                            dmc.Text(f"Created by: {issue['author']}"),
                            dmc.Text(f"Username: {issue['user']}"),
                            web_link(
                                label=f"Go to GitLab issue - #{issue['iid']}",
                                url=issue["web_url"]
                            ),
                            web_link(
                                label="Download RTDC csv (Not Implemented)",
                                url="https://google.com"
                            ),
                            button_comp(
                                comp_id={"type": "pipeline_stop_click",
                                         "index": issue["iid"]},
                                disabled=True, label="Stop Pipeline",
                                type="danger",
                            )
                        ]),
                    line_breaks(1),
                    html.Strong("Pipeline Progress:"),
                    dbc.ListGroup(
                        children=[
                            dbc.ListGroupItem(
                                children=html.Div(
                                    id={"type": "pipeline_progress_num",
                                        "index": issue["iid"]},
                                    style={"display": "inline"}
                                ),
                                style={"width": "15%", "color": "#10e84a"}
                            ),
                            dbc.ListGroupItem(
                                children=progressbar_comp(
                                    comp_id={"type": "pipeline_progress_bar",
                                             "index": issue["iid"]},
                                    width=95
                                ),
                                style={"width": "85%"}
                            )
                        ],
                        horizontal=True
                    ),
                    line_breaks(1),
                    html.Strong(
                        "Result Path: (path to find results on S3-proxy)"),
                    dbc.ListGroup(
                        children=[
                            dbc.ListGroupItem(
                                children=html.Code(
                                    id={"type": "s3_proxy_path",
                                        "index": issue["iid"]},
                                    lang="python",
                                    style={"color": "#10e84a", "fontSize": 15}
                                ),
                                style={"color": "#10e84a"}
                            ),
                            dbc.ListGroupItem(
                                children=dcc.Clipboard(
                                    target_id={"type": "s3_proxy_path",
                                               "index": issue["iid"]},
                                    title="Copy Path",
                                    style={
                                        "color": "#10e84a",
                                        "display": "inline-block",
                                        "fontSize": 20,
                                        "verticalAlign": "top",
                                    }
                                )
                            )
                        ],
                        horizontal=True
                    ),
                    line_breaks(1),
                    html.Strong("Comments:"),
                    dmc.LoadingOverlay(
                        children=dbc.ListGroup(
                            id={"type": "pipeline_comments",
                                "index": issue["iid"]}
                        ),
                        loaderProps={"variant": "dots", "color": "#10e84a",
                                     "size": "xl"},
                        overlayColor="#303030"
                    )
                ]
            )
        ],
        style={"width": "100%"},
        value=str(issue["iid"])
    )


def create_issues_accordion(issue_data, mode):
    """Creates an accordion of GitLab issues"""
    children_items = [create_issue_accordion_item(issue, mode) for issue in
                      issue_data]
    return dmc.Accordion(
        children=children_items,
        id="pipeline_accordion",
        className="my-accordion",
        disableChevronRotation=False,
        chevron=DashIconify(icon="quill:chevron-down",
                            color="#2fad40", height=50,
                            width=50),
        chevronSize=30,
        chevronPosition="right",
        variant="separated",
        transitionDuration=0,
        style={"max-height": "60rem", "width": "100%",
               "overflow-y": "scroll", "overflow-x": "hidden"},
        styles={
            "root": {"backgroundColor": "yellow", "borderRadius": 5},
            "item": {
                "backgroundColor": "#303030",
                "border": "1px solid transparent",
                "borderColor": "#017b50",
                "borderRadius": 10,
                "&[data-active]": {
                    "backgroundColor": "#262525",
                    "boxShadow": 5,
                    "borderColor": "#2fad40",
                    "borderRadius": 10,
                    "zIndex": 1,
                }
            }
        }
    )


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
                )
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
                return (create_issues_accordion(issue_meta, active_tab),
                        no_update, is_disabled, load_style, no_update)
            elif active_tab == "closed":
                return no_update, create_issues_accordion(
                    issue_meta, active_tab), is_disabled, no_update, load_style


@callback(
    Output({"type": "pipeline_comments", "index": MATCH}, "children"),
    Output({"type": "pipeline_progress_num", "index": MATCH}, "children"),
    Output({"type": "s3_proxy_path", "index": MATCH}, "children"),
    Output({"type": "pipeline_progress_bar", "index": MATCH}, "value"),
    Output({"type": "pipeline_progress_bar", "index": MATCH}, "label"),
    Input("pipeline_accordion", "value"),
    prevent_initial_call=True
)
def show_pipeline_data(pipeline_num):
    """Display pipeline data when the user clicks on pipeline accordion"""
    # Check if there is an active_item selected
    if not pipeline_num:
        return no_update, no_update, no_update, no_update, no_update

    # Get the pipeline notes from GitLab
    notes = request_gitlab.get_comments(pipeline_num)

    # Create dash chat box from the notes
    comment_cards = chat_box(notes)

    # Get pipeline stats from the notes
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

    result = [comment_cards,
              f"Jobs: [{finished_jobs} / {total_jobs}]",
              result_path,
              progress,
              f"{progress:.0f} %"]

    return result


@callback(
    Output({"type": "pipeline_stop_click", "index": MATCH}, "disabled"),
    Output({"type": "pipeline_stop_popup", "index": MATCH}, "is_open"),
    Input("main_tabs", "value"),
    Input({"type": "pipeline_comments", "index": MATCH}, "children"),
    Input({"type": "pipeline_stop_click", "index": MATCH}, "n_clicks"),
    Input({"type": "pipeline_stop_popup", "index": MATCH}, "n_clicks"),
    State({"type": "pipeline_comments", "index": MATCH}, "id"),
    State({"type": "pipeline_stop_popup", "index": MATCH}, "is_open"),
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
