from dash import ALL, callback, dcc, html, Input, no_update, Output, State
from dash import callback_context as ctx
import dash_bootstrap_components as dbc
import yaml

from .common import (button_comp, input_with_label, group_accordion,
                     header_comp, line_breaks, popup_comp)
from .gd2_grid import create_gd2_grid, create_show_grid
from ..gitlab import get_gitlab_instances


def get_user_list():
    """Fetch the members list from request repo"""
    request_gitlab = get_gitlab_instances()
    return request_gitlab.get_project_members()


def get_simple_template():
    """Fetch the simple request template from request repo"""
    request_gitlab = get_gitlab_instances()
    return request_gitlab.get_request_template(temp_type="simple")


def title_section():
    """Creates a simple title section for the pipeline."""
    return dbc.AccordionItem(
        title="Title (required)",
        children=[
            html.Div(
                dbc.InputGroup(
                    children=[
                        dbc.Select(
                            placeholder="Select Username",
                            id="title_dropdown",
                            options=[
                                {"label": member.name,
                                 "value": member.username} for
                                member in get_user_list()
                            ],
                            style={"width": "18%"},
                        ),
                        dbc.Input(
                            type="text",
                            id="title_text",
                            placeholder="Enter title of the pipeline...",
                            style={"width": "72%"},
                            class_name="custom-placeholder",
                        )
                    ],
                    style={"width": "90%"},
                ),
                className="row justify-content-center",
            )
        ]
    )


def pipeline_parameters_section():
    """Creates the prediction section of the simple pipeline."""
    return dbc.AccordionItem(
        title="dprocess params",
        children=[
            input_with_label(
                comp_id={"type": "dprocess_param", "index": 1},
                label="mode_mp",
                label_key="mode_mp",
                hover_notes="Use either 'multiprocessing' or 'sequential' "
                            "operation when you run the processing job.",
                input_type="text",
                input_width=11,
                select=True,
                select_options=[{"label": "multiprocessing", "value": "mp"},
                                {"label": "sequential", "value": "seq"}],
                select_value="mp"),

            input_with_label(
                comp_id={"type": "dprocess_param", "index": 2},
                label="mp_batch_size",
                label_key="mp_batch_size",
                hover_notes="Determines the batch size for 'multiprocessing'. "
                            "Bigger batch size improves the processing speed. "
                            "Make sure, you have enough RAM to tackle the "
                            "batch size.",
                input_type="number",
                input_min=0, input_max=1000000, input_step=100,
                input_value=10000),

            input_with_label(
                comp_id={"type": "dprocess_param", "index": 3},
                label="efp_thresh",
                label_key="efp_thresh",
                hover_notes="Brightness threshold for event detection (after "
                            "background subtraction). Available options: "
                            "'Auto' or an integer (lower means less strict). "
                            "Any events with brightness above this value will "
                            "be considered an event.",
                input_type="text",
                input_placeholder="'auto' or an 'integer'",
                input_value="auto"),

            input_with_label(
                comp_id={"type": "dprocess_param", "index": 4},
                label="event_images_to_detect",
                label_key="event_images_to_detect",
                hover_notes="'all' or an 'integer'. You may end up with more "
                            "than this number, as images may have multiple "
                            "events.",
                input_type="text",
                input_placeholder="'all' or an 'integer'",
                input_value="all"),

            input_with_label(
                comp_id={"type": "dprocess_param", "index": 5},
                label="phase_thresh",
                label_key="phase_thresh",
                hover_notes="MATLAB_PHA_THRESH_VAL=0.5 from Kyoo's MATLAB "
                            "script. Lower to include more info.",
                input_type="number",
                input_min=0, input_max=1, input_step=0.1,
                input_value=0.5),

            input_with_label(
                comp_id={"type": "dprocess_param", "index": 6},
                label="refocus",
                label_key="refocus",
                hover_notes="Refocusing each event during the analysis. This "
                            "will improve the consistency of the scalar "
                            "features e.g. deform",
                select=True,
                select_options=[{"label": "True", "value": "True"},
                                {"label": "False", "value": "False"}],
                select_value="True")
        ]
    )


