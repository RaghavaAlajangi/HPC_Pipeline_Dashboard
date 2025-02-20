import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import ALL, Input, Output, State, callback
from dash import callback_context as cc
from dash import dcc, html
from dash_iconify import DashIconify

from ..gitlab import get_gitlab_instances
from .common_components import (
    checklist_comp,
    divider_line_comp,
    form_group_dropdown,
    form_group_input,
    group_accordion,
    header_comp,
    hover_card,
    line_breaks,
    popup_comp,
)
from .common_sections import (
    cell_classifier_section,
    further_options_section,
    input_data_display_section,
    input_data_selection_section,
    title_section,
    unet_segmentation_options,
    unet_segmentation_section,
)
from .utils import update_advanced_template

DEFAULTS_FILE = (
    "https://gitlab.gwdg.de/blood_data_analysis/hpc_pipeline_"
    "requests/-/blob/main/dashboard_dcevent_defaults.yaml"
)


def get_advanced_template():
    """Fetch the advanced request template from request repo"""
    request_gitlab, _ = get_gitlab_instances()
    return request_gitlab.get_request_template(temp_type="advanced")


def advanced_segmentation_section():
    # Get the default parameters from request repo
    request_gitlab, _ = get_gitlab_instances()
    dcevent_params = request_gitlab.get_defaults()
    legacy_seg = dcevent_params["legacy"]
    thresh_seg = dcevent_params["thresh"]
    watershed_seg = dcevent_params["watershed"]
    std_seg = dcevent_params["std"]
    return dbc.AccordionItem(
        title="Segmentation Algorithm",
        children=[
            # MLUNet segmentor section
            unet_segmentation_section(
                unet_switch_id="advanced_unet_switch",
                unet_toggle_id="advanced_unet_options",
                unet_options_id="advanced_measure_type",
            ),
            divider_line_comp(),
            # Legacy segmentor section
            dmc.Group(
                children=[
                    # Legacy checkbox (switch)
                    checklist_comp(
                        comp_id="legacy_id",
                        options=[
                            {
                                "label": "legacy: Legacy thresholding "
                                "with OpenCV",
                                "value": "legacy: Legacy thresholding "
                                "with OpenCV",
                                "disabled": False,
                            }
                        ],
                    ),
                    # Legacy question mark icon and hover info
                    hover_card(
                        target=DashIconify(
                            icon="mage:message-question-mark-round-fill",
                            color="yellow",
                            width=20,
                        ),
                        notes="ShapeIN-equivalent thresholding segmentation",
                    ),
                ],
                spacing=5,
            ),
            # Legacy segmentor options
            html.Ul(
                id="legacy_options",
                children=[
                    form_group_input(
                        comp_id={"type": "legacy_param", "index": 1},
                        label="Threshold Value",
                        label_key="thresh",
                        min=legacy_seg["thresh"]["min"],
                        max=legacy_seg["thresh"]["max"],
                        step=legacy_seg["thresh"]["step"],
                        default=legacy_seg["thresh"]["default"],
                    ),
                    form_group_input(
                        comp_id={"type": "legacy_param", "index": 2},
                        label="blur",
                        label_key="blur",
                        min=legacy_seg["blur"]["min"],
                        max=legacy_seg["blur"]["max"],
                        step=legacy_seg["blur"]["step"],
                        default=legacy_seg["blur"]["default"],
                    ),
                    form_group_input(
                        comp_id={"type": "legacy_param", "index": 3},
                        label="binaryops",
                        label_key="binaryops",
                        min=legacy_seg["binaryops"]["min"],
                        max=legacy_seg["binaryops"]["max"],
                        step=legacy_seg["binaryops"]["step"],
                        default=legacy_seg["binaryops"]["default"],
                    ),
                    form_group_dropdown(
                        comp_id={"type": "legacy_param", "index": 4},
                        label="diff_method",
                        label_key="diff_method",
                        options=legacy_seg["diff_method"]["options"],
                        default=legacy_seg["diff_method"]["default"],
                    ),
                    form_group_dropdown(
                        comp_id={"type": "legacy_param", "index": 5},
                        label="clear_border",
                        label_key="clear_border",
                        options=legacy_seg["clear_border"]["options"],
                        default=legacy_seg["clear_border"]["default"],
                    ),
                    form_group_dropdown(
                        comp_id={"type": "legacy_param", "index": 6},
                        label="fill_holes",
                        label_key="fill_holes",
                        options=legacy_seg["fill_holes"]["options"],
                        default=legacy_seg["fill_holes"]["default"],
                    ),
                    form_group_input(
                        comp_id={"type": "legacy_param", "index": 7},
                        label="closing_disk",
                        label_key="closing_disk",
                        min=legacy_seg["closing_disk"]["min"],
                        max=legacy_seg["closing_disk"]["max"],
                        step=legacy_seg["closing_disk"]["step"],
                        default=legacy_seg["closing_disk"]["default"],
                    ),
                ],
            ),
            divider_line_comp(),
            # Thresholding segmentor section
            dmc.Group(
                children=[
                    # Thresh segmentor checkbox (switch)
                    checklist_comp(
                        comp_id="thresh_seg_id",
                        options=[
                            {
                                "label": "thresh: thresholding segmentation",
                                "value": "thresh: thresholding segmentation",
                                "disabled": False,
                            }
                        ],
                    ),
                    # Thresh question mark icon and hover info
                    hover_card(
                        target=DashIconify(
                            icon="mage:message-question-mark-round-fill",
                            color="yellow",
                            width=20,
                        ),
                        notes="Thresholding based segmentation.",
                    ),
                ],
                spacing=5,
            ),
            # Thresholding segmentor options
            html.Ul(
                id="thresh_seg_options",
                children=[
                    form_group_input(
                        comp_id={"type": "thresh_seg_param", "index": 1},
                        label="Threshold Value",
                        label_key="thresh",
                        min=thresh_seg["thresh"]["min"],
                        max=thresh_seg["thresh"]["max"],
                        step=thresh_seg["thresh"]["step"],
                        default=thresh_seg["thresh"]["default"],
                    ),
                    form_group_dropdown(
                        comp_id={"type": "thresh_seg_param", "index": 5},
                        label="clear_border",
                        label_key="clear_border",
                        options=thresh_seg["clear_border"]["options"],
                        default=thresh_seg["clear_border"]["default"],
                    ),
                    form_group_dropdown(
                        comp_id={"type": "thresh_seg_param", "index": 6},
                        label="fill_holes",
                        label_key="fill_holes",
                        options=thresh_seg["fill_holes"]["options"],
                        default=thresh_seg["fill_holes"]["default"],
                    ),
                    form_group_input(
                        comp_id={"type": "thresh_seg_param", "index": 7},
                        label="closing_disk",
                        label_key="closing_disk",
                        min=thresh_seg["closing_disk"]["min"],
                        max=thresh_seg["closing_disk"]["max"],
                        step=thresh_seg["closing_disk"]["step"],
                        default=thresh_seg["closing_disk"]["default"],
                    ),
                ],
            ),
            divider_line_comp(),
            checklist_comp(
                comp_id="watershed_id",
                options=[
                    {
                        "label": "watershed: Watershed algorithm",
                        "value": "watershed: Watershed algorithm",
                        "disabled": False,
                    }
                ],
            ),
            html.Ul(
                id="watershed_options",
                children=[
                    form_group_dropdown(
                        comp_id={"type": "watershed_param", "index": 1},
                        label="clear_border",
                        label_key="clear_border",
                        options=watershed_seg["clear_border"]["options"],
                        default=watershed_seg["clear_border"]["default"],
                    ),
                    form_group_dropdown(
                        comp_id={"type": "watershed_param", "index": 2},
                        label="fill_holes",
                        label_key="fill_holes",
                        options=watershed_seg["fill_holes"]["options"],
                        default=watershed_seg["fill_holes"]["default"],
                    ),
                    form_group_input(
                        comp_id={"type": "watershed_param", "index": 3},
                        label="closing_disk",
                        label_key="closing_disk",
                        min=watershed_seg["closing_disk"]["min"],
                        max=watershed_seg["closing_disk"]["max"],
                        step=watershed_seg["closing_disk"]["step"],
                        default=watershed_seg["closing_disk"]["default"],
                    ),
                ],
            ),
            divider_line_comp(),
            # STD segmentor section
            checklist_comp(
                comp_id="std_id",
                options=[
                    {
                        "label": "std: Standard-deviation-"
                        "based thresholding",
                        "value": "std: Standard-deviation-"
                        "based thresholding",
                        "disabled": False,
                    }
                ],
            ),
            html.Ul(
                id="std_options",
                children=[
                    form_group_dropdown(
                        comp_id={"type": "std_param", "index": 1},
                        label="clear_border",
                        label_key="clear_border",
                        options=std_seg["clear_border"]["options"],
                        default=std_seg["clear_border"]["default"],
                    ),
                    form_group_dropdown(
                        comp_id={"type": "std_param", "index": 2},
                        label="fill_holes",
                        label_key="fill_holes",
                        options=std_seg["fill_holes"]["options"],
                        default=std_seg["fill_holes"]["default"],
                    ),
                    form_group_input(
                        comp_id={"type": "std_param", "index": 3},
                        label="closing_disk",
                        label_key="closing_disk",
                        min=std_seg["closing_disk"]["min"],
                        max=std_seg["closing_disk"]["max"],
                        step=std_seg["closing_disk"]["step"],
                        default=std_seg["closing_disk"]["default"],
                    ),
                ],
            ),
        ],
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
                options=[
                    {
                        "label": "rollmed: Rolling median RT-DC background "
                        "image computation",
                        "value": "rollmed: Rolling median RT-DC background "
                        "image computation",
                        "disabled": False,
                    }
                ],
            ),
            html.Ul(
                id="rollmed_options",
                children=[
                    form_group_input(
                        comp_id={"type": "rollmed_param", "index": 1},
                        label="kernel_size",
                        label_key="kernel_size",
                        min=rollmed_bg["kernel_size"]["min"],
                        max=rollmed_bg["kernel_size"]["max"],
                        step=rollmed_bg["kernel_size"]["step"],
                        default=rollmed_bg["kernel_size"]["default"],
                    ),
                    form_group_input(
                        comp_id={"type": "rollmed_param", "index": 2},
                        label="batch_size",
                        label_key="batch_size",
                        min=rollmed_bg["batch_size"]["min"],
                        max=rollmed_bg["batch_size"]["max"],
                        step=rollmed_bg["batch_size"]["step"],
                        default=rollmed_bg["batch_size"]["default"],
                    ),
                ],
            ),
            divider_line_comp(),
            checklist_comp(
                comp_id="sparsemed_id",
                options=[
                    {
                        "label": "sparsemed: Sparse median background "
                        "correction with cleansing",
                        "value": "sparsemed: Sparse median background "
                        "correction with cleansing",
                        "disabled": False,
                    }
                ],
                defaults=[
                    "sparsemed: Sparse median background correction with "
                    "cleansing"
                ],
            ),
            html.Ul(
                id="sparsemed_options",
                children=[
                    form_group_input(
                        comp_id={"type": "sparsemed_param", "index": 1},
                        label="kernel_size",
                        label_key="kernel_size",
                        min=sparsemed_bg["kernel_size"]["min"],
                        max=sparsemed_bg["kernel_size"]["max"],
                        step=sparsemed_bg["kernel_size"]["step"],
                        default=sparsemed_bg["kernel_size"]["default"],
                    ),
                    form_group_input(
                        comp_id={"type": "sparsemed_param", "index": 2},
                        label="split_time",
                        label_key="split_time",
                        min=sparsemed_bg["split_time"]["min"],
                        max=sparsemed_bg["split_time"]["max"],
                        step=sparsemed_bg["split_time"]["step"],
                        default=sparsemed_bg["split_time"]["default"],
                    ),
                    form_group_input(
                        comp_id={"type": "sparsemed_param", "index": 3},
                        label="thresh_cleansing",
                        label_key="thresh_cleansing",
                        min=sparsemed_bg["thresh_cleansing"]["min"],
                        max=sparsemed_bg["thresh_cleansing"]["max"],
                        step=sparsemed_bg["thresh_cleansing"]["step"],
                        default=sparsemed_bg["thresh_cleansing"]["default"],
                    ),
                    form_group_input(
                        comp_id={"type": "sparsemed_param", "index": 4},
                        label="frac_cleansing",
                        label_key="frac_cleansing",
                        min=sparsemed_bg["frac_cleansing"]["min"],
                        max=sparsemed_bg["frac_cleansing"]["max"],
                        step=sparsemed_bg["frac_cleansing"]["step"],
                        default=sparsemed_bg["frac_cleansing"]["default"],
                    ),
                    form_group_dropdown(
                        comp_id={"type": "sparsemed_param", "index": 5},
                        label="offset_correction",
                        label_key="offset_correction",
                        options=sparsemed_bg["offset_correction"]["options"],
                        default=sparsemed_bg["offset_correction"]["default"],
                    ),
                ],
            ),
        ],
    )


