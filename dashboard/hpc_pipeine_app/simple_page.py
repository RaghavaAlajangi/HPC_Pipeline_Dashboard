from dash import callback_context as cc
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import callback, Input, Output, State, dcc, no_update, html

from .utils import update_simple_template
from .hsm_grid import create_hsm_grid, display_paths_comp
from ..components import (header_comp, paragraph_comp, checklist_comp,
                          group_accordion, popup_comp, button_comp,
                          line_breaks, input_with_dropdown)

from ..global_variables import PATHNAME_PREFIX, gitlab_obj


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
                        item_id="hsm_accord",
                        children=[
                            create_hsm_grid(),
                            line_breaks(times=2),
                        ]
                    )
                ],
                middle=True,
                comp_id="pipeline_accord"
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
    Output("refresh_simple", "pathname"),
    Input("create_simple_pipeline_button", "n_clicks"),
    Input("store_simple_template", "data"),
    Input("simple_popup_close", "n_clicks"),
    State("simple_popup", "is_open")
)
def simple_request_submission_popup(_, cached_simp_temp, close_popup, popup):
    button_trigger = [p["prop_id"] for p in cc.triggered][0]
    if "create_simple_pipeline_button" in button_trigger:
        gitlab_obj.run_pipeline(cached_simp_temp)
        return not popup, no_update
    if close_popup:
        return not popup, PATHNAME_PREFIX
    return popup, no_update
