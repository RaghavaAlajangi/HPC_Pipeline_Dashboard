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
    format_params,
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
    water_seg = dcevent_params["watershed"]
    std_seg = dcevent_params["std"]
    return dbc.AccordionItem(
        title="Segmentation Algorithm",
        children=[
            # MLUNet segmentor section
            unet_segmentation_section(
                unet_switch_id="advance_unet_click",
                unet_toggle_id="advance_unet_toggle",
                unet_options_id="advance_unet_model",
            ),
            divider_line_comp(),
            # Legacy segmentor section
            dmc.Group(
                children=[
                    # Legacy checkbox (switch)
                    checklist_comp(
                        comp_id="legacy_click",
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
                id="legacy_toggle",
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
                        comp_id="thresh_click",
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
                id="thresh_toggle",
                children=[
                    form_group_input(
                        comp_id={"type": "thresh_param", "index": 1},
                        label="Threshold Value",
                        label_key="thresh",
                        min=thresh_seg["thresh"]["min"],
                        max=thresh_seg["thresh"]["max"],
                        step=thresh_seg["thresh"]["step"],
                        default=thresh_seg["thresh"]["default"],
                    ),
                    form_group_dropdown(
                        comp_id={"type": "thresh_param", "index": 5},
                        label="clear_border",
                        label_key="clear_border",
                        options=thresh_seg["clear_border"]["options"],
                        default=thresh_seg["clear_border"]["default"],
                    ),
                    form_group_dropdown(
                        comp_id={"type": "thresh_param", "index": 6},
                        label="fill_holes",
                        label_key="fill_holes",
                        options=thresh_seg["fill_holes"]["options"],
                        default=thresh_seg["fill_holes"]["default"],
                    ),
                    form_group_input(
                        comp_id={"type": "thresh_param", "index": 7},
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
                comp_id="water_click",
                options=[
                    {
                        "label": "watershed: Watershed algorithm",
                        "value": "watershed: Watershed algorithm",
                        "disabled": False,
                    }
                ],
            ),
            html.Ul(
                id="water_toggle",
                children=[
                    form_group_dropdown(
                        comp_id={"type": "water_param", "index": 1},
                        label="clear_border",
                        label_key="clear_border",
                        options=water_seg["clear_border"]["options"],
                        default=water_seg["clear_border"]["default"],
                    ),
                    form_group_dropdown(
                        comp_id={"type": "water_param", "index": 2},
                        label="fill_holes",
                        label_key="fill_holes",
                        options=water_seg["fill_holes"]["options"],
                        default=water_seg["fill_holes"]["default"],
                    ),
                    form_group_input(
                        comp_id={"type": "water_param", "index": 3},
                        label="closing_disk",
                        label_key="closing_disk",
                        min=water_seg["closing_disk"]["min"],
                        max=water_seg["closing_disk"]["max"],
                        step=water_seg["closing_disk"]["step"],
                        default=water_seg["closing_disk"]["default"],
                    ),
                ],
            ),
            divider_line_comp(),
            # STD segmentor section
            checklist_comp(
                comp_id="std_click",
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
                id="std_toggle",
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
    romed_bg = dcevent_params["rollmed"]
    spmed_bg = dcevent_params["sparsemed"]
    return dbc.AccordionItem(
        title="Background Correction / Subtraction Method",
        children=[
            checklist_comp(
                comp_id="romed_click",
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
                id="romed_toggle",
                children=[
                    form_group_input(
                        comp_id={"type": "romed_param", "index": 1},
                        label="kernel_size",
                        label_key="kernel_size",
                        min=romed_bg["kernel_size"]["min"],
                        max=romed_bg["kernel_size"]["max"],
                        step=romed_bg["kernel_size"]["step"],
                        default=romed_bg["kernel_size"]["default"],
                    ),
                    form_group_input(
                        comp_id={"type": "romed_param", "index": 2},
                        label="batch_size",
                        label_key="batch_size",
                        min=romed_bg["batch_size"]["min"],
                        max=romed_bg["batch_size"]["max"],
                        step=romed_bg["batch_size"]["step"],
                        default=romed_bg["batch_size"]["default"],
                    ),
                ],
            ),
            divider_line_comp(),
            checklist_comp(
                comp_id="spmed_click",
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
                id="spmed_toggle",
                children=[
                    form_group_input(
                        comp_id={"type": "spmed_param", "index": 1},
                        label="kernel_size",
                        label_key="kernel_size",
                        min=spmed_bg["kernel_size"]["min"],
                        max=spmed_bg["kernel_size"]["max"],
                        step=spmed_bg["kernel_size"]["step"],
                        default=spmed_bg["kernel_size"]["default"],
                    ),
                    form_group_input(
                        comp_id={"type": "spmed_param", "index": 2},
                        label="split_time",
                        label_key="split_time",
                        min=spmed_bg["split_time"]["min"],
                        max=spmed_bg["split_time"]["max"],
                        step=spmed_bg["split_time"]["step"],
                        default=spmed_bg["split_time"]["default"],
                    ),
                    form_group_input(
                        comp_id={"type": "spmed_param", "index": 3},
                        label="thresh_cleansing",
                        label_key="thresh_cleansing",
                        min=spmed_bg["thresh_cleansing"]["min"],
                        max=spmed_bg["thresh_cleansing"]["max"],
                        step=spmed_bg["thresh_cleansing"]["step"],
                        default=spmed_bg["thresh_cleansing"]["default"],
                    ),
                    form_group_input(
                        comp_id={"type": "spmed_param", "index": 4},
                        label="frac_cleansing",
                        label_key="frac_cleansing",
                        min=spmed_bg["frac_cleansing"]["min"],
                        max=spmed_bg["frac_cleansing"]["max"],
                        step=spmed_bg["frac_cleansing"]["step"],
                        default=spmed_bg["frac_cleansing"]["default"],
                    ),
                    form_group_dropdown(
                        comp_id={"type": "spmed_param", "index": 5},
                        label="offset_correction",
                        label_key="offset_correction",
                        options=spmed_bg["offset_correction"]["options"],
                        default=spmed_bg["offset_correction"]["default"],
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
                comp_id="ngate_click",
                options=[
                    {
                        "label": "norm gating",
                        "value": "norm gating",
                        "disabled": False,
                    }
                ],
            ),
            html.Ul(
                id="ngate_toggle",
                children=[
                    form_group_dropdown(
                        comp_id={"type": "ngate_param", "index": 1},
                        label="online_gates",
                        label_key="online_gates",
                        options=norm_gate["online_gates"]["options"],
                        default=norm_gate["online_gates"]["default"],
                    ),
                    form_group_input(
                        comp_id={"type": "ngate_param", "index": 2},
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
        id="advance_request_toast",
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
                comp_id="advance_popup",
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
                        dropdown_id="title_drop",
                        text_id="title_text",
                    ),
                    advanced_segmentation_section(),
                    background_correction_section(),
                    gating_options_section(),
                    further_options_section(
                        reproduce_flag_id="reproduce_click",
                        num_frames_id="advance_nframe_click",
                        num_frames_toggle_id="advance_nframe_toggle",
                        num_frames_value="advance_nframe_value",
                    ),
                    cell_classifier_section(classifier_id="classifier_click"),
                    input_data_selection_section(),
                ],
                middle=True,
                open_first=True,
                comp_id="pipeline_accord",
            ),
            input_data_display_section(
                show_grid_id="show_grid",
                button_id="advance_create_pipeline_click",
            ),
            dcc.Store(id="cache_advance_template"),
            dcc.Store(id="cache_advance_params", data={}),
        ],
    )


@callback(
    Output("advance_unet_model", "children"),
    Input("advance_unet_click", "value"),
)
def fetch_and_show_unet_models(unet_click):
    """This circular callback fetches unet model metadata from the
    DVC repo and shows it as dmc.RadioGroup options, enable the user
    to select the appropriate options from the same dmc.RadioItem
    options."""

    _, dvc_gitlab = get_gitlab_instances()

    model_dict = dvc_gitlab.get_model_metadata()
    check_boxes = unet_segmentation_options(model_dict)

    return check_boxes


@callback(
    Output("cache_advance_params", "data"),
    Output("advance_unet_toggle", "style"),
    Output("legacy_toggle", "style"),
    Output("thresh_toggle", "style"),
    Output("water_toggle", "style"),
    Output("std_toggle", "style"),
    Output("romed_toggle", "style"),
    Output("spmed_toggle", "style"),
    Output("ngate_toggle", "style"),
    Output("advance_nframe_toggle", "style"),
    # Unet inputs
    Input("advance_unet_click", "value"),
    Input("advance_unet_model", "value"),
    # Legacy inputs
    Input("legacy_click", "value"),
    Input({"type": "legacy_param", "index": ALL}, "key"),
    Input({"type": "legacy_param", "index": ALL}, "value"),
    # Thesh inputs
    Input("thresh_click", "value"),
    Input({"type": "thresh_param", "index": ALL}, "key"),
    Input({"type": "thresh_param", "index": ALL}, "value"),
    # Watershed inputs
    Input("water_click", "value"),
    Input({"type": "water_param", "index": ALL}, "key"),
    Input({"type": "water_param", "index": ALL}, "value"),
    # STD inputs
    Input("std_click", "value"),
    Input({"type": "std_param", "index": ALL}, "key"),
    Input({"type": "std_param", "index": ALL}, "value"),
    # Rolling median bg inputs
    Input("romed_click", "value"),
    Input({"type": "romed_param", "index": ALL}, "key"),
    Input({"type": "romed_param", "index": ALL}, "value"),
    # Sparse median bg inputs
    Input("spmed_click", "value"),
    Input({"type": "spmed_param", "index": ALL}, "key"),
    Input({"type": "spmed_param", "index": ALL}, "value"),
    # Norm gate inputs
    Input("ngate_click", "value"),
    Input({"type": "ngate_param", "index": ALL}, "key"),
    Input({"type": "ngate_param", "index": ALL}, "value"),
    # bloody bunny input
    Input("classifier_click", "value"),
    # reproduce flag input
    Input("reproduce_click", "value"),
    # num frames inputs
    Input("advance_nframe_click", "value"),
    Input("advance_nframe_value", "value"),
)
def toggle_and_cache_params(
    unet_click,
    unet_value,
    legacy_click,
    leg_keys,
    leg_values,
    thresh_click,
    thresh_keys,
    thresh_values,
    water_click,
    water_keys,
    water_values,
    std_click,
    std_keys,
    std_values,
    romed_click,
    romed_keys,
    romed_values,
    spmed_click,
    spmed_keys,
    spmed_values,
    ngate_click,
    ngate_keys,
    ngate_values,
    classifier_click,
    reproduce_click,
    nframe_click,
    nframe_value,
):
    """Consolidated callback for toggling and caching parameters"""

    cache_data = {
        **format_params(
            unet_click, [unet_value if unet_value else ""], ["model_file"]
        ),
        **format_params(legacy_click, leg_values, leg_keys),
        **format_params(thresh_click, thresh_values, thresh_keys),
        **format_params(water_click, water_values, water_keys),
        **format_params(std_click, std_values, std_keys),
        **format_params(romed_click, romed_values, romed_keys),
        **format_params(spmed_click, spmed_values, spmed_keys),
        **format_params(ngate_click, ngate_values, ngate_keys),
        **format_params(nframe_click, nframe_value),
        **format_params(classifier_click, None),
        **format_params(reproduce_click, None),
    }

    return (
        cache_data,
        {"display": "block"} if unet_click else {"display": "none"},
        {"display": "block"} if legacy_click else {"display": "none"},
        {"display": "block"} if thresh_click else {"display": "none"},
        {"display": "block"} if water_click else {"display": "none"},
        {"display": "block"} if std_click else {"display": "none"},
        {"display": "block"} if romed_click else {"display": "none"},
        {"display": "block"} if spmed_click else {"display": "none"},
        {"display": "block"} if ngate_click else {"display": "none"},
        {"display": "block"} if nframe_click else {"display": "none"},
    )


@callback(
    Output("cache_advance_template", "data"),
    Input("title_drop", "value"),
    Input("title_text", "value"),
    Input("cache_advance_params", "data"),
    Input("show_grid", "selectedRows"),
)
def collect_advanced_pipeline_params(
    author_name,
    advance_title,
    cache_params,
    selected_rows,
):
    """
    Collects all the user-selected and cached parameters to update the
    advanced issue template. The updated template will be cached.
    """
    # Extract file paths from selected rows
    rtdc_files = (
        [s["filepath"] for s in selected_rows] if selected_rows else []
    )
    # Update the template if required fields are provided
    if author_name and advance_title and rtdc_files:
        rtdc_files = [s["filepath"] for s in selected_rows]
        pipeline_template = {"title": advance_title}
        description = update_advanced_template(
            cache_params, author_name, rtdc_files, get_advanced_template()
        )
        pipeline_template["description"] = description

        return pipeline_template

    return None


@callback(
    Output("advance_popup", "is_open"),
    Input("advance_create_pipeline_click", "n_clicks"),
    Input("cache_advance_template", "data"),
    Input("advance_popup_close", "n_clicks"),
    State("advance_popup", "is_open"),
)
def advanced_request_submission_popup(_, cached_adv_temp, close_popup, popup):
    """Show a popup when user clicks on create pipeline button. Then, user
    is asked to close the popup. When user closes page will be refreshed"""
    request_gitlab, _ = get_gitlab_instances()
    button_trigger = [p["prop_id"] for p in cc.triggered][0]
    if "advance_create_pipeline_click" in button_trigger and cached_adv_temp:
        request_gitlab.run_pipeline(cached_adv_temp)
        return not popup
    if close_popup:
        return not popup
    return popup


@callback(
    Output("advance_create_pipeline_click", "disabled"),
    Input("title_drop", "value"),
    Input("title_text", "value"),
    Input("show_grid", "selectedRows"),
    Input("cache_advance_params", "data"),
)
def toggle_advanced_create_pipeline_button(
    author_name,
    title,
    selected_rows,
    cached_params,
):
    """Activates create pipeline button only when author name, title,
    data files, and segmentation method are entered"""
    if author_name and title and title.strip() and selected_rows:
        if cached_params:
            return False
    return True
