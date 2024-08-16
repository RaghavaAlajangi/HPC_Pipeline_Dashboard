import os

from dash import callback, dcc, html, Input, MATCH, no_update, Output, State
from dash import callback_context as ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from .common import (chat_box, create_badge, create_list_group, header_comp,
                     line_breaks, paragraph_comp, progressbar_comp, web_link,
                     hover_card)
from ..gitlab import get_gitlab_instances

# Get the BASENAME_PREFIX from environment variables if not default
BASENAME_PREFIX = os.environ.get("BASENAME_PREFIX", "/local-dashboard/")

# dcevent documentation URL
DCEVENT_DOCS = "https://blood_data_analysis.pages.gwdg.de/dcevent/"


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
                            text="If you want to segment or/and classify "
                                 "your data, use the Simple Request on "
                                 "the left.",
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


def get_tab_content(tab_id, load_id, prev_button_id, next_button_id):
    """Placeholder for opened and closed tab content. This function has
    search bar to find specific pipeline and `Previous` and `Next` buttons
    for the pagination.
    """
    return dbc.CardBody([
        dbc.ListGroup([
            # Pipeline search bar
            dbc.ListGroupItem(
                children=dmc.TextInput(
                    id="pipeline_filter",
                    style={"width": "100%", "color": "white"},
                    placeholder="Filter pipelines with username or "
                                "title or keywords...",
                    icon=DashIconify(icon="tabler:search", width=22),
                    size="sm"
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
                dmc.Button(
                    "Prev",
                    id=prev_button_id,
                    disabled=True,
                    leftIcon=DashIconify(
                        icon="streamline:button-previous-solid"),
                ),
            ),
            dbc.ListGroupItem(
                dmc.Button(
                    "Next",
                    id=next_button_id,
                    disabled=True,
                    rightIcon=DashIconify(icon="streamline:button-next-solid"),
                ),
            ),
            # Cache page number on the browser
            dcc.Store(id="cache_page_num", storage_type="memory",
                      data={"opened": 1, "closed": 1})
        ],
            horizontal=True,
            style={"justify-content": "center"}
        )
    ])


def create_pipeline_accordion_item(pipeline):
    """Creates an accordion item for a given pipeline"""

    state_icon_dict = {
        "run": {"color": "#10e84a", "icon": "line-md:loading-twotone-loop",
                "status": "Processing"},
        "pause": {"color": "orange",
                  "icon": "material-symbols:motion-photos-paused",
                  "status": "Paused"},

        "cancel": {"color": "red", "icon": "flat-color-icons:cancel",
                   "status": "Canceled"},
        "finish": {"color": "yellow",
                   "icon": "ion:checkmark-done-circle-outline",
                   "status": "Finished"},
        "error": {"color": "red",
                  "icon": "material-symbols:error-outline",
                  "status": "Error"}
    }

    icon_dict = state_icon_dict[pipeline["pipe_state"]]

    pipeline_color = "success" if pipeline["type"] == "simple" else "danger"

    return dmc.AccordionItem(
        children=[
            dmc.AccordionControl(
                children=[
                    dmc.Grid(
                        children=[
                            dmc.Col([
                                # Pipeline title
                                html.P(
                                    children=f"{pipeline['title']}",
                                    style={"color": "white",
                                           "display": "inline"}
                                ),
                                html.Br(),
                                # Badge for pipeline number (issue iid)
                                create_badge(f"#{pipeline['iid']}", "skyblue"),
                                # Badge for type of pipeline (simple/advanced)
                                create_badge(pipeline["type"].capitalize(),
                                             pipeline_color),
                                # Badge for username
                                create_badge(pipeline["user"], "success"),
                                # Badge for date of submission
                                create_badge(pipeline["date"], "info"),
                            ],
                                span=8
                            ),
                            dmc.Col(
                                dmc.Text([
                                    DashIconify(
                                        color=icon_dict["color"],
                                        icon=icon_dict["icon"],
                                        height=40,
                                        width=40
                                    ),
                                    f"  {icon_dict['status']}"
                                ], c="white", fw=700),

                                span=1
                            )
                        ],
                        justify="space-between",
                        align="center",
                        gutter="xs"
                    )
                ],
                # Pipeline icon
                icon=DashIconify(
                    color="red", icon="carbon:subflow", height=30, width=30
                )
            ),
            dmc.AccordionPanel(
                children=[
                    dbc.Modal([
                        dbc.ModalHeader(
                            dbc.ModalTitle("Pipeline Status"),
                            close_button=False
                        ),
                        dbc.ModalBody(id={"type": "pipeline_popup_msg",
                                          "index": pipeline["iid"]}),
                        dbc.ModalFooter(
                            html.A(
                                dmc.Button("Close",
                                           id={"type": "pipeline_popup_click",
                                               "index": pipeline["iid"]},
                                           variant="red"),
                                href=BASENAME_PREFIX
                            )
                        ),
                    ],
                        id={"type": "pipeline_popup",
                            "index": pipeline["iid"]},
                        centered=True,
                        is_open=False,
                        keyboard=True,
                        backdrop="static",
                        style={"color": "white"}
                    ),

                    # Store component to cache pipeline notes. It allows us
                    # to use the same notes across multiple callbacks without
                    # computing twice.
                    dcc.Store({"type": "cache_pipeline_notes",
                               "index": pipeline["iid"]}, data={}),
                    html.Strong("Pipeline Details:"),
                    create_list_group(
                        children=[
                            dmc.Text(f"Created by: {pipeline['author']}"),
                            dmc.Text(f"Username: {pipeline['user']}"),
                            web_link(
                                label=f"Go to GitLab issue - "
                                      f"#{pipeline['iid']}",
                                url=pipeline["web_url"]
                            ),
                            web_link(
                                label="Download RTDC csv (Not Implemented)",
                                url="https://google.com"
                            ),
                            dmc.Group([
                                hover_card(
                                    target=dmc.Button(
                                        "Run / Pause Pipeline",
                                        id={"type": "run_pause_click",
                                            "index": pipeline["iid"]},
                                        disabled=True,
                                        rightIcon=DashIconify(
                                            icon="lets-icons:stop-and-play"
                                                 "-fill",
                                            height=30, width=30),
                                        variant="gradient"
                                    ),
                                    notes="You can set the priority "
                                          "(Run/Pause) of the pipeline. Run "
                                          "the pipeline that has high "
                                          "priority and pause the rest until "
                                          "it is done."
                                ),

                                dmc.Button(
                                    "Stop Pipeline",
                                    id={"type": "stop_pipe_click",
                                        "index": pipeline["iid"]},
                                    disabled=True,
                                    color="red",
                                    rightIcon=DashIconify(
                                        icon="mdi:stop-alert",
                                        height=25, width=25)
                                )
                            ]),
                        ]),
                    line_breaks(1),
                    html.Strong("Pipeline Progress:"),
                    dbc.ListGroup(
                        children=[
                            dbc.ListGroupItem(
                                children=html.Div(
                                    id={"type": "pipeline_progress_num",
                                        "index": pipeline["iid"]},
                                    style={"display": "inline"}
                                ),
                                style={"width": "15%", "color": "#10e84a"}
                            ),
                            dbc.ListGroupItem(
                                children=progressbar_comp(
                                    comp_id={"type": "pipeline_progress_bar",
                                             "index": pipeline["iid"]},
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
                                        "index": pipeline["iid"]},
                                    lang="python",
                                    style={"color": "#10e84a", "fontSize": 15}
                                ),
                                style={"color": "#10e84a"}
                            ),
                            dbc.ListGroupItem(
                                children=dcc.Clipboard(
                                    target_id={"type": "s3_proxy_path",
                                               "index": pipeline["iid"]},
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
                                "index": pipeline["iid"]}
                        ),
                        loaderProps={"variant": "dots", "color": "#10e84a",
                                     "size": "xl"},
                        overlayColor="#303030"
                    )
                ]
            )
        ],
        style={"width": "100%"},
        value=str(pipeline["iid"])
    )


def create_pipelines_accordion(pipelines_meta):
    """Creates an accordion of GitLab issues"""
    children_items = [create_pipeline_accordion_item(pipeline) for
                      pipeline in pipelines_meta]
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
                    children=get_tab_content(
                        tab_id="opened_content",
                        load_id="opened_loading",
                        prev_button_id="opened_prev_button",
                        next_button_id="opened_next_button"
                    ),
                    value="opened"
                ),
                dmc.TabsPanel(
                    children=get_tab_content(
                        tab_id="closed_content",
                        load_id="closed_loading",
                        prev_button_id="closed_prev_button",
                        next_button_id="closed_next_button"
                    ),
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
    Output("cache_page_num", "data"),
    Output("opened_prev_button", "disabled"),
    Output("closed_prev_button", "disabled"),
    Input("opened_prev_button", "n_clicks"),
    Input("opened_next_button", "n_clicks"),
    Input("closed_prev_button", "n_clicks"),
    Input("closed_next_button", "n_clicks"),
    Input("main_tabs", "value"),
    State("cache_page_num", "data")
)
def change_page(opclick, onclick, cpclick, cnclick, active_tab, cache_page):
    """Cache page number when user clicks on `Previous` and `Next` buttons"""
    triggered_id = ctx.triggered_id

    if triggered_id == f"{active_tab}_next_button":
        cache_page[active_tab] += 1
    if triggered_id == f"{active_tab}_prev_button":
        cache_page[active_tab] -= 1
    opened_prev_disabled = cache_page["opened"] < 2
    closed_prev_disabled = cache_page["closed"] < 2
    return cache_page, opened_prev_disabled, closed_prev_disabled


