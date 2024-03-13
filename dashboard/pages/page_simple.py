from dash import callback, dcc, html, Input, no_update, Output, State
from dash import callback_context as ctx
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from .hsm_grid import create_hsm_grid, create_show_grid
from .utils import update_simple_template
from .common import (button_comp, checklist_comp, group_accordion, header_comp,
                     line_breaks, paragraph_comp, popup_comp)

from ..gitlab import request_gitlab, dvc_gitlab


def get_user_list():
    """Fetch the members list from request repo"""
    return request_gitlab.get_project_members()


def get_simple_template():
    """Fetch the simple request template from request repo"""
    return request_gitlab.get_request_template(temp_type="simple")


def simple_title_section():
    return dbc.AccordionItem(
        title="Title (required)",
        children=[
            html.Div(
                dbc.InputGroup(
                    children=[
                        dbc.Select(
                            placeholder="Select Username",
                            id="simple_title_drop",
                            options=[
                                {"label": member.name,
                                 "value": member.username} for
                                member in get_user_list()
                            ],
                            style={"width": "18%"},
                        ),
                        dbc.Input(
                            type="text",
                            id="simple_title_text",
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


def simple_segmentation_section():
    return dbc.AccordionItem(
        title="Segmentation",
        children=[
            # MLUNet segmentor section
            checklist_comp(comp_id="simple_unet_id",
                           options={"mlunet": False}),
            html.Ul(
                id="simple_unet_options",
                key="model_file",
                children=[
                    dmc.Group([
                        dmc.Stack(
                            children=[
                                html.P(
                                    "⦿ Select device:",
                                    style={"margin": "0",
                                           "padding-bottom": "5px"}
                                ),
                                # Placeholder to display device options
                                # Ex: Accelerator or Naiad
                                dmc.ChipGroup(id="simple_unet_device"),
                            ],
                            spacing=5
                        ),
                        dmc.Stack(
                            children=[
                                html.P(
                                    "⦿ Select type:",
                                    style={"margin": "0",
                                           "padding-bottom": "5px"}
                                ),
                                # Placeholder to display cell types
                                # Ex: Blood or Beads
                                dmc.ChipGroup(id="simple_unet_cell_type"),
                            ],
                            spacing=5
                        )
                    ],
                        spacing=50
                    )
                ]
            ),
            checklist_comp(
                comp_id="simp_segm_id",
                options={
                    "legacy": False,
                    "watershed": False,
                    "std": False}
            )
        ]
    )


def simple_prediction_section():
    return dbc.AccordionItem(
        title="Prediction",
        children=[
            paragraph_comp("Classification Model"),
            checklist_comp(
                comp_id="simp_classifier_id",
                options={"bloody-bunny": False},
                defaults=["bloody-bunny"]
            )
        ]
    )


def simple_post_analysis_section():
    return dbc.AccordionItem(
        title="Post Analysis (Not Implemented)",
        children=[
            checklist_comp(
                comp_id="simp_postana_id",
                options={
                    "Benchmarking": True,
                    "Scatter Plots": True
                }
            )
        ]
    )


def simple_data_to_process_section():
    return dbc.AccordionItem(
        title="Data to Process",
        item_id="hsm_accord",
        children=[
            create_hsm_grid(),
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
            popup_comp(comp_id="simple_popup", refresh_path=refresh_path,
                       text="Pipeline request has been submitted!"),
            line_breaks(times=1),
            header_comp("⦿ Pipeline for segmentation and/or classification "
                        "(prediction) and analysis of data.", indent=40),
            line_breaks(times=1),
            header_comp("⦿ Choosing multiple Segmentation or Prediction "
                        "algorithms will create a matrix of jobs (multiple "
                        "jobs).", indent=40),
            line_breaks(times=2),
            group_accordion(
                children=[
                    simple_title_section(),
                    simple_segmentation_section(),
                    simple_prediction_section(),
                    simple_post_analysis_section(),
                    simple_data_to_process_section()
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
                        comp_id="create_simple_pipeline_button"),
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
            dcc.Store(id="store_simple_template", storage_type="local"),
            dcc.Store(id="store_unet_options", storage_type="local"),
            dcc.Store(id="store_simple_unet_model_path", storage_type="local"),
        ]
    )


@callback(
    Output("simple_unet_device", "children"),
    Output("simple_unet_cell_type", "children"),
    Output("store_simple_unet_model_path", "data"),
    Input("simple_unet_id", "value"),
    Input("simple_unet_device", "value"),
    Input("simple_unet_cell_type", "value"),
    Input("simple_unet_options", "key"),
)
def show_and_cache_unet_model_meta(unet_click, device, cell_type, mpath_key):
    """This circular callback fetches unet model metadata from the DVC repo
    and shows it as dmc.Chip options, enable the user to select the
    appropriate same dmc.Chip options."""

    devices, cell_types, model_dict = dvc_gitlab.get_model_metadata()

    device_chips = [
        dmc.Chip(opt.capitalize(), color="green", value=opt) for opt in devices
    ]
    type_chips = [
        dmc.Chip(opt.capitalize(), color="green", value=opt) for opt in
        cell_types
    ]
    if device and cell_type and unet_click:
        model_path = model_dict[device][cell_type]
        unet_path = {mpath_key: model_path}
        return device_chips, type_chips, {unet_click[0]: unet_path}
    return device_chips, type_chips, None


@callback(
    Output("simple_unet_options", "style"),
    Input("simple_unet_id", "value"),
)
def toggle_unet_options(unet_click):
    """Toggle mlunet segmentation options with unet switch"""
    if unet_click:
        return {"display": "block"}
    else:
        return {"display": "none"}


@callback(
    Output("store_simple_template", "data"),
    Input("simple_title_drop", "value"),
    Input("simple_title_text", "value"),
    Input("store_simple_unet_model_path", "data"),
    Input("simp_segm_id", "value"),
    Input("simp_classifier_id", "value"),
    Input("simp_postana_id", "value"),
    Input("show_grid", "selectedRows")
)
def collect_simple_pipeline_params(author_name, simple_title, simple_unet,
                                   simple_segment, simple_classifier,
                                   simple_postana, selected_files):
    """Collect all the user selected parameters. Then, it updates the simple
    issue template. Updated template will be cached"""
    params = simple_segment + simple_classifier + simple_postana

    # Update the template, only when author name, title, and data files
    # to process are entered
    if author_name and simple_title and selected_files and simple_unet:
        rtdc_files = [s["filepath"] for s in selected_files]
        # Create a template dict with title
        pipeline_template = {"title": simple_title}
        # Update the simple template from request repo
        description = update_simple_template(params, simple_unet["mlunet"],
                                             author_name, rtdc_files,
                                             get_simple_template())
        pipeline_template["description"] = description
        return pipeline_template


@callback(
    Output("create_simple_pipeline_button", "disabled"),
    Input("simple_title_drop", "value"),
    Input("simple_title_text", "value"),
    Input("show_grid", "selectedRows"),
    Input("simple_unet_id", "value"),
    Input("store_simple_unet_model_path", "data")
)
def toggle_simple_create_pipeline_button(author_name, title, selected_files,
                                         unet_click, unet_mpath):
    """Activates create pipeline button only when author name, title, and
    data files are entered"""
    if author_name and title and title.strip() and selected_files:
        if unet_click and unet_mpath:
            return False
        elif unet_click and not unet_click:
            return True
        elif not unet_click:
            return False
        else:
            return True
    else:
        return True


@callback(
    Output("simple_popup", "is_open"),
    Input("create_simple_pipeline_button", "n_clicks"),
    Input("store_simple_template", "data"),
    Input("simple_popup_close", "n_clicks"),
    State("simple_popup", "is_open")
)
def simple_request_submission_popup(_, cached_simp_temp, close_popup, popup):
    """Show a popup when user clicks on create pipeline button. Then, user
    is asked to close the popup. When user closes page will be refreshed"""
    button_trigger = [p["prop_id"] for p in ctx.triggered][0]
    if "create_simple_pipeline_button" in button_trigger:
        request_gitlab.run_pipeline(cached_simp_temp)
        return not popup
    if close_popup:
        return not popup
    return popup