def data_to_process_section():
    """Creates the data to process section of the simple pipeline."""
    return dbc.AccordionItem(
        title="Data to Process",
        item_id="guck_accord",
        children=[
            create_gd2_grid(),
            line_breaks(times=2),
        ]
    )


def simple_page_layout(refresh_path):
    """Creates simple request page"""
    return dbc.Toast(
        id="simple_request_toast",
        header="Simple Pipeline Request",
        header_style={"background-color": "#017b70",
                      "font-size": "25px",
                      "color": "white"},
        is_open=True,
        className="my-toast",
        children=[
            popup_comp(comp_id="pipeline_popup", refresh_path=refresh_path,
                       text="Pipeline request has been submitted!"),
            line_breaks(times=1),
            header_comp("⦿ Pipeline for analysing Auto-Rapid data.",
                        indent=40),
            line_breaks(times=2),
            group_accordion(
                children=[
                    title_section(),
                    pipeline_parameters_section(),
                    data_to_process_section()
                ],
                middle=True,
                open_first=True,
                comp_id="pipeline_accord"
            ),
            line_breaks(times=3),
            create_show_grid(comp_id="show_grid"),
            line_breaks(times=3),
            button_comp(label="Create pipeline",
                        disabled=True,
                        comp_id="create_pipeline_button"),
            line_breaks(times=2),
            dbc.Alert("Note: Username, pipeline title, and data paths are "
                      "mandatory fields to activate 'Create Pipeline' button.",
                      color="warning",
                      style={
                          "color": "black",
                          "width": "fit-content",
                          "margin": "auto",
                      }),
            line_breaks(times=5),
            dcc.Store(id="cache_pipeline_template", storage_type="local"),
        ]
    )


@callback(
    Output("cache_pipeline_template", "data"),
    Input("title_dropdown", "value"),
    Input("title_text", "value"),
    Input({"type": "dprocess_param", "index": ALL}, "key"),
    Input({"type": "dprocess_param", "index": ALL}, "value"),
    Input("show_grid", "selectedRows")
)
def collect_pipeline_params(author_name, simple_title, dprocess_key,
                            dprocess_val, selected_files):
    """Collect all the user selected parameters. Then, it updates the simple
    issue template. Updated template will be cached"""
    dprocess_params = {k: v for k, v in zip(dprocess_key, dprocess_val)}

    if author_name and simple_title and selected_files:
        hdf5_files = [s["filepath"] for s in selected_files]
        # Create yaml dict
        yaml_dict = {"params": dprocess_params, "data": hdf5_files}
        # Convert yaml dict into string
        yaml_str = yaml.dump(yaml_dict, sort_keys=False)

        # Put the yaml string in a python codeblock
        codeblock_str = f"```python\n{yaml_str}```"
        # Create a template dict with title
        pipeline_template = {"title": simple_title}
        # Get the pipeline template
        pipe_template = get_simple_template()
        # Split the template and get the desired part
        template_wo_codeblock = pipe_template.split("```python")[0]
        username_str = f"\n - [x] username={author_name}"
        # Add yaml string to template part
        description = template_wo_codeblock + codeblock_str + username_str
        # Update pipeline description
        pipeline_template["description"] = description
        return pipeline_template
    return no_update


@callback(
    Output("create_pipeline_button", "disabled"),
    Input("title_dropdown", "value"),
    Input("title_text", "value"),
    Input("show_grid", "selectedRows")
)
def toggle_create_pipeline_button(author_name, title, selected_files):
    """Activates create pipeline button only when author name, title and
    data files are entered"""
    if author_name and title and title.strip() and selected_files:
        return False
    return True


@callback(
    Output("pipeline_popup", "is_open"),
    Input("create_pipeline_button", "n_clicks"),
    Input("cache_pipeline_template", "data"),
    Input("pipeline_popup_close", "n_clicks"),
    State("pipeline_popup", "is_open")
)
def request_submission_popup(bclick, cached_template, close_popup, popup):
    """Show a popup when user clicks on create pipeline button. Then, user
    is asked to close the popup. When user closes page will be refreshed"""

    request_gitlab = get_gitlab_instances()

    button_trigger = [p["prop_id"] for p in ctx.triggered][0]
    if "create_pipeline_button" in button_trigger:
        request_gitlab.run_pipeline(cached_template)
        return not popup
    if close_popup:
        return not popup
    return popup