@callback(
    Output("open_tab_badge", "children"),
    Output("close_tab_badge", "children"),
    Input("url", "pathname")
)
def show_pipeline_number(pathname):
    """Display how many pipelines available in opened and closed tabs"""
    request_gitlab, _ = get_gitlab_instances()

    if pathname == BASENAME_PREFIX:
        open_num = request_gitlab.total_issues(state="opened")
        close_num = request_gitlab.total_issues(state="closed")
        return open_num, close_num
    return no_update


@callback(
    Output("opened_content", "children"),
    Output("closed_content", "children"),
    Output("opened_next_button", "disabled"),
    Output("closed_next_button", "disabled"),
    Output("opened_loading", "parent_style"),
    Output("closed_loading", "parent_style"),
    Input("main_tabs", "value"),
    Input("cache_page_num", "data"),
    Input("pipeline_filter", "value")
)
def switch_tabs(active_tab, cache_page, search_term):
    """Allow user to switch between welcome, opened, and closed tabs"""
    load_style = {"position": "center"}
    issues_per_page = 10
    request_gitlab, _ = get_gitlab_instances()

    if active_tab in ["welcome", "workflow"]:
        raise PreventUpdate

    # if active_tab in ["opened", "closed"]:
    pipeline_meta = request_gitlab.get_issues_meta(
        state=active_tab,
        page=cache_page[active_tab],
        per_page=issues_per_page,
        search_term=search_term
    )

    is_disabled = len(pipeline_meta) != issues_per_page
    if len(pipeline_meta) == 0:
        return [
            html.Div([
                line_breaks(1),
                header_comp("⦿ No active requests found!", indent=40),
                line_breaks(5)
            ]),
            no_update,
            True,
            no_update,
            no_update,
            no_update
        ]
    # else:
    if active_tab == "opened":
        return [
            create_pipelines_accordion(pipeline_meta),
            no_update,
            is_disabled,
            no_update,
            load_style,
            no_update
        ]
    if active_tab == "closed":
        return [
            no_update,
            create_pipelines_accordion(pipeline_meta),
            no_update,
            is_disabled,
            no_update,
            load_style
        ]

    # Default return statement in case none of the conditions are met
    raise PreventUpdate