def gating_options_section():
    # Get the default parameters from request repo
    request_gitlab, _ = get_gitlab_instances()
    dcevent_params = request_gitlab.get_defaults()
    norm_gate = dcevent_params["norm_gate"]
    return dbc.AccordionItem(
        title="Available gating options",
        children=[
            checklist_comp(
                comp_id="norm_gate_id",
                options=[
                    {
                        "label": "norm gating",
                        "value": "norm gating",
                        "disabled": False,
                    }
                ],
            ),
            html.Ul(
                id="norm_gate_options",
                children=[
                    form_group_dropdown(
                        comp_id={"type": "norm_gate_param", "index": 1},
                        label="online_gates",
                        label_key="online_gates",
                        options=norm_gate["online_gates"]["options"],
                        default=norm_gate["online_gates"]["default"],
                    ),
                    form_group_input(
                        comp_id={"type": "norm_gate_param", "index": 2},
                        label="size_thresh_mask",
                        label_key="size_thresh_mask",
                        min=norm_gate["size_thresh_mask"]["min"],
                        max=norm_gate["size_thresh_mask"]["max"],
                        step=norm_gate["size_thresh_mask"]["step"],
                        default=norm_gate["size_thresh_mask"]["default"],
                    ),
                ],
            ),
        ],
    )


