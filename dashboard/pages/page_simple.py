from dash import callback, dcc, html, Input, Output, State
from dash import callback_context as ctx
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from .common import (button_comp, checklist_comp, divider_line_comp,
                     form_group_input, group_accordion, header_comp,
                     hover_card, line_breaks, paragraph_comp, popup_comp)
from .hsm_grid import create_hsm_grid, create_show_grid
from .utils import update_simple_template
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
            dmc.Group(
                children=[
                    # UNet checkbox (switch)
                    dbc.Checklist(
                        options=[
                            {"label": "U-Net Segmentation", "value": "mlunet"},
                        ],
                        id="simple_unet_id",
                        switch=True,
                        value=[],
                        labelCheckedClassName="text-success",
                        inputCheckedClassName="border-success bg-success",
                    ),
                    # UNet question mark icon and hover info
                    hover_card(
                        target=DashIconify(
                            icon="mage:message-question-mark-round-fill",
                            color="yellow", width=20),
                        notes="A deep learning based image segmentation "
                              "method.\n Warning: U-Net is trained on "
                              "specific cell types. When you select correct "
                              "option from below, appropriate model file "
                              "will be used for segmentation."
                    )
                ],
                spacing=5
            ),
            # UNet segmentation options
            html.Ul(
                id="simple_unet_options",
                children=[
                    dmc.RadioGroup(
                        id="simple_measure_options",
                        label="Select Measurement Type",
                        description="Please make sure that you select the "
                                    "right option. Otherwise, the pipeline "
                                    "might fail.",
                        orientation="vertical",
                        withAsterisk=True,
                        offset="md",
                        mb=10,
                        spacing=10
                    )
                ]
            ),
            divider_line_comp(),
            dmc.Group(
                children=[
                    dbc.Checklist(
                        options=[
                            {"label": "Legacy Thresholding Segmentation",
                             "value": "legacy"},
                        ],
                        id="simple_legacy_id",
                        switch=True,
                        value=[],
                        labelCheckedClassName="text-success",
                        inputCheckedClassName="border-success bg-success",
                    ),
                    hover_card(
                        target=DashIconify(
                            icon="mage:message-question-mark-round-fill",
                            color="yellow", width=20),
                        notes="This is a thresholding based segmentation "
                              "same as the segmentation available in shapeIn "
                              "(ZMD device). \n Default threshold value [-6]. "
                              "Tune it according to your use case."
                    )
                ],
                align="left",
                spacing=5
            ),
            html.Ul(
                id="simple_legacy_options",
                children=[
                    form_group_input(
                        comp_id="simple_legacy_thresh_id",
                        label="Threshold Value:",
                        label_key="thresh",
                        min=-10, max=10, step=1,
                        default=-6
                    )
                ]
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
            dcc.Store(id="store_simple_segm_data", storage_type="local"),
        ]
    )


@callback(
    Output("simple_measure_options", "children"),
    Output("store_simple_segm_data", "data"),
    Input("simple_unet_id", "value"),
    Input("simple_measure_options", "value"),
    Input("simple_legacy_id", "value"),
    Input("simple_legacy_thresh_id", "value")
)
def show_and_cache_segment_options(unet_click, measure_option, legacy_click,
                                   legacy_thresh):
    """This circular callback fetches unet model metadata from the DVC repo
    and shows it as dmc.RadioGroup options, enable the user to select the
    appropriate options from the same dmc.RadioItem options."""

    model_dict = dvc_gitlab.get_model_metadata()

    check_boxes = [
        dmc.Radio(
            label=f"{meta['device'].capitalize()} device, "
                  f"{meta['type'].capitalize()} cells",
            value=model_ckp, color="green"
        ) for model_ckp, meta in model_dict.items()]

    segm_options = {}
    if unet_click and measure_option:
        segm_options[unet_click[0]] = {"model_file": measure_option}

    if legacy_click and legacy_thresh:
        segm_options[legacy_click[0]] = {"thresh": legacy_thresh}

    return check_boxes, segm_options


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
    Output("simple_legacy_options", "style"),
    Input("simple_legacy_id", "value"),
)
def toggle_legacy_options(legacy_click):
    """Toggle legacy segmentation options with legacy switch"""
    if legacy_click:
        return {"display": "block"}
    else:
        return {"display": "none"}


@callback(
    Output("store_simple_template", "data"),
    Input("simple_title_drop", "value"),
    Input("simple_title_text", "value"),
    Input("store_simple_segm_data", "data"),
    Input("simp_classifier_id", "value"),
    Input("simp_postana_id", "value"),
    Input("show_grid", "selectedRows")
)
def collect_simple_pipeline_params(author_name, simple_title, segment_options,
                                   simple_classifier, simple_postana,
                                   selected_files):
    """Collect all the user selected parameters. Then, it updates the simple
    issue template. Updated template will be cached"""
    params = list(segment_options.keys()) + simple_classifier + simple_postana

    # Update the template, only when author name, title, and data files
    # to process are entered
    if author_name and simple_title and selected_files and segment_options:
        rtdc_files = [s["filepath"] for s in selected_files]
        # Create a template dict with title
        pipeline_template = {"title": simple_title}
        # Update the simple template from request repo
        description = update_simple_template(params, segment_options,
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
    Input("store_simple_segm_data", "data")
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
