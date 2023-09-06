import dash
import os
from dash import callback_context as cc
import dash_bootstrap_components as dbc
from dash import callback, html, Input, Output, State, dcc

from ..gitlab_api import get_gitlab_obj
from .utils import update_simple_template
from .hsm_grid import create_hsm_grid, display_paths_comp
from ..components import (header_comp, paragraph_comp, checklist_comp,
                          group_accordion, popup_comp, button_comp,
                          divider_line_comp, line_breaks, input_with_dropdown,
                          form_group_dropdown, form_group_input)

BASENAME_PREFIX = os.getenv("BASENAME_PREFIX")

# BASENAME_PREFIX = "/test/"
gitlab_obj = get_gitlab_obj()


def simple_request():
    return dbc.Toast(
        [
            popup_comp(comp_id="simple_popup"),
            line_breaks(times=1),
            header_comp("⦿ Pipeline for segmentation and/or classification "
                        "(prediction) and analysis of data.", indent=40),
            header_comp("⦿ Choosing multiple Segmentation or Prediction "
                        "algorithms will create a matrix of jobs (multiple "
                        "jobs).", indent=40),

            line_breaks(times=2),
            group_accordion(
                [
                    dbc.AccordionItem(
                        [
                            input_with_dropdown(
                                comp_id="simple_title",
                                # drop_options=gitlab_obj.get_project_members(),
                                drop_options=["eoghan", "max", "nadia",
                                              "paul", "raghava"],
                                dropdown_holder="User",
                                input_holder="Type title...",
                                with_button=False, width=80
                            )
                        ],
                        title="Title (required)",
                    ),

                    dbc.AccordionItem(
                        [
                            checklist_comp(
                                comp_id="simp_segm_id",
                                options=["legacy", "mlunet",
                                         "watershed", "std"],
                                defaults=["legacy", "mlunet"]
                            )
                        ],
                        title="Segmentation",
                    ),
                    dbc.AccordionItem(
                        [
                            paragraph_comp("Classification Model"),
                            checklist_comp(
                                comp_id="simp_classifier_id",
                                options=["MNet", "Bloody-Bunny"],
                                defaults=["Bloody-Bunny"]
                            )
                        ],
                        title="Prediction",
                    ),
                    dbc.AccordionItem(
                        [
                            checklist_comp(
                                comp_id="simp_postana_id",
                                options=["Benchmarking",
                                         "Scatter Plots"],
                                defaults=["Scatter Plots"]
                            )
                        ],
                        title="Post Analysis",
                    ),
                    dbc.AccordionItem(
                        [
                            create_hsm_grid(),
                            line_breaks(times=2),
                        ],
                        title="Data to Process",
                    )
                ],
                middle=True
            ),
            line_breaks(times=4),
            display_paths_comp(comp_id="show_grid"),
            line_breaks(times=4),
            button_comp(label="Create pipeline",
                        disabled=True,
                        comp_id="create_simple_pipeline_button"),
            line_breaks(times=5),
            dcc.Store(id="store_simple_template")

        ],
        id="simple_request_toast",
        header="Simple pipeline request",
        header_style={"background-color": "#017b70",
                      "font-size": "25px",
                      "color": "white"},
        is_open=True,
        className="my-toast"
    )


@callback(
    Output("store_simple_template", "data"),
    Input("simple_title_text", "value"),
    Input("simp_segm_id", "value"),
    Input("simp_classifier_id", "value"),
    Input("simp_postana_id", "value"),
    Input("hsm_grid", "selectedRows"),
    Input("store_input_paths", "data")
)
def collect_simple_pipeline_params(simple_title, simple_segment,
                                   simple_classifier, simple_postana,
                                   selected_rows, stored_input):
    params = simple_segment + simple_classifier + simple_postana
    rtdc_files = [] + stored_input
    if selected_rows:
        selected_paths = [s["filepath"] for s in selected_rows]
        for path_parts in selected_paths:
            new_path = "/".join(path_parts)
            rtdc_files.append(new_path)

    pipeline_template = {}
    if simple_title is not None and len(rtdc_files) != 0:
        simple_template = gitlab_obj.get_simple_template()
        pipeline_template["title"] = simple_title
        description = update_simple_template(params,
                                             rtdc_files,
                                             simple_template)
        pipeline_template["description"] = description
        return pipeline_template


