from dash import callback_context as cc
import dash_bootstrap_components as dbc
from dash import callback, Input, Output, State, dcc

from .utils import update_simple_template
from .hsm_grid import create_hsm_grid, create_show_grid
from ..components import (header_comp, paragraph_comp, checklist_comp,
                          group_accordion, popup_comp, button_comp,
                          line_breaks, input_with_dropdown)

from ..global_variables import request_gitlab

# Fetch the simple request template from request repo
simple_template = request_gitlab.read_file(
    path=".gitlab/issue_templates/pipeline_request_simple.md")


def simple_request(refresh_path):
    """Creates simple request page"""
    return dbc.Toast(
        id="simple_request_toast",
        header="Simple pipeline request",
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
                                # drop_options=request_gitlab.get_project_members(),
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
            create_show_grid(comp_id="show_grid"),
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
    Input("show_grid", "selectedRows")
)
def collect_simple_pipeline_params(simple_title, simple_segment,
                                   simple_classifier, simple_postana,
                                   selected_files):
    """Collect all the user selected parameters. Then, it updates the simple
    issue template. Updated template will be cached"""
    params = simple_segment + simple_classifier + simple_postana

    # Update the template, only when is a title and data paths to process
    if simple_title and selected_files:
        rtdc_files = [s["filepath"] for s in selected_files]
        # Create a template dict with title
        pipeline_template = {"title": simple_title}
        # Update the simple template from request repo
        description = update_simple_template(params, rtdc_files,
                                             simple_template)
        pipeline_template["description"] = description
        return pipeline_template


@callback(
    Output("create_simple_pipeline_button", "disabled"),
    Input("simple_title_text", "value"),
    Input("show_grid", "selectedRows")
)
def toggle_simple_create_pipeline_button(title, selected_files):
    """Activates create pipeline button only when the issue title and data
    paths are put in the template"""
    if selected_files and title and title != "":
        return False
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