def advanced_page_layout(refresh_path):
    """Creates advanced request page"""
    return dbc.Toast(
        id="advanced_request_toast",
        header="Advanced Pipeline Request",
        header_style={
            "background-color": "#017b70",
            "font-size": "25px",
            "color": "white",
        },
        is_open=True,
        className="my-toast",
        children=[
            popup_comp(
                comp_id="advanced_popup",
                refresh_path=refresh_path,
                text="Pipeline request has been submitted!",
            ),
            line_breaks(times=1),
            header_comp(
                "⦿ Pipeline for segmentation and/or classification "
                "(prediction) and analysis of data.",
                indent=40,
            ),
            line_breaks(times=1),
            header_comp(
                "⦿ Choosing multiple Segmentation or Prediction "
                "algorithms will create a matrix of jobs "
                "(multiple jobs).",
                indent=40,
            ),
            line_breaks(times=1),
            dbc.Alert(
                children=[
                    # Warning icon
                    html.I(className="bi bi-info-circle-fill me-2"),
                    dcc.Markdown(
                        f"To adjust the default segmentation and background "
                        f"method parameters, visit the [Request Repository]"
                        f"({DEFAULTS_FILE}) and modify the desired settings. "
                        f"Your changes will be immediately reflected on the "
                        f"dashboard."
                    ),
                ],
                className="d-flex align-items-inline",
                color="info",
                style={
                    "color": "black",
                    "width": "fit-content",
                    "marginLeft": "40px",
                    "height": "60px",
                },
            ),
            line_breaks(times=2),
            group_accordion(
                children=[
                    title_section(
                        dropdown_id="advanced_title_drop",
                        text_id="advanced_title_text",
                    ),
                    advanced_segmentation_section(),
                    background_correction_section(),
                    gating_options_section(),
                    further_options_section(
                        reproduce_flag_id="advanced_reproduce_flag",
                        num_frames_id="advanced_num_frames_switch",
                        num_frames_toggle_id="advanced_num_frames_options",
                        num_frames_value="advanced_num_frames_value",
                    ),
                    cell_classifier_section(classifier_id="classifier_name"),
                    input_data_selection_section(),
                ],
                middle=True,
                open_first=True,
                comp_id="pipeline_accord",
            ),
            input_data_display_section(
                show_grid_id="show_grid",
                button_id="create_advanced_pipeline_button",
            ),
            dcc.Store(id="cache_advanced_template", storage_type="local"),
            dcc.Store(
                id="cache_advanced_unet_model_path", storage_type="local"
            ),
            dcc.Store(id="cache_legacy_params", storage_type="local"),
            dcc.Store(id="cache_thresh_seg_params", storage_type="local"),
            dcc.Store(id="cache_watershed_params", storage_type="local"),
            dcc.Store(id="cache_std_params", storage_type="local"),
            dcc.Store(id="cache_rollmed_params", storage_type="local"),
            dcc.Store(id="cache_sparsemed_params", storage_type="local"),
            dcc.Store(id="cache_norm_gate_params", storage_type="local"),
            dcc.Store(id="cache_advanced_num_frames", storage_type="local"),
        ],
    )


