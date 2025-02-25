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
    format_params,
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
                unet_switch_id="simple_unet_click",
                unet_toggle_id="simple_unet_toggle",
                unet_options_id="simple_unet_model",
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
                        id="simple_legacy_click",
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
                id="simple_legacy_toggle",
                children=[
                    form_group_input(
                        comp_id="simple_legacy_param",
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
                        dropdown_id="title_drop",
                        text_id="titel_text",
                    ),
                    simple_segmentation_section(),
                    cell_classifier_section(classifier_id="classifier_click"),
                    further_options_section(
                        reproduce_flag_id="reproduce_click",
                        num_frames_id="simple_nframe_click",
                        num_frames_toggle_id="simple_nframe_toggle",
                        num_frames_value="simple_nframe_value",
                    ),
                    input_data_selection_section(),
                ],
                middle=True,
                open_first=True,
                comp_id="pipeline_accord",
            ),
            input_data_display_section(
                show_grid_id="show_grid",
                button_id="simple_create_pipeline_click",
            ),
            dcc.Store(id="cache_simple_template"),
            dcc.Store(id="cache_simple_params", data={}),
        ],
    )


@callback(
    Output("simple_unet_model", "children"),
    Input("simple_unet_click", "value"),
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
    # Outputs
    Output("cache_simple_params", "data"),
    Output("simple_unet_toggle", "style"),
    Output("simple_legacy_toggle", "style"),
    Output("simple_nframe_toggle", "style"),
    # Unet inputs
    Input("simple_unet_click", "value"),
    Input("simple_unet_model", "value"),
    # Legacy inputs
    Input("simple_legacy_click", "value"),
    Input("simple_legacy_param", "key"),
    Input("simple_legacy_param", "value"),
    # bloody bunny input
    Input("classifier_click", "value"),
    # reproduce flag input
    Input("reproduce_click", "value"),
    # num frames inputs
    Input("simple_nframe_click", "value"),
    Input("simple_nframe_value", "value"),
)
def toggle_and_cache_params(
    unet_click,
    unet_value,
    legacy_click,
    legacy_key,
    legacy_value,
    classifier_click,
    reproduce_click,
    nframe_click,
    nframe_value,
):
    """Consolidated callback for toggling options and caching parameters"""
    print(
        legacy_click,
        legacy_key,
        legacy_value,
    )
    cache_data = {
        **format_params(
            unet_click, [unet_value if unet_value else ""], ["model_file"]
        ),
        **format_params(legacy_click, [legacy_value], [legacy_key]),
        **format_params(nframe_click, nframe_value),
        **format_params(classifier_click, None),
        **format_params(reproduce_click, None),
    }

    return (
        cache_data,
        {"display": "block"} if unet_click else {"display": "none"},
        {"display": "block"} if legacy_click else {"display": "none"},
        {"display": "block"} if nframe_click else {"display": "none"},
    )


@callback(
    Output("cache_simple_template", "data"),
    Input("title_drop", "value"),
    Input("titel_text", "value"),
    Input("cache_simple_params", "data"),
    Input("show_grid", "selectedRows"),
)
def collect_simple_pipeline_params(
    author_name,
    simple_title,
    cached_params,
    selected_rows,
):
    """Collect all the user selected parameters. Then, it updates the simple
    issue template. Updated template will be cached"""
    # Update the template, only when author name, title, and data files
    # to process are entered
    if author_name and simple_title and selected_rows:
        rtdc_files = [s["filepath"] for s in selected_rows]
        # Create a template dict with title
        pipeline_template = {"title": simple_title}
        # Update the simple template from request repo
        description = update_simple_template(
            cached_params,
            author_name,
            rtdc_files,
            get_simple_template(),
        )
        pipeline_template["description"] = description
        return pipeline_template
    return no_update


@callback(
    Output("simple_create_pipeline_click", "disabled"),
    Input("title_drop", "value"),
    Input("titel_text", "value"),
    Input("show_grid", "selectedRows"),
    Input("cache_simple_params", "data"),
)
def toggle_simple_create_pipeline_button(
    author_name, title, selected_rows, cached_params
):
    """Activates create pipeline button only when author name, title,
    data files, and segmentation method are entered"""
    if (
        author_name
        and title
        and title.strip()
        and selected_rows
        and cached_params
    ):
        return False
    return True


@callback(
    Output("simple_popup", "is_open"),
    Input("simple_create_pipeline_click", "n_clicks"),
    Input("cache_simple_template", "data"),
    Input("simple_popup_close", "n_clicks"),
    State("simple_popup", "is_open"),
)
def simple_request_submission_popup(_, cached_template, close_popup, popup):
    """Show a popup when user clicks on create pipeline button. Then, user
    is asked to close the popup. When user closes page will be refreshed"""

    request_gitlab, _ = get_gitlab_instances()

    button_trigger = [p["prop_id"] for p in ctx.triggered][0]
    if "simple_create_pipeline_click" in button_trigger:
        request_gitlab.run_pipeline(cached_template)
        return not popup
    if close_popup:
        return not popup
    return popup