@callback(
    Output({"type": "pipeline_comments", "index": MATCH}, "children"),
    Output({"type": "s3_proxy_path", "index": MATCH}, "children"),
    Output({"type": "pipeline_progress_num", "index": MATCH}, "children"),
    Output({"type": "pipeline_progress_bar", "index": MATCH}, "value"),
    Output({"type": "pipeline_progress_bar", "index": MATCH}, "label"),
    Output({"type": "cache_pipeline_notes", "index": MATCH}, "data"),
    Input("pipeline_accordion", "value"),
    prevent_initial_call=True
)
def show_pipeline_data(pipeline_num):
    """Display pipeline data when the user clicks on pipeline accordion"""

    request_gitlab, _ = get_gitlab_instances()

    progress_comments = [
        "STATE: setup",
        "STATE: queued",
        "STATE: done"
    ]

    # Check if there is an active_item selected
    if not pipeline_num:
        return [no_update] * 6

    # Get the processed pipeline notes from GitLab
    pipeline_notes = request_gitlab.get_processed_issue_notes(pipeline_num)

    # Create dash chat box from the notes
    chat = chat_box(pipeline_notes)

    finished_jobs = pipeline_notes["finished_jobs"]
    total_jobs = pipeline_notes["total_jobs"]
    result_path = pipeline_notes["results_path"]

    # Show only comments if total jobs equal to zero
    if total_jobs == 0:
        return chat, result_path, "Jobs: [0 / 0]", None, None, pipeline_notes

    # Calculate the progress percentage
    progress = (finished_jobs / total_jobs) * 85

    # Add 5% progress for specific state comments
    for state_comment in progress_comments:
        if state_comment in pipeline_notes["comments"]:
            progress += 5

    result = [
        chat,
        result_path,
        f"Jobs: [{finished_jobs} / {total_jobs}]",
        progress,
        f"{progress:.0f} %",
        pipeline_notes
    ]

    return result