@callback(
    Output("create_simple_pipeline_button", "disabled"),
    Input("simple_title_text", "value"),
    Input("hsm_grid", "selectedRows"),
    Input("store_input_paths", "data")
)
def toggle_simple_create_pipeline_button(title, selected_rows, stored_input):
    rtdc_files = [] + stored_input
    if selected_rows:
        selected_paths = [s["filepath"] for s in selected_rows]
        for path_parts in selected_paths:
            new_path = "/".join(path_parts)
            rtdc_files.append(new_path)
    if title is None or title == "":
        return True
    elif len(rtdc_files) == 0:
        return True
    else:
        return False


@callback(
    Output("simple_popup", "is_open"),
    Output("refresh_app", "pathname"),
    Input("create_simple_pipeline_button", "n_clicks"),
    Input("store_simple_template", "data"),
    Input("simple_popup_close", "n_clicks"),
    State("simple_popup", "is_open")
)
def simple_request_submission_popup(_, cached_simp_temp, close, popup):
    button_trigger = [p["prop_id"] for p in cc.triggered][0]
    if "create_simple_pipeline_button" in button_trigger:
        gitlab_obj.run_pipeline(cached_simp_temp)
        return not popup, dash.no_update
    if close:
        return not popup, BASENAME_PREFIX
    else:
        return popup, dash.no_update


