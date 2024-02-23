from dash import callback_context as cc
import dash_bootstrap_components as dbc
from dash import callback, Input, Output, State, dcc, html

from .utils import update_simple_template
from .hsm_grid import create_hsm_grid, create_show_grid
from ..components import (header_comp, paragraph_comp, checklist_comp,
                          group_accordion, popup_comp, button_comp, line_breaks,
                          radio_item_comp)

from ..global_variables import request_gitlab, dvc_gitlab


def get_user_list():
    """Fetch the members list from request repo"""
    return request_gitlab.get_project_members()


def get_simple_template():
    """Fetch the simple request template from request repo"""
    return request_gitlab.read_file(
        path=".gitlab/issue_templates/pipeline_request_simple.md")


def simple_request(refresh_path):
    """Creates simple request page"""
    model_meta_dict = dvc_gitlab.fetch_model_meta()
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
                    dbc.AccordionItem(
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
                                            placeholder="Enter the name of "
                                                        "the pipeline...",
                                            style={"width": "72%"},
                                            class_name="custom-placeholder",
                                        )
                                    ],
                                    style={"width": "90%"},
                                ),
                                className="row justify-content-center",
                            )
                        ]
                    ),
                    dbc.AccordionItem(
                        title="Segmentation",
                        children=[
                            # MLUNet segmentor section
                            checklist_comp(
                                comp_id="simple_unet_id",
                                options={"mlunet": False},
                            ),
                            html.Ul(
                                id="simple_unet_options",
                                key="model_file",
                                children=[
                                    dbc.Row([
                                        dbc.Col([
                                            html.P("⦿ Select device:",
                                                   style={
                                                       "margin": "0",
                                                       "padding-bottom": "5px"
                                                   }
                                                   ),
                                            radio_item_comp(
                                                comp_id="simple_unet_device",
                                                option_list=model_meta_dict[0]
                                            ),
                                        ], width=2),
                                        dbc.Col([
                                            html.P("⦿ Select type:",
                                                   style={"margin": "0",
                                                          "padding-bottom": "5px"}
                                                   ),
                                            radio_item_comp(
                                                comp_id="simple_unet_type",
                                                option_list=model_meta_dict[0]
                                            )
                                        ])
                                    ])
                                ]
                            ),
                            checklist_comp(
                                comp_id="simp_segm_id",
                                options={
                                    "legacy": False,
                                    "watershed": False,
                                    "std": False},
                            )
                        ]
                    ),
                    dbc.AccordionItem(
                        title="Prediction",
                        children=[
                            paragraph_comp("Classification Model"),
                            checklist_comp(
                                comp_id="simp_classifier_id",
                                options={"bloody-bunny": False},
                                defaults=["bloody-bunny"]
                            )
                        ]
                    ),
                    dbc.AccordionItem(
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
                    ),
                    dbc.AccordionItem(
                        title="Data to Process",
                        item_id="hsm_accord",
                        children=[
                            create_hsm_grid(),
                            line_breaks(times=2),
                        ]
                    )
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
            dcc.Store(id="store_simple_unet_params", storage_type="local"),
        ]
    )


@callback(
    Output("store_simple_unet_params", "data"),
    Input("simple_unet_id", "value"),
    Input("simple_unet_device", "value"),
    Input("simple_unet_type", "value"),
    Input("simple_unet_options", "key")
)
def cache_unet_options(unet_click, device, ftype, mpath_key):
    meta_dict = dvc_gitlab.fetch_model_meta()[2]
    if device and ftype and unet_click:
        model_path = meta_dict[device][ftype]
        unet_path = {mpath_key: model_path}
        return {unet_click[0]: unet_path}
    else:
        return None


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
    Input("store_simple_unet_params", "data"),
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
    Input("store_simple_unet_params", "data")
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
    button_trigger = [p["prop_id"] for p in cc.triggered][0]
    if "create_simple_pipeline_button" in button_trigger:
        request_gitlab.run_pipeline(cached_simp_temp)
        return not popup
    if close_popup:
        return not popup
    return popup
