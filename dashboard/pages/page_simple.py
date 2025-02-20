import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import Input, Output, State, callback
from dash import callback_context as ctx
from dash import dcc, html, no_update
from dash_iconify import DashIconify

from ..gitlab import get_gitlab_instances
from .common_components import (
    divider_line_comp,
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
from .utils import update_simple_template


def get_simple_template():
    """Fetch the simple request template from request repo"""
    request_gitlab, _ = get_gitlab_instances()
    return request_gitlab.get_request_template(temp_type="simple")


def simple_segmentation_section():
    """Creates the segmentation section of the simple pipeline."""
    # Get the default parameters from request repo
    request_gitlab, _ = get_gitlab_instances()
    dcevent_params = request_gitlab.get_defaults()
    legacy_seg = dcevent_params["legacy"]
    return dbc.AccordionItem(
        title="Segmentation",
        children=[
            # MLUNet segmentor section
            unet_segmentation_section(
                unet_switch_id="simple_unet_switch",
                unet_toggle_id="simple_unet_options",
                unet_options_id="simple_measure_type",
            ),
            divider_line_comp(),
            dmc.Group(
                children=[
                    dbc.Checklist(
                        options=[
                            {
                                "label": "legacy: Legacy thresholding "
                                "with OpenCV",
                                "value": "legacy: Legacy thresholding "
                                "with OpenCV",
                            },
                        ],
                        id="simple_legacy_switch",
                        switch=True,
                        value=[],
                        labelCheckedClassName="text-success",
                        inputCheckedClassName="border-success bg-success",
                    ),
                    hover_card(
                        target=DashIconify(
                            icon="mage:message-question-mark-round-fill",
                            color="yellow",
                            width=20,
                        ),
                        notes="This is a thresholding based segmentation "
                        "same as the segmentation available in shapeIn "
                        "(ZMD device). \n Default threshold value [-6]. "
                        "Tune it according to your use case.",
                    ),
                ],
                align="left",
                spacing=5,
            ),
            html.Ul(
                id="simple_legacy_options",
                children=[
                    form_group_input(
                        comp_id="simple_legacy_thresh_value",
                        label="Threshold Value:",
                        label_key="thresh",
                        min=legacy_seg["thresh"]["min"],
                        max=legacy_seg["thresh"]["max"],
                        step=legacy_seg["thresh"]["step"],
                        default=legacy_seg["thresh"]["default"],
                    )
                ],
            ),
        ],
    )


def simple_page_layout(refresh_path):
    """Creates simple request page"""
    return dbc.Toast(
        id="simple_request_toast",
        header="Simple Pipeline Request",
        header_style={
            "background-color": "#017b70",
            "font-size": "25px",
            "color": "white",
        },
        is_open=True,
        className="my-toast",
        children=[
            popup_comp(
                comp_id="simple_popup",
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
                "algorithms will create a matrix of jobs (multiple "
                "jobs).",
                indent=40,
            ),
            line_breaks(times=2),
            group_accordion(
                children=[
                    title_section(
                        dropdown_id="simple_title_drop",
                        text_id="simple_title_text",
                    ),
                    simple_segmentation_section(),
                    cell_classifier_section(
                        classifier_id="simple_classifier_name"
                    ),
                    further_options_section(
                        reproduce_flag_id="simple_reproduce_flag",
                        num_frames_id="simple_num_frames_switch",
                        num_frames_toggle_id="simple_num_frames_options",
                        num_frames_value="simple_num_frames_value",
                    ),
                    input_data_selection_section(),
                ],
                middle=True,
                open_first=True,
                comp_id="pipeline_accord",
            ),
            input_data_display_section(
                show_grid_id="show_grid",
                button_id="create_simple_pipeline_button",
            ),
            dcc.Store(id="cache_simple_template", storage_type="local"),
            dcc.Store(id="cache_simple_seg_options", storage_type="local"),
            dcc.Store(id="cache_simple_num_frames", storage_type="local"),
        ],
    )


@callback(
    Output("simple_measure_type", "children"),
    Output("cache_simple_seg_options", "data"),
    Input("simple_unet_switch", "value"),
    Input("simple_measure_type", "value"),
    Input("simple_legacy_switch", "value"),
    Input("simple_legacy_thresh_value", "value"),
)
def show_and_cache_segment_options(
    unet_click, measurement_type, legacy_click, legacy_thresh
):
    """This circular callback fetches unet model metadata from the DVC repo
    and shows it as dmc.RadioGroup options, enable the user to select the
    appropriate options from the same dmc.RadioItem options."""

    _, dvc_gitlab = get_gitlab_instances()

    model_dict = dvc_gitlab.get_model_metadata()
    check_boxes = unet_segmentation_options(model_dict)

    segm_options = {}
    if unet_click and measurement_type:
        segm_options[unet_click[0]] = {"model_file": measurement_type}

    if legacy_click and legacy_thresh:
        segm_options[legacy_click[0]] = {"thresh": legacy_thresh}

    return check_boxes, segm_options


@callback(
    Output("simple_unet_options", "style"),
    Input("simple_unet_switch", "value"),
)
def toggle_unet_options(unet_click):
    """Toggle mlunet segmentation options with unet switch"""
    if unet_click:
        return {"display": "block"}
    return {"display": "none"}


@callback(
    Output("simple_legacy_options", "style"),
    Input("simple_legacy_switch", "value"),
)
def toggle_legacy_options(legacy_click):
    """Toggle legacy segmentation options with legacy switch"""
    if legacy_click:
        return {"display": "block"}
    return {"display": "none"}


@callback(
    Output("cache_simple_num_frames", "data"),
    Output("simple_num_frames_options", "style"),
    Input("simple_num_frames_switch", "value"),
    Input("simple_num_frames_value", "key"),
    Input("simple_num_frames_value", "value"),
)
def toggle_simple_num_frames_options(
    num_frames_click, num_frames_key, num_frames_value
):
    """Toggle num_frames options with num_frames switch"""
    if num_frames_click:
        return {num_frames_key: num_frames_value}, {"display": "block"}
    return {}, {"display": "none"}


@callback(
    Output("cache_simple_template", "data"),
    Input("simple_title_drop", "value"),
    Input("simple_title_text", "value"),
    Input("cache_simple_seg_options", "data"),
    Input("cache_simple_num_frames", "data"),
    Input("simple_classifier_name", "value"),
    Input("simple_reproduce_flag", "value"),
    Input("show_grid", "selectedRows"),
)
def collect_simple_pipeline_params(
    author_name,
    simple_title,
    cached_seg_options,
    cached_num_frames,
    simple_classifier,
    reproduce_flag,
    selected_files,
):
    """Collect all the user selected parameters. Then, it updates the simple
    issue template. Updated template will be cached"""
    # Initialize the params dictionary with empty dictionaries

    params_dict = {
        param: None for param in [*simple_classifier, *reproduce_flag]
    }

    # Merge parameter dicts
    params_dict = {
        **params_dict,
        **cached_seg_options,
        **cached_num_frames,
    }

    # Update the template, only when author name, title, and data files
    # to process are entered
    if author_name and simple_title and selected_files:
        rtdc_files = [s["filepath"] for s in selected_files]
        # Create a template dict with title
        pipeline_template = {"title": simple_title}
        # Update the simple template from request repo
        description = update_simple_template(
            params_dict,
            author_name,
            rtdc_files,
            get_simple_template(),
        )
        pipeline_template["description"] = description
        return pipeline_template
    return no_update


@callback(
    Output("create_simple_pipeline_button", "disabled"),
    Input("simple_title_drop", "value"),
    Input("simple_title_text", "value"),
    Input("show_grid", "selectedRows"),
    Input("cache_simple_seg_options", "data"),
)
def toggle_simple_create_pipeline_button(
    author_name, title, selected_files, cached_seg_options
):
    """Activates create pipeline button only when author name, title,
    data files, and segmentation method are entered"""
    if (
        author_name
        and title
        and title.strip()
        and selected_files
        and cached_seg_options
    ):
        return False
    return True


@callback(
    Output("simple_popup", "is_open"),
    Input("create_simple_pipeline_button", "n_clicks"),
    Input("cache_simple_template", "data"),
    Input("simple_popup_close", "n_clicks"),
    State("simple_popup", "is_open"),
)
def simple_request_submission_popup(_, cached_template, close_popup, popup):
    """Show a popup when user clicks on create pipeline button. Then, user
    is asked to close the popup. When user closes page will be refreshed"""

    request_gitlab, _ = get_gitlab_instances()

    button_trigger = [p["prop_id"] for p in ctx.triggered][0]
    if "create_simple_pipeline_button" in button_trigger:
        request_gitlab.run_pipeline(cached_template)
        return not popup
    if close_popup:
        return not popup
    return popup