def advanced_request():
    return dbc.Toast(
        [
            popup_comp(comp_id="advanced_popup"),
            line_breaks(times=1),
            header_comp("⦿ Pipeline for segmentation and/or classification "
                        "(prediction) and analysis of data.", indent=40),

            header_comp("⦿ Choosing multiple Segmentation or Prediction "
                        "algorithms will create a matrix of jobs "
                        "(multiple jobs).", indent=40),

            line_breaks(times=2),
            group_accordion(
                [
                    # Title section
                    dbc.AccordionItem(
                        [
                            input_with_dropdown(
                                comp_id="advanced_title",
                                drop_options=["eoghan", "max",
                                              "nadia",
                                              "paul",
                                              "raghava"],
                                dropdown_holder="User",
                                input_holder="Type title...",
                                with_button=False, width=80
                            )
                        ],
                        title="Title (required)",
                    ),
                    # dcevent version section
                    dbc.AccordionItem(
                        [
                            checklist_comp(
                                comp_id="dcevent_ver_id",
                                options=["dcevent version=latest"],
                                defaults=["dcevent version=latest"]
                            ),
                        ],
                        title="dcevent version",
                    ),
                    # Segmentation section
                    dbc.AccordionItem(
                        [
                            # MLUNet segmentor section
                            checklist_comp(
                                comp_id="mlunet_id",
                                options=["mlunet"],
                                defaults=["mlunet"]
                            ),

                            html.Ul(
                                form_group_dropdown(
                                    comp_id="mlunet_model_ckp_id",
                                    label="model_path:",
                                    box_width=18,
                                    options=[
                                        "unet-double-d3-f3_g1_81bbe.ckp",
                                        "unet-double-d3-f3_g2_cwfas.ckp"],
                                    defaults=[
                                        "unet-double-d3-f3_g1_81bbe.ckp"]

                                ),
                                id="mlunet_options"
                            ),

                            divider_line_comp(),
                            # Legacy segmentor section
                            checklist_comp(
                                comp_id="legacy_id",
                                options=["legacy: Legacy thresholding"
                                         " with OpenCV"],
                                defaults=[]
                            ),
                            html.Ul([
                                form_group_input(
                                    comp_id="legacy_thresh_id",
                                    label="thresh:",
                                    min=-10, max=10, step=1,
                                    default=-6
                                ),
                                form_group_input(
                                    comp_id="legacy_blur_id",
                                    label="blur:",
                                    min=0, max=10, step=1,
                                    default=0
                                ),
                                form_group_input(
                                    comp_id="legacy_binop_id",
                                    label="binaryops:",
                                    min=0, max=10, step=1,
                                    default=5
                                ),
                                form_group_input(
                                    comp_id="legacy_difme_id",
                                    label="diff_method:",
                                    min=0, max=10, step=1,
                                    default=1
                                ),
                                form_group_dropdown(
                                    comp_id="legacy_clrbo_id",
                                    label="clear_border:",
                                    options=["True", "False"],
                                    defaults=["True"]
                                ),
                                form_group_dropdown(
                                    comp_id="legacy_filho_id",
                                    label="fill_holes:",
                                    options=["True", "False"],
                                    defaults=["True"]
                                ),

                                form_group_input(
                                    comp_id="legacy_cldis_id",
                                    label="close_disk:",
                                    min=0, max=10, step=1,
                                    default=5
                                ),
                            ],
                                id="legacy_options"
                            ),

                            divider_line_comp(),

                            checklist_comp(
                                comp_id="watershed_id",
                                options=["watershed: Watershed algorithm"],
                                defaults=[]
                            ),
                            html.Ul([
                                form_group_dropdown(
                                    comp_id="wtrshd_clrbo_id",
                                    label="clear_border:",
                                    options=["True", "False"],
                                    defaults=["True"]
                                ),
                                form_group_dropdown(
                                    comp_id="wtrshd_filho_id",
                                    label="fill_holes:",
                                    options=["True", "False"],
                                    defaults=["True"]
                                ),
                                form_group_input(
                                    comp_id="wtrshd_cldis_id",
                                    label="close_disk:",
                                    min=0, max=10, step=1,
                                    default=5
                                ),
                            ],
                                id="watershed_options"
                            ),

                            divider_line_comp(),

                            # STD segmentor section
                            checklist_comp(
                                comp_id="std_id",
                                options=["std: Standard-deviation-"
                                         "based thresholding"],
                                defaults=[]
                            ),
                            html.Ul([
                                form_group_dropdown(
                                    comp_id="std_clrbo_id",
                                    label="clear_border:",
                                    options=["True", "False"],
                                    defaults=["True"]
                                ),
                                form_group_dropdown(
                                    comp_id="std_filho_id",
                                    label="fill_holes:",
                                    options=["True", "False"],
                                    defaults=["True"]
                                ),
                                form_group_input(
                                    comp_id="std_cldis_id",
                                    label="close_disk:",
                                    min=0, max=10, step=1,
                                    default=5
                                ),
                            ],
                                id="std_options"
                            ),

                        ],
                        title="Segmentation Algorithm",
                    ),
                    dbc.AccordionItem(
                        [
                            checklist_comp(
                                comp_id="rollmed_id",
                                options=["rollmed: Rolling median "
                                         "RT-DC background image "
                                         "computation"],
                                defaults=[
                                    "rollmed: Rolling median RT-DC "
                                    "background image computation"]
                            ),

                            html.Ul([
                                form_group_input(
                                    comp_id="rollmed_ksize_id",
                                    label="kernel_size:",
                                    min=50, max=500, step=10,
                                    default=100
                                ),
                                form_group_input(
                                    comp_id="rollmed_bsize_id",
                                    label="batch_size:",
                                    min=100, max=100000, step=100,
                                    default=10000
                                ),
                            ],
                                id="rollmed_options"
                            ),

                            divider_line_comp(),

                            checklist_comp(
                                comp_id="sparsemed_id",
                                options=["sparsemed: Sparse median "
                                         "background correction with "
                                         "cleansing"],
                                defaults=[]
                            ),

                            html.Ul([
                                form_group_input(
                                    comp_id="sparsemed_ksize_id",
                                    label="kernel_size:",
                                    min=50, max=500, step=10,
                                    default=100
                                ),
                                form_group_input(
                                    comp_id="sparsemed_bsize_id",
                                    label="batch_size:",
                                    min=100, max=100000, step=100,
                                    default=10000
                                ),
                                form_group_input(
                                    comp_id="sparsemed_thrcln_id",
                                    label="thresh_cleansing:",
                                    min=0, max=1, step=1,
                                    default=0
                                ),
                                form_group_input(
                                    comp_id="sparsemed_frcln_id",
                                    label="frac_cleansing:",
                                    min=0, max=1, step=0.1,
                                    default=0.8
                                ),
                            ],
                                id="sparsemed_options"
                            ),

                        ],
                        title="Background Correction / Subtraction Method",
                    ),

                    dbc.AccordionItem(
                        [
                            checklist_comp(
                                comp_id="ngate_id",
                                options=["norm gating"],
                                defaults=["norm gating"]
                            ),

                            html.Ul([
                                form_group_dropdown(
                                    comp_id="ngate_ongate_id",
                                    label="online_gates:",
                                    options=["True", "False"],
                                    defaults=["False"]
                                ),
                                form_group_input(
                                    comp_id="ngate_thrmsk_id",
                                    label="size_thresh_mask:",
                                    min=0, max=10, step=1,
                                    default=5
                                ),
                            ],
                                id="ngate_options"
                            ),

                            divider_line_comp(),

                            checklist_comp(
                                comp_id="repro_id",
                                options=["--reproduce=False"],
                                defaults=[]
                            )
                        ],
                        title="Further Options",
                    ),

                    dbc.AccordionItem(
                        [
                            checklist_comp(
                                comp_id="dcml_ver_id",
                                options=["dcml version"],
                                defaults=["dcml version"]
                            ),
                            checklist_comp(
                                comp_id="classifier_id",
                                options=["Classification Model"],
                                defaults=["Classification Model"]
                            ),
                        ],
                        title="Prediction",
                    ),
                    dbc.AccordionItem(
                        [
                            create_hsm_grid(),
                            line_breaks(times=2),
                        ],
                        title="Data to Process",
                    )
                ],
                middle=True
            ),
            line_breaks(times=4),
            display_paths_comp(comp_id="show_grid"),
            line_breaks(times=4),
            button_comp(label="Create pipeline",
                        disabled=True,
                        comp_id="create_advanced_pipeline_button"),

            dcc.Store(id="store_advanced_template")

        ],
        id="advanced_request_toast",
        header="Advanced pipeline request",
        header_style={"background-color": "#017b70",
                      "font-size": "25px",
                      "color": "white"},
        is_open=True,
        className="my-toast"
    )


