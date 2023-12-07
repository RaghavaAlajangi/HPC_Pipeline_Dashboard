import dash_bootstrap_components as dbc
from dash import callback_context as cc
from dash import callback, Input, Output, State, html, dcc, ALL

from .utils import update_advanced_template
from .hsm_grid import create_hsm_grid, create_show_grid
from ..components import (header_comp, checklist_comp, group_accordion,
                          popup_comp, button_comp, form_group_dropdown,
                          form_group_input, line_breaks, divider_line_comp)
from ..global_variables import request_gitlab, dvc_gitlab


# Fetch the model checkpoint list from DVC repo
def get_model_ckp_list():
    return dvc_gitlab.get_dvc_files(path="model_registry/segmentation")


# Fetch the members list from request repo
def get_user_list():
    return request_gitlab.get_project_members()


# Fetch the advanced request template from request repo
def get_advanced_template():
    return request_gitlab.read_file(
        path=".gitlab/issue_templates/pipeline_request_advanced.md")


def advanced_request(refresh_path):
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
                            html.Div(
                                dbc.InputGroup(
                                    [
                                        dbc.Select(
                                            placeholder="User",
                                            id="advanced_title_drop",
                                            options=[
                                                {"label": member.name,
                                                 "value": member.username} for
                                                member in get_user_list()
                                            ],
                                            # Note: HPC_pipeline_dashboard is
                                            # hard coded as a default user
                                            value="project_28692_bot1",
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
                    ),
                    # dcevent version section
                    dbc.AccordionItem(
                        title="dcevent version",
                        children=[
                            checklist_comp(
                                comp_id="dcevent_ver_id",
                                options={
                                    "dcevent version=latest": False,
                                },
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
                                options={"mlunet: UNET": False},
                                defaults=["mlunet: UNET"]
                            ),
                            html.Ul(
                                id="mlunet_options",
                                children=[
                                    form_group_dropdown(
                                        comp_id="mlunet_modelpath",
                                        label="model_file",
                                        box_width=18,
                                        options=get_model_ckp_list(),
                                        default=get_model_ckp_list()[-1],
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
                                        label="thresh",
                                        min=-10, max=10, step=1,
                                        default=-6
                                    ),
                                    form_group_input(
                                        comp_id={"type": "legacy_param",
                                                 "index": 2},
                                        label="blur",
                                        min=0, max=10, step=1,
                                        default=0
                                    ),
                                    form_group_input(
                                        comp_id={"type": "legacy_param",
                                                 "index": 3},
                                        label="binaryops",
                                        min=0, max=10, step=1,
                                        default=5
                                    ),
                                    form_group_input(
                                        comp_id={"type": "legacy_param",
                                                 "index": 4},
                                        label="diff_method",
                                        min=0, max=10, step=1,
                                        default=1
                                    ),
                                    form_group_dropdown(
                                        comp_id={"type": "legacy_param",
                                                 "index": 5},
                                        label="clear_border",
                                        options=["True", "False"],
                                        default="True"
                                    ),
                                    form_group_dropdown(
                                        comp_id={"type": "legacy_param",
                                                 "index": 6},
                                        label="fill_holes",
                                        options=["True", "False"],
                                        default="True"
                                    ),

                                    form_group_input(
                                        comp_id={"type": "legacy_param",
                                                 "index": 7},
                                        label="closing_disk",
                                        min=0, max=10, step=1,
                                        default=5
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
                                        options=["True", "False"],
                                        default="True"
                                    ),
                                    form_group_dropdown(
                                        comp_id={"type": "watershed_param",
                                                 "index": 2},
                                        label="fill_holes",
                                        options=["True", "False"],
                                        default="True"
                                    ),
                                    form_group_input(
                                        comp_id={"type": "watershed_param",
                                                 "index": 3},
                                        label="closing_disk",
                                        min=0, max=10, step=1,
                                        default=5
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
                                        options=["True", "False"],
                                        default="True"
                                    ),
                                    form_group_dropdown(
                                        comp_id={"type": "std_param",
                                                 "index": 2},
                                        label="fill_holes",
                                        options=["True", "False"],
                                        default="True"
                                    ),
                                    form_group_input(
                                        comp_id={"type": "std_param",
                                                 "index": 3},
                                        label="closing_disk",
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
                                options={
                                    "rollmed: Rolling median "
                                    "RT-DC background image "
                                    "computation": False,
                                },
                                defaults=["rollmed: Rolling median RT-DC "
                                          "background image computation"]
                            ),
                            html.Ul(
                                id="rollmed_options",
                                children=[
                                    form_group_input(
                                        comp_id={"type": "rollmed_param",
                                                 "index": 1},
                                        label="kernel_size",
                                        min=50, max=500, step=10,
                                        default=100
                                    ),
                                    form_group_input(
                                        comp_id={"type": "rollmed_param",
                                                 "index": 2},
                                        label="batch_size",
                                        min=0, max=100000, step=1000,
                                        default=10000
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
                                }
                            ),
                            html.Ul(
                                id="sparsemed_options",
                                children=[
                                    form_group_input(
                                        comp_id={"type": "sparsemed_param",
                                                 "index": 1},
                                        label="kernel_size",
                                        min=50, max=500, step=10,
                                        default=200
                                    ),
                                    form_group_input(
                                        comp_id={"type": "sparsemed_param",
                                                 "index": 2},
                                        label="split_time",
                                        min=1, max=30, step=1,
                                        default=1
                                    ),
                                    form_group_input(
                                        comp_id={"type": "sparsemed_param",
                                                 "index": 3},
                                        label="thresh_cleansing",
                                        min=0, max=1, step=0.1,
                                        default=0
                                    ),
                                    form_group_input(
                                        comp_id={"type": "sparsemed_param",
                                                 "index": 4},
                                        label="frac_cleansing",
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
                                options={
                                    "norm gating": False,
                                },
                                defaults=["norm gating"]
                            ),
                            html.Ul(
                                id="ngate_options",
                                children=[
                                    form_group_dropdown(
                                        comp_id={"type": "ngate_param",
                                                 "index": 1},
                                        label="online_gates",
                                        options=["True", "False"],
                                        default="False",
                                    ),
                                    form_group_input(
                                        comp_id={"type": "ngate_param",
                                                 "index": 2},
                                        label="size_thresh_mask",
                                        min=0, max=10, step=1,
                                        default=5
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
                                options={
                                    "--reproduce": False,
                                }
                            )
                        ]
                    ),
                    dbc.AccordionItem(
                        title="Classification Model",
                        children=[
                            checklist_comp(
                                comp_id="classifier_id",
                                options={
                                    "bloody-bunny_g1_bacae: "
                                    "Bloody Bunny": False,
                                },
                                defaults=["bloody-bunny_g1_bacae: "
                                          "Bloody Bunny"]
                            )
                        ]
                    ),
                    dbc.AccordionItem(
                        title="Post Analysis (Not Implemented)",
                        children=[
                            checklist_comp(
                                comp_id="adv_postana_id",
                                options={
                                    "Benchmarking": True,
                                    "Scatter Plot": True,
                                }
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
                open_first=True,
                comp_id="pipeline_accord"
            ),
            line_breaks(times=3),
            create_show_grid(comp_id="show_grid"),
            line_breaks(times=4),
            button_comp(label="Create pipeline",
                        disabled=True,
                        comp_id="create_advanced_pipeline_button"),
            line_breaks(times=5),
            dcc.Store(id="store_advanced_template"),
            dcc.Store(id="store_mlunet_params", data={}),
            dcc.Store(id="store_legacy_params", data={}),
            dcc.Store(id="store_watershed_params", data={}),
            dcc.Store(id="store_std_params", data={}),
            dcc.Store(id="store_rollmed_params", data={}),
            dcc.Store(id="store_sparsemed_params", data={}),
            dcc.Store(id="store_ngate_params", data={}),
        ]
    )


@callback(
    Output("store_mlunet_params", "data"),
    Output("mlunet_options", "style"),
    Input("mlunet_id", "value"),
    Input("mlunet_modelpath", "key"),
    Input("mlunet_modelpath", "value"),
)
def toggle_mlunet_options(mlunet_opt, mpath_key, mpath_value):
    """Toggle mlunet segmentation options with mlunet switch, selected options
    will be cached"""
    model_file = {mpath_key: mpath_value}
    if len(mlunet_opt) == 1:
        return {mlunet_opt[0]: model_file}, {"display": "block"}
    else:
        return {}, {"display": "none"}


@callback(
    Output("store_legacy_params", "data"),
    Output("legacy_options", "style"),
    Input("legacy_id", "value"),
    Input({"type": "legacy_param", "index": ALL}, "key"),
    Input({"type": "legacy_param", "index": ALL}, "value"),
)
def toggle_legacy_options(legacy_opt, leg_keys, leg_values):
    """Toggle legacy segmentation options with legacy switch, selected options
    will be cached"""
    legacy_params = {k: v for k, v in zip(leg_keys, leg_values)}

    if len(legacy_opt) == 1:
        return {legacy_opt[0]: legacy_params}, {"display": "block"}
    else:
        return {}, {"display": "none"}


@callback(
    Output("store_watershed_params", "data"),
    Output("watershed_options", "style"),
    Input("watershed_id", "value"),
    Input({"type": "watershed_param", "index": ALL}, "key"),
    Input({"type": "watershed_param", "index": ALL}, "value"),
)
def toggle_watershed_options(watershed_opt, water_keys, water_values):
    """Toggle watershed segmentation options with watershed switch, selected
    options will be cached"""
    water_params = {k: v for k, v in zip(water_keys, water_values)}
    if len(watershed_opt) == 1:
        return {watershed_opt[0]: water_params}, {"display": "block"}
    else:
        return {}, {"display": "none"}


@callback(
    Output("store_std_params", "data"),
    Output("std_options", "style"),
    Input("std_id", "value"),
    Input({"type": "std_param", "index": ALL}, "key"),
    Input({"type": "std_param", "index": ALL}, "value"),
)
def toggle_std_options(std_opt, std_keys, std_values):
    """Toggle std segmentation options with std switch, selected options
    will be cached"""
    std_params = {k: v for k, v in zip(std_keys, std_values)}
    if len(std_opt) == 1:
        return {std_opt[0]: std_params}, {"display": "block"}
    else:
        return {}, {"display": "none"}


@callback(
    Output("store_rollmed_params", "data"),
    Output("rollmed_options", "style"),
    Input("rollmed_id", "value"),
    Input({"type": "rollmed_param", "index": ALL}, "key"),
    Input({"type": "rollmed_param", "index": ALL}, "value"),
)
def toggle_rollmed_options(rollmed_opt, rollmed_keys, rollmed_values):
    """Toggle rolling median background correction options with rolling
    median switch, selected options will be cached"""
    rollmed_params = {k: v for k, v in zip(rollmed_keys, rollmed_values)}
    if len(rollmed_opt) == 1:
        return {rollmed_opt[0]: rollmed_params}, {"display": "block"}
    else:
        return {}, {"display": "none"}


@callback(
    Output("store_sparsemed_params", "data"),
    Output("sparsemed_options", "style"),
    Input("sparsemed_id", "value"),
    Input({"type": "sparsemed_param", "index": ALL}, "key"),
    Input({"type": "sparsemed_param", "index": ALL}, "value"),
)
def toggle_sparsemed_options(sparsemed_opt, sparsemed_keys, sparsemed_values):
    """Toggle sparse median background correction options with sparse
    median switch, selected options will be cached"""
    sparsemed_params = {k: v for k, v in zip(sparsemed_keys, sparsemed_values)}
    if len(sparsemed_opt) == 1:
        return {sparsemed_opt[0]: sparsemed_params}, {"display": "block"}
    else:
        return {}, {"display": "none"}


@callback(
    Output("store_ngate_params", "data"),
    Output("ngate_options", "style"),
    Input("ngate_id", "value"),
    Input({"type": "ngate_param", "index": ALL}, "key"),
    Input({"type": "ngate_param", "index": ALL}, "value"),
)
def toggle_ngate_options(ngate_opt, ngate_keys, ngate_values):
    """Toggle norm gating options with norm gating switch, selected options
    will be cached"""
    ngate_params = {k: v for k, v in zip(ngate_keys, ngate_values)}
    if len(ngate_opt) == 1:
        return {ngate_opt[0]: ngate_params}, {"display": "block"}
    else:
        return {}, {"display": "none"}


@callback(
    Output("store_advanced_template", "data"),
    Input("advanced_title_drop", "value"),
    Input("advanced_title_text", "value"),
    # Direct options
    Input("dcevent_ver_id", "value"),
    Input("repro_id", "value"),
    Input("classifier_id", "value"),
    Input("adv_postana_id", "value"),
    # Cached options
    Input("store_mlunet_params", "data"),
    Input("store_legacy_params", "data"),
    Input("store_watershed_params", "data"),
    Input("store_std_params", "data"),
    Input("store_rollmed_params", "data"),
    Input("store_sparsemed_params", "data"),
    Input("store_ngate_params", "data"),
    # Data to process
    Input("show_grid", "selectedRows")
)
def collect_advanced_pipeline_params(*args):
    """Collect all the user selected and cached parameters. Then, it updates
    the advanced issue template. Updated template will be cached"""
    # Get the title of the request
    author_name, advanced_title = args[0:2]
    # Get the params value list and convert it to a dictionary
    params = [item for sublist in args[2:5] for item in sublist]
    params_dict = {params: {} for params in params}
    # Get the cached selections and update the dictionary
    for d in args[6:-1]:
        params_dict.update(d)
    # Get the data files
    selected_files = args[-1]

    # Update the template, only when is a title and data files to process
    if advanced_title and selected_files:
        rtdc_files = [s["filepath"] for s in selected_files]
        # Create a template dict with title
        pipeline_template = {"title": advanced_title}
        # Update the advanced template from request repo
        description = update_advanced_template(params_dict, author_name,
                                               rtdc_files,
                                               get_advanced_template())
        pipeline_template["description"] = description
        return pipeline_template


@callback(
    Output("advanced_popup", "is_open"),
    Input("create_advanced_pipeline_button", "n_clicks"),
    Input("store_advanced_template", "data"),
    Input("advanced_popup_close", "n_clicks"),
    State("advanced_popup", "is_open")
)
def advanced_request_submission_popup(_, cached_adv_temp, close_popup, popup):
    """Show a popup when user clicks on create pipeline button. Then, user
    is asked to close the popup. When user closes page will be refreshed"""
    button_trigger = [p["prop_id"] for p in cc.triggered][0]
    if "create_advanced_pipeline_button" in button_trigger and cached_adv_temp:
        request_gitlab.run_pipeline(cached_adv_temp)
        return not popup
    if close_popup:
        return not popup
    return popup


@callback(
    Output("create_advanced_pipeline_button", "disabled"),
    Input("advanced_title_text", "value"),
    Input("show_grid", "selectedRows")
)
def toggle_advanced_create_pipeline_button(title, selected_files):
    """Activates create pipeline button only when the issue title and data
    files are put in the template"""
    if selected_files and title and title != "":
        return False
    else:
        return True
