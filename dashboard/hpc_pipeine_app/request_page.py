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
        id="simple_request_toast",
        header="Simple pipeline request",
        header_style={"background-color": "#017b70",
                      "font-size": "25px",
                      "color": "white"},
        is_open=True,
        className="my-toast",
        children=[
            popup_comp(comp_id="simple_popup"),
            line_breaks(times=1),
            header_comp("⦿ Pipeline for segmentation and/or classification "
                        "(prediction) and analysis of data.", indent=40),
            header_comp("⦿ Choosing multiple Segmentation or Prediction "
                        "algorithms will create a matrix of jobs (multiple "
                        "jobs).", indent=40),
            line_breaks(times=2),
            group_accordion(
                children=[
                    dbc.AccordionItem(
                        title="Title (required)",
                        children=[
                            input_with_dropdown(
                                comp_id="simple_title",
                                # drop_options=gitlab_obj.get_project_members(),
                                drop_options=["eoghan", "max", "nadia",
                                              "paul", "raghava"],
                                dropdown_holder="User",
                                input_holder="Type title...",
                                with_button=False, width=80
                            )
                        ]
                    ),
                    dbc.AccordionItem(
                        title="Segmentation",
                        children=[
                            checklist_comp(
                                comp_id="simp_segm_id",
                                options=["legacy", "mlunet",
                                         "watershed", "std"],
                                defaults=["legacy", "mlunet"]
                            )
                        ]
                    ),
                    dbc.AccordionItem(
                        title="Prediction",
                        children=[
                            paragraph_comp("Classification Model"),
                            checklist_comp(
                                comp_id="simp_classifier_id",
                                options=["MNet", "Bloody-Bunny"],
                                defaults=["Bloody-Bunny"]
                            )
                        ]
                    ),
                    dbc.AccordionItem(
                        title="Post Analysis",
                        children=[
                            checklist_comp(
                                comp_id="simp_postana_id",
                                options=["Benchmarking",
                                         "Scatter Plots"],
                                defaults=["Scatter Plots"]
                            )
                        ]
                    ),
                    dbc.AccordionItem(
                        title="Data to Process",
                        children=[
                            create_hsm_grid(),
                            line_breaks(times=2),
                        ]
                    )
                ],
                middle=True
            ),
            line_breaks(times=3),
            display_paths_comp(comp_id="show_grid"),
            line_breaks(times=3),
            button_comp(label="Create pipeline",
                        disabled=True,
                        comp_id="create_simple_pipeline_button"),
            line_breaks(times=5),
            dcc.Store(id="store_simple_template")
        ]
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
        id="advanced_request_toast",
        header="Advanced pipeline request",
        header_style={"background-color": "#017b70",
                      "font-size": "25px",
                      "color": "white"},
        is_open=True,
        className="my-toast",
        children=[
            popup_comp(comp_id="advanced_popup"),
            line_breaks(times=1),
            header_comp("⦿ Pipeline for segmentation and/or classification "
                        "(prediction) and analysis of data.", indent=40),

            header_comp("⦿ Choosing multiple Segmentation or Prediction "
                        "algorithms will create a matrix of jobs "
                        "(multiple jobs).", indent=40),

            line_breaks(times=2),
            group_accordion(
                children=[
                    # Title section
                    dbc.AccordionItem(
                        title="Title (required)",
                        children=[
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
                        ]
                    ),
                    # dcevent version section
                    dbc.AccordionItem(
                        title="dcevent version",
                        children=[
                            checklist_comp(
                                comp_id="dcevent_ver_id",
                                options=["dcevent version=latest"],
                                defaults=["dcevent version=latest"]
                            )
                        ]
                    ),
                    # Segmentation section
                    dbc.AccordionItem(
                        title="Segmentation Algorithm",
                        children=[
                            # MLUNet segmentor section
                            checklist_comp(
                                comp_id="mlunet_id",
                                options=["mlunet"],
                                defaults=["mlunet"]
                            ),
                            html.Ul(
                                id="mlunet_options",
                                children=[
                                    form_group_dropdown(
                                        comp_id="mlunet_model_ckp_id",
                                        label="model_path:",
                                        box_width=18,
                                        options=[
                                            "unet-double-d3-f3_g1_81bbe.ckp",
                                            "unet-double-d3-f3_g2_cwfas.ckp"],
                                        defaults=[
                                            "unet-double-d3-f3_g1_81bbe.ckp"]
                                    )
                                ]
                            ),
                            divider_line_comp(),
                            # Legacy segmentor section
                            checklist_comp(
                                comp_id="legacy_id",
                                options=["legacy: Legacy thresholding"
                                         " with OpenCV"],
                                defaults=[]
                            ),
                            html.Ul(
                                id="legacy_options",
                                children=[
                                    form_group_input(
                                        comp_id={"type": "legacy_param",
                                                 "index": 1},
                                        label="thresh:",
                                        min=-10, max=10, step=1,
                                        default=-6
                                    ),
                                    form_group_input(
                                        comp_id={"type": "legacy_param",
                                                 "index": 2},
                                        label="blur:",
                                        min=0, max=10, step=1,
                                        default=0
                                    ),
                                    form_group_input(
                                        comp_id={"type": "legacy_param",
                                                 "index": 3},
                                        label="binaryops:",
                                        min=0, max=10, step=1,
                                        default=5
                                    ),
                                    form_group_input(
                                        comp_id={"type": "legacy_param",
                                                 "index": 4},
                                        label="diff_method:",
                                        min=0, max=10, step=1,
                                        default=1
                                    ),
                                    form_group_dropdown(
                                        comp_id={"type": "legacy_param",
                                                 "index": 5},
                                        label="clear_border:",
                                        options=["True", "False"],
                                        defaults=["True"]
                                    ),
                                    form_group_dropdown(
                                        comp_id={"type": "legacy_param",
                                                 "index": 6},
                                        label="fill_holes:",
                                        options=["True", "False"],
                                        defaults=["True"]
                                    ),

                                    form_group_input(
                                        comp_id={"type": "legacy_param",
                                                 "index": 7},
                                        label="close_disk:",
                                        min=0, max=10, step=1,
                                        default=5
                                    ),
                                ]
                            ),
                            divider_line_comp(),
                            checklist_comp(
                                comp_id="watershed_id",
                                options=["watershed: Watershed algorithm"],
                                defaults=[]
                            ),
                            html.Ul(
                                id="watershed_options",
                                children=[
                                    form_group_dropdown(
                                        comp_id={"type": "watershd_param",
                                                 "index": 1},
                                        label="clear_border:",
                                        options=["True", "False"],
                                        defaults=["True"]
                                    ),
                                    form_group_dropdown(
                                        comp_id={"type": "watershd_param",
                                                 "index": 2},
                                        label="fill_holes:",
                                        options=["True", "False"],
                                        defaults=["True"]
                                    ),
                                    form_group_input(
                                        comp_id={"type": "watershd_param",
                                                 "index": 3},
                                        label="close_disk:",
                                        min=0, max=10, step=1,
                                        default=5
                                    ),
                                ]
                            ),
                            divider_line_comp(),
                            # STD segmentor section
                            checklist_comp(
                                comp_id="std_id",
                                options=["std: Standard-deviation-"
                                         "based thresholding"],
                                defaults=[]
                            ),
                            html.Ul(
                                id="std_options",
                                children=[
                                    form_group_dropdown(
                                        comp_id={"type": "std_param",
                                                 "index": 1},
                                        label="clear_border:",
                                        options=["True", "False"],
                                        defaults=["True"]
                                    ),
                                    form_group_dropdown(
                                        comp_id={"type": "std_param",
                                                 "index": 2},
                                        label="fill_holes:",
                                        options=["True", "False"],
                                        defaults=["True"]
                                    ),
                                    form_group_input(
                                        comp_id={"type": "std_param",
                                                 "index": 3},
                                        label="close_disk:",
                                        min=0, max=10, step=1,
                                        default=5
                                    )
                                ]
                            ),
                        ]
                    ),
                    dbc.AccordionItem(
                        title="Background Correction / Subtraction Method",
                        children=[
                            checklist_comp(
                                comp_id="rollmed_id",
                                options=["rollmed: Rolling median "
                                         "RT-DC background image "
                                         "computation"],
                                defaults=[
                                    "rollmed: Rolling median RT-DC "
                                    "background image computation"]
                            ),
                            html.Ul(
                                id="rollmed_options",
                                children=[
                                    form_group_input(
                                        comp_id={"type": "rollmed_param",
                                                 "index": 1},
                                        label="kernel_size:",
                                        min=50, max=500, step=10,
                                        default=100
                                    ),
                                    form_group_input(
                                        comp_id={"type": "rollmed_param",
                                                 "index": 2},
                                        label="batch_size:",
                                        min=100, max=100000, step=100,
                                        default=10000
                                    )
                                ]
                            ),
                            divider_line_comp(),
                            checklist_comp(
                                comp_id="sparsemed_id",
                                options=["sparsemed: Sparse median "
                                         "background correction with "
                                         "cleansing"],
                                defaults=[]
                            ),
                            html.Ul(
                                id="sparsemed_options",
                                children=[
                                    form_group_input(
                                        comp_id={"type": "sparsemed_param",
                                                 "index": 1},
                                        label="kernel_size:",
                                        min=50, max=500, step=10,
                                        default=100
                                    ),
                                    form_group_input(
                                        comp_id={"type": "sparsemed_param",
                                                 "index": 2},
                                        label="batch_size:",
                                        min=100, max=100000, step=100,
                                        default=10000
                                    ),
                                    form_group_input(
                                        comp_id={"type": "sparsemed_param",
                                                 "index": 3},
                                        label="thresh_cleansing:",
                                        min=0, max=1, step=1,
                                        default=0
                                    ),
                                    form_group_input(
                                        comp_id={"type": "sparsemed_param",
                                                 "index": 4},
                                        label="frac_cleansing:",
                                        min=0, max=1, step=0.1,
                                        default=0.8
                                    )
                                ]
                            )
                        ]
                    ),
                    dbc.AccordionItem(
                        title="Available gating options",
                        children=[
                            checklist_comp(
                                comp_id="ngate_id",
                                options=["norm gating"],
                                defaults=["norm gating"]
                            ),
                            html.Ul(
                                id="ngate_options",
                                children=[
                                    form_group_dropdown(
                                        comp_id={"type": "ngate_param",
                                                 "index": 1},
                                        label="online_gates:",
                                        options=["True", "False"],
                                        defaults=["False"],
                                        gap=2
                                    ),
                                    form_group_input(
                                        comp_id={"type": "ngate_param",
                                                 "index": 2},
                                        label="size_thresh_mask:",
                                        min=0, max=10, step=1,
                                        default=5, gap=2
                                    )
                                ]
                            )
                        ]
                    ),
                    dbc.AccordionItem(
                        title="Further Options",
                        children=[
                            checklist_comp(
                                comp_id="repro_id",
                                options=["--reproduce=False"],
                                defaults=[]
                            )
                        ]
                    ),
                    dbc.AccordionItem(
                        title="Prediction",
                        children=[
                            checklist_comp(
                                comp_id="classifier_id",
                                options=["Classification Model"],
                                defaults=["Classification Model"]
                            ),
                            html.Ul(
                                id="classifier_options",
                                children=[
                                    form_group_dropdown(
                                        comp_id="classifier_model_ckp_id",
                                        label="model_path:",
                                        box_width=21,
                                        options=[
                                            "bloody-bunny_g1_bacae: Bloody Bunny"],
                                        defaults=[
                                            "bloody-bunny_g1_bacae: Bloody Bunny"]
                                    )
                                ]
                            )
                        ]
                    ),
                    dbc.AccordionItem(
                        title="Data to Process",
                        children=[
                            create_hsm_grid(),
                            line_breaks(times=2),
                        ]
                    )
                ],
                middle=True
            ),
            line_breaks(times=3),
            display_paths_comp(comp_id="show_grid"),
            line_breaks(times=4),
            button_comp(label="Create pipeline",
                        disabled=True,
                        comp_id="create_advanced_pipeline_button"),
            line_breaks(times=5),
            dcc.Store(id="store_advanced_template")
        ]
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
    Output("classifier_options", "style"),
    Input("classifier_id", "value"),
)
def toggle_bb_options(classifier_model_ckp):
    if len(classifier_model_ckp) == 1:
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


