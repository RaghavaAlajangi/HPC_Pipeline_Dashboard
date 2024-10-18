from dash import ALL, callback, dcc, html, Input, Output, State
from dash import callback_context as cc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from .common import (button_comp, checklist_comp, divider_line_comp,
                     form_group_dropdown, form_group_input, group_accordion,
                     header_comp, hover_card, line_breaks, popup_comp)
from .hsm_grid import create_hsm_grid, create_show_grid
from .utils import update_advanced_template
from ..gitlab import get_gitlab_instances


def get_user_list():
    """Fetch the members list from request repo"""
    request_gitlab, _ = get_gitlab_instances()
    return request_gitlab.get_project_members()


def get_advanced_template():
    """Fetch the advanced request template from request repo"""
    request_gitlab, _ = get_gitlab_instances()
    return request_gitlab.get_request_template(temp_type="advanced")


def advanced_title_section():
    return dbc.AccordionItem(
        title="Title (required)",
        children=[
            html.Div(
                dbc.InputGroup(
                    [
                        dbc.Select(
                            placeholder="Select Username",
                            id="advanced_title_drop",
                            options=[
                                {"label": member.name,
                                 "value": member.username} for
                                member in get_user_list()
                            ],
                            style={"width": "18%"},
                        ),
                        dbc.Input(
                            type="text",
                            id="advanced_title_text",
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
    )


def advanced_segmentation_section():
    # Get the default parameters from request repo
    request_gitlab, _ = get_gitlab_instances()
    dcevent_params = request_gitlab.get_defaults()
    legacy_seg = dcevent_params["legacy"]
    watershed_seg = dcevent_params["watershed"]
    std_seg = dcevent_params["std"]
    return dbc.AccordionItem(
        title="Segmentation Algorithm",
        children=[
            # MLUNet segmentor section
            dmc.Group(
                children=[
                    # UNet checkbox (switch)
                    dbc.Checklist(
                        options=[
                            {"label": "U-Net Segmentation",
                             "value": "mlunet: UNET"},
                        ],
                        id="advanced_unet_id",
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
                id="advanced_unet_options",
                children=[
                    dmc.RadioGroup(
                        id="advanced_measure_options",
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
            # Legacy segmentor section
            checklist_comp(
                comp_id="legacy_id",
                options={"legacy: Legacy thresholding"
                         " with OpenCV": False}
            ),
            html.Ul(
                id="legacy_options",
                children=[
                    form_group_input(
                        comp_id={"type": "legacy_param",
                                 "index": 1},
                        label="Threshold Value",
                        label_key="thresh",
                        min=legacy_seg["thresh"]["min"],
                        max=legacy_seg["thresh"]["max"],
                        step=legacy_seg["thresh"]["step"],
                        default=legacy_seg["thresh"]["default"]
                    ),
                    form_group_input(
                        comp_id={"type": "legacy_param",
                                 "index": 2},
                        label="blur",
                        label_key="blur",
                        min=legacy_seg["blur"]["min"],
                        max=legacy_seg["blur"]["max"],
                        step=1,
                        # step=legacy_seg["blur"]["step"],
                        default=legacy_seg["blur"]["default"]
                    ),
                    form_group_input(
                        comp_id={"type": "legacy_param",
                                 "index": 3},
                        label="binaryops",
                        label_key="binaryops",
                        min=legacy_seg["binaryops"]["min"],
                        max=legacy_seg["binaryops"]["max"],
                        step=legacy_seg["binaryops"]["step"],
                        default=legacy_seg["binaryops"]["default"]
                    ),
                    form_group_dropdown(
                        comp_id={"type": "legacy_param",
                                 "index": 4},
                        label="diff_method",
                        label_key="diff_method",
                        options=legacy_seg["diff_method"]["options"],
                        default=legacy_seg["diff_method"]["default"]
                    ),
                    form_group_dropdown(
                        comp_id={"type": "legacy_param",
                                 "index": 5},
                        label="clear_border",
                        label_key="clear_border",
                        options=legacy_seg["clear_border"]["options"],
                        default=legacy_seg["clear_border"]["default"]
                    ),
                    form_group_dropdown(
                        comp_id={"type": "legacy_param",
                                 "index": 6},
                        label="fill_holes",
                        label_key="fill_holes",
                        options=legacy_seg["fill_holes"]["options"],
                        default=legacy_seg["fill_holes"]["default"]
                    ),

                    form_group_input(
                        comp_id={"type": "legacy_param",
                                 "index": 7},
                        label="closing_disk",
                        label_key="closing_disk",
                        min=legacy_seg["closing_disk"]["min"],
                        max=legacy_seg["closing_disk"]["max"],
                        step=legacy_seg["closing_disk"]["step"],
                        default=legacy_seg["closing_disk"]["default"]
                    ),
                ]
            ),
            divider_line_comp(),
            checklist_comp(
                comp_id="watershed_id",
                options={
                    "watershed: Watershed algorithm": False,
                }
            ),
            html.Ul(
                id="watershed_options",
                children=[
                    form_group_dropdown(
                        comp_id={"type": "watershed_param",
                                 "index": 1},
                        label="clear_border",
                        label_key="clear_border",
                        options=watershed_seg["clear_border"]["options"],
                        default=watershed_seg["clear_border"]["default"]
                    ),
                    form_group_dropdown(
                        comp_id={"type": "watershed_param",
                                 "index": 2},
                        label="fill_holes",
                        label_key="fill_holes",
                        options=watershed_seg["fill_holes"]["options"],
                        default=watershed_seg["fill_holes"]["default"]
                    ),
                    form_group_input(
                        comp_id={"type": "watershed_param",
                                 "index": 3},
                        label="closing_disk",
                        label_key="closing_disk",
                        min=watershed_seg["closing_disk"]["min"],
                        max=watershed_seg["closing_disk"]["max"],
                        step=watershed_seg["closing_disk"]["step"],
                        default=watershed_seg["closing_disk"]["default"]
                    ),
                ]
            ),
            divider_line_comp(),
            # STD segmentor section
            checklist_comp(
                comp_id="std_id",
                options={
                    "std: Standard-deviation-"
                    "based thresholding": False,
                }
            ),
            html.Ul(
                id="std_options",
                children=[
                    form_group_dropdown(
                        comp_id={"type": "std_param",
                                 "index": 1},
                        label="clear_border",
                        label_key="clear_border",
                        options=std_seg["clear_border"]["options"],
                        default=std_seg["clear_border"]["default"]
                    ),
                    form_group_dropdown(
                        comp_id={"type": "std_param",
                                 "index": 2},
                        label="fill_holes",
                        label_key="fill_holes",
                        options=std_seg["fill_holes"]["options"],
                        default=std_seg["fill_holes"]["default"]
                    ),
                    form_group_input(
                        comp_id={"type": "std_param",
                                 "index": 3},
                        label="closing_disk",
                        label_key="closing_disk",
                        min=std_seg["closing_disk"]["min"],
                        max=std_seg["closing_disk"]["max"],
                        step=std_seg["closing_disk"]["step"],
                        default=std_seg["closing_disk"]["default"]
                    )
                ]
            )
        ]
    )


def background_correction_section():
    # Get the default parameters from request repo
    request_gitlab, _ = get_gitlab_instances()
    dcevent_params = request_gitlab.get_defaults()
    rollmed_bg = dcevent_params["rollmed"]
    sparsemed_bg = dcevent_params["sparsemed"]
    return dbc.AccordionItem(
        title="Background Correction / Subtraction Method",
        children=[
            checklist_comp(
                comp_id="rollmed_id",
                options={
                    "rollmed: Rolling median "
                    "RT-DC background image "
                    "computation": False,
                }
            ),
            html.Ul(
                id="rollmed_options",
                children=[
                    form_group_input(
                        comp_id={"type": "rollmed_param",
                                 "index": 1},
                        label="kernel_size",
                        label_key="kernel_size",
                        min=rollmed_bg["kernel_size"]["min"],
                        max=rollmed_bg["kernel_size"]["max"],
                        step=rollmed_bg["kernel_size"]["step"],
                        default=rollmed_bg["kernel_size"]["default"]
                    ),
                    form_group_input(
                        comp_id={"type": "rollmed_param",
                                 "index": 2},
                        label="batch_size",
                        label_key="batch_size",
                        min=rollmed_bg["batch_size"]["min"],
                        max=rollmed_bg["batch_size"]["max"],
                        step=rollmed_bg["batch_size"]["step"],
                        default=rollmed_bg["batch_size"]["default"]
                    )
                ]
            ),
            divider_line_comp(),
            checklist_comp(
                comp_id="sparsemed_id",
                options={
                    "sparsemed: Sparse median "
                    "background correction with "
                    "cleansing": False,
                },
                defaults=["sparsemed: Sparse median "
                          "background correction with "
                          "cleansing"]
            ),
            html.Ul(
                id="sparsemed_options",
                children=[
                    form_group_input(
                        comp_id={"type": "sparsemed_param",
                                 "index": 1},
                        label="kernel_size",
                        label_key="kernel_size",
                        min=sparsemed_bg["kernel_size"]["min"],
                        max=sparsemed_bg["kernel_size"]["max"],
                        step=sparsemed_bg["kernel_size"]["step"],
                        default=sparsemed_bg["kernel_size"]["default"]
                    ),
                    form_group_input(
                        comp_id={"type": "sparsemed_param",
                                 "index": 2},
                        label="split_time",
                        label_key="split_time",
                        min=sparsemed_bg["split_time"]["min"],
                        max=sparsemed_bg["split_time"]["max"],
                        step=sparsemed_bg["split_time"]["step"],
                        default=sparsemed_bg["split_time"]["default"]
                    ),
                    form_group_input(
                        comp_id={"type": "sparsemed_param",
                                 "index": 3},
                        label="thresh_cleansing",
                        label_key="thresh_cleansing",
                        min=sparsemed_bg["thresh_cleansing"]["min"],
                        max=sparsemed_bg["thresh_cleansing"]["max"],
                        step=sparsemed_bg["thresh_cleansing"]["step"],
                        default=sparsemed_bg["thresh_cleansing"]["default"]
                    ),
                    form_group_input(
                        comp_id={"type": "sparsemed_param",
                                 "index": 4},
                        label="frac_cleansing",
                        label_key="frac_cleansing",
                        min=sparsemed_bg["frac_cleansing"]["min"],
                        max=sparsemed_bg["frac_cleansing"]["max"],
                        step=sparsemed_bg["frac_cleansing"]["step"],
                        default=sparsemed_bg["frac_cleansing"]["default"]
                    )
                ]
            )
        ]
    )


def gating_options_section():
    # Get the default parameters from request repo
    request_gitlab, _ = get_gitlab_instances()
    dcevent_params = request_gitlab.get_defaults()
    norm_gate = dcevent_params["norm"]
    return dbc.AccordionItem(
        title="Available gating options",
        children=[
            checklist_comp(
                comp_id="norm_gate_id",
                options={
                    "norm gating": False,
                },
            ),
            html.Ul(
                id="norm_gate_options",
                children=[
                    form_group_dropdown(
                        comp_id={"type": "norm_gate_param",
                                 "index": 1},
                        label="online_gates",
                        label_key="online_gates",
                        options=norm_gate["online_gates"]["options"],
                        default=norm_gate["online_gates"]["default"]
                    ),
                    form_group_input(
                        comp_id={"type": "norm_gate_param",
                                 "index": 2},
                        label="size_thresh_mask",
                        label_key="size_thresh_mask",
                        min=norm_gate["size_thresh_mask"]["min"],
                        max=norm_gate["size_thresh_mask"]["max"],
                        step=norm_gate["size_thresh_mask"]["step"],
                        default=norm_gate["size_thresh_mask"]["default"]
                    )
                ]
            )
        ]
    )


def further_options_section():
    # Get the default parameters from request repo
    request_gitlab, _ = get_gitlab_instances()
    dcevent_params = request_gitlab.get_defaults()
    reproduce = dcevent_params["reproduce"]
    return dbc.AccordionItem(
        title="Further Options",
        children=[
            checklist_comp(
                comp_id="reproduce_flag",
                options={
                    "--reproduce": False,
                },
                defaults=["--reproduce"] if reproduce else []
            )
        ]
    )


def advanced_prediction_section():
    return dbc.AccordionItem(
        title="Classification Model",
        children=[
            checklist_comp(
                comp_id="classifier_name",
                options={
                    "bloody-bunny_g1_bacae: "
                    "Bloody Bunny": False,
                },
                defaults=["bloody-bunny_g1_bacae: "
                          "Bloody Bunny"]
            )
        ]
    )


def advanced_post_analysis_section():
    return dbc.AccordionItem(
        title="Post Analysis (Not Implemented)",
        children=[
            checklist_comp(
                comp_id="advanced_post_analysis_flag",
                options={
                    "Benchmarking": True,
                    "Scatter Plot": True,
                }
            )
        ]
    )


def advanced_data_to_process_section():
    return dbc.AccordionItem(
        title="Data to Process",
        item_id="hsm_accord",
        children=[
            create_hsm_grid(),
            line_breaks(times=2),
        ]
    )


def advanced_page_layout(refresh_path):
    """Creates advanced request page"""
    return dbc.Toast(
        id="advanced_request_toast",
        header="Advanced Pipeline Request",
        header_style={"background-color": "#017b70",
                      "font-size": "25px",
                      "color": "white"},
        is_open=True,
        className="my-toast",
        children=[
            popup_comp(comp_id="advanced_popup", refresh_path=refresh_path,
                       text="Pipeline request has been submitted!"),
            line_breaks(times=1),
            header_comp("⦿ Pipeline for segmentation and/or classification "
                        "(prediction) and analysis of data.", indent=40),
            line_breaks(times=1),
            header_comp("⦿ Choosing multiple Segmentation or Prediction "
                        "algorithms will create a matrix of jobs "
                        "(multiple jobs).", indent=40),

            line_breaks(times=2),
            group_accordion(
                children=[
                    advanced_title_section(),
                    advanced_segmentation_section(),
                    background_correction_section(),
                    gating_options_section(),
                    further_options_section(),
                    advanced_prediction_section(),
                    advanced_post_analysis_section(),
                    advanced_data_to_process_section()
                ],
                middle=True,
                open_first=True,
                comp_id="pipeline_accord"
            ),
            line_breaks(times=3),
            create_show_grid(comp_id="show_grid"),
            line_breaks(times=4),
            button_comp(label="Create pipeline",
                        disabled=True,
                        comp_id="create_advanced_pipeline_button"),
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
            dcc.Store(id="cache_advanced_template", storage_type="local"),
            dcc.Store(id="cache_advanced_unet_model_path",
                      storage_type="local"),
            dcc.Store(id="cache_legacy_params", storage_type="local"),
            dcc.Store(id="cache_watershed_params", storage_type="local"),
            dcc.Store(id="cache_std_params", storage_type="local"),
            dcc.Store(id="cache_rollmed_params", storage_type="local"),
            dcc.Store(id="cache_sparsemed_params", storage_type="local"),
            dcc.Store(id="cache_norm_gate_params", storage_type="local"),
        ]
    )


@callback(
    Output("advanced_measure_options", "children"),
    Output("cache_advanced_unet_model_path", "data"),
    Input("advanced_unet_id", "value"),
    Input("advanced_measure_options", "value")
)
def show_and_cache_unet_model_meta(unet_click, measure_option):
    """This circular callback fetches unet model metadata from the DVC repo
    and shows it as dmc.RadioGroup options, enable the user to select the
    appropriate options from the same dmc.RadioItem options."""

    _, dvc_gitlab = get_gitlab_instances()

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
    return check_boxes, segm_options


@callback(
    Output("advanced_unet_options", "style"),
    Input("advanced_unet_id", "value"),
)
def toggle_unet_options(unet_click):
    """Toggle mlunet segmentation options with unet switch"""
    if unet_click:
        return {"display": "block"}
    return {"display": "none"}


@callback(
    Output("cache_legacy_params", "data"),
    Output("legacy_options", "style"),
    Input("legacy_id", "value"),
    Input({"type": "legacy_param", "index": ALL}, "key"),
    Input({"type": "legacy_param", "index": ALL}, "value"),
)
def toggle_legacy_options(legacy_opt, leg_keys, leg_values):
    """Toggle legacy segmentation options with legacy switch, selected
    options will be cached"""
    legacy_params = {k: v for k, v in zip(leg_keys, leg_values)}

    if legacy_opt:
        return {legacy_opt[0]: legacy_params}, {"display": "block"}
    return None, {"display": "none"}


@callback(
    Output("cache_watershed_params", "data"),
    Output("watershed_options", "style"),
    Input("watershed_id", "value"),
    Input({"type": "watershed_param", "index": ALL}, "key"),
    Input({"type": "watershed_param", "index": ALL}, "value"),
)
def toggle_watershed_options(watershed_opt, water_keys, water_values):
    """Toggle watershed segmentation options with watershed switch,
    selected options will be cached"""
    water_params = {k: v for k, v in zip(water_keys, water_values)}
    if watershed_opt:
        return {watershed_opt[0]: water_params}, {"display": "block"}
    return None, {"display": "none"}


@callback(
    Output("cache_std_params", "data"),
    Output("std_options", "style"),
    Input("std_id", "value"),
    Input({"type": "std_param", "index": ALL}, "key"),
    Input({"type": "std_param", "index": ALL}, "value"),
)
def toggle_std_options(std_opt, std_keys, std_values):
    """Toggle std segmentation options with std switch, selected options
    will be cached"""
    std_params = {k: v for k, v in zip(std_keys, std_values)}
    if std_opt:
        return {std_opt[0]: std_params}, {"display": "block"}
    return None, {"display": "none"}


@callback(
    Output("cache_rollmed_params", "data"),
    Output("rollmed_options", "style"),
    Input("rollmed_id", "value"),
    Input({"type": "rollmed_param", "index": ALL}, "key"),
    Input({"type": "rollmed_param", "index": ALL}, "value"),
)
def toggle_rollmed_options(rollmed_opt, rollmed_keys, rollmed_values):
    """Toggle rolling median background correction options with rolling
    median switch, selected options will be cached"""
    rollmed_params = {k: v for k, v in zip(rollmed_keys, rollmed_values)}
    if rollmed_opt:
        return {rollmed_opt[0]: rollmed_params}, {"display": "block"}
    return None, {"display": "none"}


@callback(
    Output("cache_sparsemed_params", "data"),
    Output("sparsemed_options", "style"),
    Input("sparsemed_id", "value"),
    Input({"type": "sparsemed_param", "index": ALL}, "key"),
    Input({"type": "sparsemed_param", "index": ALL}, "value"),
)
def toggle_sparsemed_options(sparsemed_opt, sparsemed_keys, sparsemed_values):
    """Toggle sparse median background correction options with sparse
    median switch, selected options will be cached"""
    sparsemed_params = {k: v for k, v in zip(sparsemed_keys, sparsemed_values)}
    if sparsemed_opt:
        return {sparsemed_opt[0]: sparsemed_params}, {"display": "block"}
    return None, {"display": "none"}


@callback(
    Output("cache_norm_gate_params", "data"),
    Output("norm_gate_options", "style"),
    Input("norm_gate_id", "value"),
    Input({"type": "norm_gate_param", "index": ALL}, "key"),
    Input({"type": "norm_gate_param", "index": ALL}, "value"),
)
def toggle_norm_gate_options(ngate_opt, ngate_keys, ngate_values):
    """Toggle norm gating options with norm gating switch, selected options
    will be cached"""
    norm_gate_params = {k: v for k, v in zip(ngate_keys, ngate_values)}
    if ngate_opt:
        return {ngate_opt[0]: norm_gate_params}, {"display": "block"}
    return None, {"display": "none"}


@callback(
    Output("cache_advanced_template", "data"),
    Input("advanced_title_drop", "value"),
    Input("advanced_title_text", "value"),
    # Direct options
    Input("reproduce_flag", "value"),
    Input("classifier_name", "value"),
    Input("advanced_post_analysis_flag", "value"),
    # Cached options
    Input("cache_advanced_unet_model_path", "data"),
    Input("cache_legacy_params", "data"),
    Input("cache_watershed_params", "data"),
    Input("cache_std_params", "data"),
    Input("cache_rollmed_params", "data"),
    Input("cache_sparsemed_params", "data"),
    Input("cache_norm_gate_params", "data"),
    # Data to process
    Input("show_grid", "selectedRows")
)
def collect_advanced_pipeline_params(
        author_name, advanced_title,
        reproduce_flag, classifier_name, post_analysis_flag,
        cached_unet_model_path, cached_legacy_params,
        cache_watershed_params,
        cache_std_params, cache_rollmed_params, cache_sparsemed_params,
        cache_norm_gate_params,
        selected_rows
):
    """
    Collects all the user-selected and cached parameters to update
    the advanced issue template. The updated template will be cached.
    """
    # Combine params from direct options
    direct_params = [reproduce_flag, classifier_name, post_analysis_flag]
    params_list = [item for sublist in direct_params if sublist for item in
                   sublist]
    params_dict = {param: {} for param in params_list}

    # Combine params from cached options
    cached_params = [
        cached_unet_model_path, cached_legacy_params,
        cache_watershed_params,
        cache_std_params, cache_rollmed_params, cache_sparsemed_params,
        cache_norm_gate_params
    ]
    for param in cached_params:
        if param:
            params_dict.update(param)

    # Extract file paths from selected rows
    rtdc_files = [s["filepath"] for s in selected_rows] \
        if selected_rows else []

    # Update the template if required fields are provided
    if author_name and advanced_title and rtdc_files:
        pipeline_template = {"title": advanced_title}
        description = update_advanced_template(
            params_dict, author_name, rtdc_files, get_advanced_template()
        )
        pipeline_template["description"] = description
        return pipeline_template

    return None


@callback(
    Output("advanced_popup", "is_open"),
    Input("create_advanced_pipeline_button", "n_clicks"),
    Input("cache_advanced_template", "data"),
    Input("advanced_popup_close", "n_clicks"),
    State("advanced_popup", "is_open")
)
def advanced_request_submission_popup(_, cached_adv_temp, close_popup, popup):
    """Show a popup when user clicks on create pipeline button. Then, user
    is asked to close the popup. When user closes page will be refreshed"""
    request_gitlab, _ = get_gitlab_instances()
    button_trigger = [p["prop_id"] for p in cc.triggered][0]
    if "create_advanced_pipeline_button" in button_trigger and cached_adv_temp:
        request_gitlab.run_pipeline(cached_adv_temp)
        return not popup
    if close_popup:
        return not popup
    return popup


@callback(
    Output("create_advanced_pipeline_button", "disabled"),
    Input("advanced_title_drop", "value"),
    Input("advanced_title_text", "value"),
    Input("show_grid", "selectedRows"),
    Input("cache_advanced_unet_model_path", "data"),
    Input("cache_legacy_params", "data"),
    Input("cache_watershed_params", "data"),
    Input("cache_std_params", "data"),
)
def toggle_advanced_create_pipeline_button(author_name, title, selected_files,
                                           cached_unet_model_path,
                                           cached_legacy_params,
                                           cache_watershed_params,
                                           cache_std_params):
    """Activates create pipeline button only when author name, title,
    data files, and segmentation method are entered"""
    if author_name and title and title.strip() and selected_files:
        if cached_unet_model_path or cached_legacy_params or \
                cache_watershed_params or cache_std_params:
            return False
    return True