@callback(
    Output({"type": "pipeline_popup", "index": MATCH}, "is_open"),
    Output({"type": "pipeline_popup_msg", "index": MATCH}, "children"),
    Output({"type": "run_pause_click", "index": MATCH}, "disabled"),
    Output({"type": "stop_pipe_click", "index": MATCH}, "disabled"),

    Input("main_tabs", "value"),
    Input("pipeline_accordion", "value"),
    Input({"type": "run_pause_click", "index": MATCH}, "n_clicks"),
    Input({"type": "stop_pipe_click", "index": MATCH}, "n_clicks"),
    Input({"type": "pipeline_comments", "index": MATCH}, "children"),
    prevent_initial_call=True
)
def manage_pipeline_status(active_tab, pipeline_num, run_pause_click,
                           stop_pipe_click, pipeline_comments):
    """Toggle the pipeline control buttons and display popup messages based
    on user interaction.

    Notes
    -----
    The function triggers based on the provided inputs and checks the state
    of the pipeline to determine the appropriate actions. If the run/pause
    button is clicked, the pipeline state toggles between "run" and "pause".
    If the stop button is clicked, the pipeline is stopped, and both buttons
    are disabled. The function uses the `get_gitlab_instances` method to
    interact with GitLab and retrieve the current pipeline status.
    """

    # Check for pipeline_num, opened tab, and pipeline content
    if not pipeline_num or active_tab != "opened" or \
            not isinstance(pipeline_comments, dict):
        return no_update, no_update, no_update, no_update

    popup_open = False
    popup_message = None
    run_pause_disabled = False
    stop_disabled = False

    triggered_id = ctx.triggered[0]["prop_id"]

    request_gitlab, _ = get_gitlab_instances()

    issue_notes = request_gitlab.get_processed_issue_notes(pipeline_num)
    pipe_state = issue_notes["pipe_state"]

    if "run_pause_click" in triggered_id:
        popup_open = True
        if pipe_state == "pause":
            request_gitlab.change_pipeline_status(pipeline_num, "run")
            popup_message = "The issue has been resumed."
        elif pipe_state == "run":
            request_gitlab.change_pipeline_status(pipeline_num, "pause")
            popup_message = "The issue has been paused."

    elif "stop_pipe_click" in triggered_id:
        request_gitlab.change_pipeline_status(pipeline_num, "cancel")
        popup_message = "The issue has been stopped."
        run_pause_disabled = True
        stop_disabled = True
        popup_open = True
    elif pipe_state == "cancel":
        # In "cancel" state, both buttons are disabled
        run_pause_disabled = True
        stop_disabled = True
    elif pipe_state == "error":
        # In "error" state, run_pause_disabled button is disabled
        run_pause_disabled = True
        stop_disabled = False

    return popup_open, popup_message, run_pause_disabled, stop_disabled