# @callback(
#     Output("store_advanced_template", "data"),
#     Input("advanced_title_text", "value"),
#     Input("dcevent_ver_id", "value"),
#     Input("mlunet_id", "value"),
#     Input("legacy_id", "value"),
#     Input("legacy_thresh_id", "value"),
#     Input("legacy_blur_id", "value"),
#     Input("legacy_binop_id", "value"),
#     Input("legacy_difme_id", "value"),
#     Input("legacy_clrbo_id", "value"),
#     Input("legacy_filho_id", "value"),
#     Input("legacy_cldis_id", "value"),
#     Input("wtrshd_clrbo_id", "value"),
#     Input("wtrshd_filho_id", "value"),
#     Input("wtrshd_cldis_id", "value"),
#     Input("std_clrbo_id", "value"),
#     Input("std_filho_id", "value"),
#     Input("std_cldis_id", "value"),
#     Input("rollmed_ksize_id", "value"),
#     Input("rollmed_bsize_id", "value"),
#     Input("sparsemed_ksize_id", "value"),
#     Input("sparsemed_bsize_id", "value"),
#     Input("sparsemed_thrcln_id", "value"),
#     Input("sparsemed_frcln_id", "value"),
#     Input("ngate_ongate_id", "value"),
#     Input("ngate_thrmsk_id", "value"),
#
#     Input("simp_segm_id", "value"),
#     Input("simp_classifier_id", "value"),
#     Input("simp_postana_id", "value"),
#     Input("hsm_grid", "selectedRows"),
#     Input("store_input_paths", "data")
# )
# def collect_advanced_pipeline_params(*args):
#     print(args)
#     # params = simple_segment + simple_classifier + simple_postana
#     # rtdc_files = [] + stored_input
#     # if selected_rows:
#     #     selected_paths = [s["filepath"] for s in selected_rows]
#     #     for path_parts in selected_paths:
#     #         new_path = "/".join(path_parts)
#     #         rtdc_files.append(new_path)
#     #
#     # pipeline_template = {}
#     # if simple_title is not None and len(rtdc_files) != 0:
#     #     simple_template = gitlab_obj.get_simple_template()
#     #     pipeline_template["title"] = simple_title
#     #     description = update_simple_template(params,
#     #                                          rtdc_files,
#     #                                          simple_template)
#     #     pipeline_template["description"] = description
#     #     return pipeline_template