@callback(
    Output("mlunet_options", "style"),
    Input("mlunet_id", "value"),
)
def toggle_mlunet_options(mlunet_opt):
    if len(mlunet_opt) == 1:
        return {"display": "block"}
    else:
        return {"display": "none"}


@callback(
    Output("legacy_options", "style"),
    Input("legacy_id", "value"),
)
def toggle_legacy_options(legacy_opt):
    if len(legacy_opt) == 1:
        return {"display": "block"}
    else:
        return {"display": "none"}


@callback(
    Output("watershed_options", "style"),
    Input("watershed_id", "value"),
)
def toggle_watershed_options(watershed_opt):
    if len(watershed_opt) == 1:
        return {"display": "block"}
    else:
        return {"display": "none"}


@callback(
    Output("std_options", "style"),
    Input("std_id", "value"),
)
def toggle_std_options(std_opt):
    if len(std_opt) == 1:
        return {"display": "block"}
    else:
        return {"display": "none"}


@callback(
    Output("rollmed_options", "style"),
    Input("rollmed_id", "value"),
)
def toggle_rollmed_options(rollmed_opt):
    if len(rollmed_opt) == 1:
        return {"display": "block"}
    else:
        return {"display": "none"}


@callback(
    Output("sparsemed_options", "style"),
    Input("sparsemed_id", "value"),
)
def toggle_sparsemed_options(sparsemed_opt):
    if len(sparsemed_opt) == 1:
        return {"display": "block"}
    else:
        return {"display": "none"}


@callback(
    Output("ngate_options", "style"),
    Input("ngate_id", "value"),
)
def toggle_ngate_options(ngate_opt):
    if len(ngate_opt) == 1:
        return {"display": "block"}
    else:
        return {"display": "none"}


@callback(
    Output("advanced_popup", "is_open"),
    Input("create_advanced_pipeline_button", "n_clicks"),
    State("advanced_popup", "is_open")
)
def advanced_request_submission_popup(click, popup):
    if click:
        return not popup
    return popup

# @callback(Output("create_advanced_pipeline_button", "disabled"),
#           Input("advanced_title_text", "value"),
#           Input("hsm_grid", "selectedRows"),
#           Input("store_input_paths", "data"))
# def toggle_advanced_create_pipeline_button(title, selected_rows, stored_input):
#     print(title)
#     rtdc_files = [] + stored_input
#     if selected_rows:
#         selected_paths = [s["filepath"] for s in selected_rows]
#         for path_parts in selected_paths:
#             new_path = "/".join(path_parts)
#             rtdc_files.append(new_path)
#     if title is None or title == "":
#         return True
#     elif len(rtdc_files) == 0:
#         return True
#     else:
#         return False