@callback(
    Output("advanced_measure_type", "children"),
    Output("cache_advanced_unet_model_path", "data"),
    Input("advanced_unet_switch", "value"),
    Input("advanced_measure_type", "value"),
)
def show_and_cache_unet_model_meta(unet_click, measure_option):
    """This circular callback fetches unet model metadata from the DVC repo
    and shows it as dmc.RadioGroup options, enable the user to select the
    appropriate options from the same dmc.RadioItem options."""

    _, dvc_gitlab = get_gitlab_instances()

    model_dict = dvc_gitlab.get_model_metadata()
    check_boxes = unet_segmentation_options(model_dict)

    segm_options = {}
    if unet_click and measure_option:
        segm_options[unet_click[0]] = {"model_file": measure_option}
    return check_boxes, segm_options


@callback(
    Output("advanced_unet_options", "style"),
    Input("advanced_unet_switch", "value"),
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
    return {}, {"display": "none"}


@callback(
    Output("cache_thresh_seg_params", "data"),
    Output("thresh_seg_options", "style"),
    Input("thresh_seg_id", "value"),
    Input({"type": "thresh_seg_param", "index": ALL}, "key"),
    Input({"type": "thresh_seg_param", "index": ALL}, "value"),
)
def toggle_thresh_seg_options(
    thresh_seg_opt, thresh_seg_keys, thresh_seg_values
):
    """Toggle thresholding segmentation options with thresh switch, selected
    options will be cached"""
    thresh_seg_params = {
        k: v for k, v in zip(thresh_seg_keys, thresh_seg_values)
    }

    if thresh_seg_opt:
        return {thresh_seg_opt[0]: thresh_seg_params}, {"display": "block"}
    return {}, {"display": "none"}


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
    return {}, {"display": "none"}


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
    return {}, {"display": "none"}


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
    return {}, {"display": "none"}


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
    return {}, {"display": "none"}


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
    return {}, {"display": "none"}


@callback(
    Output("cache_advanced_num_frames", "data"),
    Output("advanced_num_frames_options", "style"),
    Input("advanced_num_frames_switch", "value"),
    Input("advanced_num_frames_value", "key"),
    Input("advanced_num_frames_value", "value"),
)
def toggle_simple_num_frames_options(
    num_frames_click, num_frames_key, num_frames_value
):
    """Toggle num_frames options with num_frames switch"""
    if num_frames_click:
        return {num_frames_key: num_frames_value}, {"display": "block"}
    return {}, {"display": "none"}


@callback(
    Output("cache_advanced_template", "data"),
    Input("advanced_title_drop", "value"),
    Input("advanced_title_text", "value"),
    # Direct options
    Input("advanced_reproduce_flag", "value"),
    Input("classifier_name", "value"),
    # Cached options
    Input("cache_advanced_unet_model_path", "data"),
    Input("cache_legacy_params", "data"),
    Input("cache_thresh_seg_params", "data"),
    Input("cache_watershed_params", "data"),
    Input("cache_std_params", "data"),
    Input("cache_rollmed_params", "data"),
    Input("cache_sparsemed_params", "data"),
    Input("cache_norm_gate_params", "data"),
    Input("cache_advanced_num_frames", "data"),
    # Data to process
    Input("show_grid", "selectedRows"),
)
def collect_advanced_pipeline_params(
    author_name,
    advanced_title,
    reproduce_flag,
    classifier_name,
    cache_unet_model_path,
    cache_legacy_params,
    cache_thresh_seg_params,
    cache_watershed_params,
    cache_std_params,
    cache_rollmed_params,
    cache_sparsemed_params,
    cache_norm_gate_params,
    cache_num_frames,
    selected_rows,
):
    """
    Collects all the user-selected and cached parameters to update
    the advanced issue template. The updated template will be cached.
    """
    # Initialize the params dictionary with empty dictionaries
    params_dict = {
        param: None for param in [*classifier_name, *reproduce_flag]
    }

    # Combine params from cached options
    # cached_params = [
    #     cache_unet_model_path,
    #     cache_legacy_params,
    #     cache_thresh_seg_params,
    #     cache_watershed_params,
    #     cache_std_params,
    #     cache_rollmed_params,
    #     cache_sparsemed_params,
    #     cache_norm_gate_params,
    #     cache_num_frames,
    # ]

    # Update params_dict with non-empty cached params
    # params_dict.update(
    #     {k: v for param in cached_params if param for k, v in param.items()}
    # )

    # Merge parameter dicts
    params_dict = {
        **params_dict,
        **cache_unet_model_path,
        **cache_legacy_params,
        **cache_thresh_seg_params,
        **cache_watershed_params,
        **cache_std_params,
        **cache_rollmed_params,
        **cache_sparsemed_params,
        **cache_norm_gate_params,
        **cache_num_frames,
    }

    # Extract file paths from selected rows
    rtdc_files = (
        [s["filepath"] for s in selected_rows] if selected_rows else []
    )

    # Update the template if required fields are provided
    if author_name and advanced_title and rtdc_files:
        pipeline_template = {"title": advanced_title}
        description = update_advanced_template(
            params_dict, author_name, rtdc_files, get_advanced_template()
        )
        pipeline_template["description"] = description
        import pprint

        pprint.pprint(pipeline_template)
        return pipeline_template

    return None


@callback(
    Output("advanced_popup", "is_open"),
    Input("create_advanced_pipeline_button", "n_clicks"),
    Input("cache_advanced_template", "data"),
    Input("advanced_popup_close", "n_clicks"),
    State("advanced_popup", "is_open"),
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
    Input("cache_thresh_seg_params", "data"),
    Input("cache_watershed_params", "data"),
    Input("cache_std_params", "data"),
)
def toggle_advanced_create_pipeline_button(
    author_name,
    title,
    selected_files,
    cached_unet_model_path,
    cached_legacy_params,
    cache_thresh_seg_params,
    cache_watershed_params,
    cache_std_params,
):
    """Activates create pipeline button only when author name, title,
    data files, and segmentation method are entered"""
    if author_name and title and title.strip() and selected_files:
        if (
            cached_unet_model_path
            or cached_legacy_params
            or cache_thresh_seg_params
            or cache_watershed_params
            or cache_std_params
        ):
            return False
    return True
