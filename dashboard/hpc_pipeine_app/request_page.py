import csv

import dash
import dash_ag_grid as dag
from dash import callback_context as cc
import dash_bootstrap_components as dbc
from dash import callback, Input, Output, State, dcc, html, ALL, ctx, Patch
import pathlib

from ..gitlab_api import get_gitlab_obj
from .utils import update_simple_template
from ..components import (header_comp, paragraph_comp, checklist_comp,
                          text_input_comp, groupby_rows, num_searchbar_comp,
                          dropdown_searchbar_comp, popup_comp, button_comp,
                          divider_line_comp, group_accordion, line_breaks,
                          input_with_dropdown)

gitlab_obj = get_gitlab_obj()

hsmfs_path = pathlib.Path(__file__).parents[2] / "HSMFS_drive.csv"


def get_grid_data(hsm_path=hsmfs_path):
    grid_data = []
    with open(hsm_path, mode="r", encoding="utf-8", errors="replace") as file:
        csvfile = csv.reader(file)
        for line in csvfile:
            parts = line[0].split("\\")
            entry = {
                "filepath": ["HSMFS:"] + parts[4:-1],
                "dateModified": parts[-1]
            }
            grid_data.append(entry)
    return grid_data


def create_hsmfs_grid():
    return html.Div([
        dcc.Store(id="store_input_paths", data=[]),
        dag.AgGrid(
            id="hsmfs_grid",
            className="ag-theme-alpine-dark",
            columnDefs=[
                {"field": "dateModified"},
            ],
            defaultColDef={
                "flex": 1,
                "sortable": True,
            },
            dashGridOptions={
                "autoGroupColumnDef": {
                    "headerName": "HSMFS Drive",
                    "minWidth": 150,
                    "cellRendererParams": {
                        "suppressCount": True,
                        "checkbox": True,
                    },
                },
                "groupDefaultExpanded": 2,
                "getDataPath": {"function": "getDataPath(params)"},
                "treeData": True,
                "animateRows": True,
                "rowSelection": "multiple",
                "groupSelectsChildren": True,
                "suppressRowClickSelection": True,
                # no blue highlight
                "suppressRowHoverHighlight": True,
            },
            rowData=get_grid_data(),
            enableEnterpriseModules=True,
            style={"height": 600}
        )
    ])


def display_paths_comp(comp_id):
    return html.Div(
        className="row justify-content-center",
        children=[
            html.Div(
                dbc.Button([
                    "Selected files:",
                    dbc.Badge(id="num_files", color="danger",
                              text_color="dark", className="ms-1"),
                ],
                    color="info",
                ),
                style={"marginLeft": "0px", "width": "80%"}
            ),
            dbc.Card(
                id=comp_id,
                body=True,
                style={"max-height": "25rem", "width": "80%",
                       "overflow-y": "scroll"},
            )
        ]
    )


def convert_paths_to_buttons(paths):
    return [
        dbc.Row([
            html.Li([
                dbc.Button(
                    "X",
                    n_clicks=0,
                    key=[name],
                    style={"width": "20px", "height": "20px",
                           "padding": "0px", "margin-right": "5px"},
                    class_name="btn btn-danger btn-sm",
                    id={"type": "remove_file", "index": name}
                ),
                html.Span(name)
            ]),
        ],
            style={"flexWrap": "nowrap"}
        ) for name in paths
    ]


@callback(
    [Output("store_input_paths", "data"),
     Output("input_group_drop", "value"),
     Output("input_group_text", "value")],
    Input("input_group_button", "n_clicks"),
    Input("input_group_drop", "value"),
    Input("input_group_text", "value"),
    Input({"type": "remove_file", "index": ALL}, "n_clicks"),
    Input({"type": "remove_file", "index": ALL}, "key"),
    State("store_input_paths", "data")
)
def store_input_group_paths(_, drop_input, text_input,
                            remove_buttons, button_keys, cached_paths):
    button_trigger = [p["prop_id"] for p in cc.triggered][0]
    if text_input is not None and text_input != "" and drop_input is not None:

        if "input_group_button" in button_trigger:
            input_path = f"{drop_input}: {text_input}"
            cached_paths.append(input_path)
            return [cached_paths, None, None]
        else:
            return dash.no_update

    elif 1 in remove_buttons:
        index = remove_buttons.index(1)
        key = button_keys[index][0]
        if key in cached_paths:
            cached_paths.remove(key)
            return [cached_paths, drop_input, text_input]
        else:
            return dash.no_update
    else:
        return [cached_paths, drop_input, text_input]


@callback(
    Output("upload_show", "children"),
    Output("num_files", "children"),
    Input("hsmfs_grid", "selectedRows"),
    Input("store_input_paths", "data"),
)
def display_selected_paths(selected_rows, stored_input):
    original_paths = [] + stored_input
    if selected_rows:
        # Get the list of user selected hsmfs paths (each path is a list
        # of strings) and join them with "/"
        selected_paths = ["/".join(s["filepath"]) for s in selected_rows]
        original_paths = original_paths + selected_paths
    return convert_paths_to_buttons(original_paths), len(original_paths)


@callback(
    Output("hsmfs_grid", "dashGridOptions"),
    Input("grid_filter", "value"),
    State("hsmfs_grid", "dashGridOptions"),
)
def update_filter(filter_value, gridOptions):
    gridOptions["quickFilterText"] = filter_value
    return gridOptions


@callback(
    Output("hsmfs_grid", "selectedRows"),
    Input({"type": "remove_file", "index": ALL}, "n_clicks"),
    State("hsmfs_grid", "selectedRows"),
    prevent_initial_call=True
)
def remove_paths_from_list(remove_buttons, selected_rows):
    if sum(remove_buttons) > 0 and selected_rows is not None:
        selects = Patch()
        for x in range(len(selected_rows) - 1, -1, -1):
            if all(i in ctx.triggered_id.index.split("/") for i in
                   selected_rows[x]["filepath"]):
                del selects[x]
        return selects
    return dash.no_update


def simple_request():
    return dbc.Toast([
        popup_comp(comp_id="simple_popup"),
        line_breaks(times=1),
        header_comp("⦿ Pipeline for segmentation and/or classification "
                    "(prediction) and analysis of data.", indent=40),
        header_comp("⦿ Choosing multiple Segmentation or Prediction "
                    "algorithms will create a matrix of jobs (multiple "
                    "jobs).", indent=40),

        line_breaks(times=2),
        group_accordion([
            dbc.AccordionItem([
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

            dbc.AccordionItem([
                checklist_comp(comp_id="simp_segm_id",
                               options=["legacy", "mlunet",
                                        "watershed", "std"],
                               defaults=["legacy", "mlunet"])
            ],
                title="Segmentation",
            ),
            dbc.AccordionItem([
                paragraph_comp("Classification Model"),
                checklist_comp(comp_id="simp_classifier_id",
                               options=["MNet", "Bloody-Bunny"],
                               defaults=["MNet"])
            ],
                title="Prediction",
            ),
            dbc.AccordionItem([
                checklist_comp(comp_id="simp_postana_id",
                               options=["Benchmarking",
                                        "Scatter Plots"],
                               defaults=["Scatter Plots"])
            ],
                title="Post Analysis",
            ),
            dbc.AccordionItem([
                line_breaks(times=1),
                input_with_dropdown(comp_id="input_group",
                                    drop_options=["DVC", "DCOR"],
                                    dropdown_holder="Source",
                                    input_holder="Enter DVC path or DCOR Id "
                                                 "or Circle or Dataset etc...",
                                    width=80),
                line_breaks(times=2),
                text_input_comp(comp_id="grid_filter",
                                placeholder="Search...",
                                width=20, middle=False),
                create_hsmfs_grid(),
                line_breaks(times=2),
            ],
                title="Data to Process",
            )
        ],
            middle=True
        ),
        line_breaks(times=4),
        display_paths_comp(comp_id="upload_show"),
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
    Input("hsmfs_grid", "selectedRows"),
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


@callback(Output("create_simple_pipeline_button", "disabled"),
          Input("simple_title_text", "value"),
          Input("hsmfs_grid", "selectedRows"),
          Input("store_input_paths", "data"))
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


@callback(Output("simple_popup", "is_open"),
          Input("create_simple_pipeline_button", "n_clicks"),
          Input("store_simple_template", "data"),
          State("simple_popup", "is_open"))
def simple_request_submission_popup(_, store_simple_template, popup):
    button_trigger = [p["prop_id"] for p in cc.triggered][0]
    if "create_simple_pipeline_button" in button_trigger:
        gitlab_obj.run_pipeline(store_simple_template)
        return not popup
    return popup


def advanced_request():
    legacy_thresh_param = paragraph_comp(text="thresh:")
    legacy_thresh_sbar = num_searchbar_comp(comp_id="legacy_thresh_id",
                                            min=-10, max=10, step=1,
                                            default=-6)
    legacy_blur_param = paragraph_comp(text="blur:")
    legacy_blur_sbar = num_searchbar_comp(comp_id="legacy_blur_id",
                                          min=0, max=10, step=1, default=0)

    legacy_binop_param = paragraph_comp(text="binaryops:")
    legacy_binop_sbar = num_searchbar_comp(comp_id="legacy_binop_id",
                                           min=0, max=10, step=1, default=5)

    legacy_difme_param = paragraph_comp(text="diff_method:")
    legacy_difme_sbar = num_searchbar_comp(comp_id="legacy_difme_id",
                                           min=0, max=10, step=1, default=1)

    legacy_clrbo_param = paragraph_comp(text="clear_border:")
    legacy_clrbo_sbar = dropdown_searchbar_comp(comp_id="legacy_clrbo_id",
                                                options=["True", "False"],
                                                defaults=["True"])

    legacy_filho_param = paragraph_comp(text="fill_holes:")
    legacy_filho_sbar = dropdown_searchbar_comp(comp_id="legacy_filho_id",
                                                options=["True", "False"],
                                                defaults=["True"])

    legacy_cldis_param = paragraph_comp(text="close_disk:")
    legacy_cldis_sbar = num_searchbar_comp(comp_id="legacy_cldis_id",
                                           min=0, max=10, step=1, default=5)

    wtrshd_clrbo_param = paragraph_comp(text="clear_border:")
    wtrshd_clrbo_sbar = dropdown_searchbar_comp(comp_id="wtrshd_clrbo_id",
                                                options=["True", "False"],
                                                defaults=["True"])

    wtrshd_filho_param = paragraph_comp(text="fill_holes:")
    wtrshd_filho_sbar = dropdown_searchbar_comp(comp_id="wtrshd_filho_id",
                                                options=["True", "False"],
                                                defaults=["True"])

    wtrshd_cldis_param = paragraph_comp(text="close_disk:")
    wtrshd_cldis_sbar = num_searchbar_comp(comp_id="wtrshd_cldis_id",
                                           min=0, max=10, step=1, default=5)

    std_clrbo_param = paragraph_comp(text="clear_border:")
    std_clrbo_sbar = dropdown_searchbar_comp(comp_id="std_clrbo_id",
                                             options=["True", "False"],
                                             defaults=["True"])

    std_filho_param = paragraph_comp(text="fill_holes:")
    std_filho_sbar = dropdown_searchbar_comp(comp_id="std_filho_id",
                                             options=["True", "False"],
                                             defaults=["True"])

    std_cldis_param = paragraph_comp(text="close_disk:")
    std_cldis_sbar = num_searchbar_comp(comp_id="std_cldis_id",
                                        min=0, max=10, step=1, default=5)

    rollmed_ksize_param = paragraph_comp(text="kernel_size:")
    rollmed_ksize_sbar = num_searchbar_comp(comp_id="rollmed_ksize_id",
                                            min=50, max=500, step=10,
                                            default=100)

    rollmed_bsize_param = paragraph_comp(text="batch_size:")
    rollmed_bsize_sbar = num_searchbar_comp(comp_id="rollmed_bsize_id",
                                            min=100, max=100000, step=100,
                                            default=10000)

    sparsemed_ksize_param = paragraph_comp(text="kernel_size:")
    sparsemed_ksize_sbar = num_searchbar_comp(comp_id="sparsemed_ksize_id",
                                              min=50, max=500, step=10,
                                              default=100)

    sparsemed_bsize_param = paragraph_comp(text="batch_size:")
    sparsemed_bsize_sbar = num_searchbar_comp(comp_id="sparsemed_bsize_id",
                                              min=100, max=100000, step=100,
                                              default=10000)

    sparsemed_thrcln_param = paragraph_comp(text="thresh_cleansing:")
    sparsemed_thrcln_sbar = num_searchbar_comp(comp_id="sparsemed_thrcln_id",
                                               min=0, max=1, step=1,
                                               default=0)

    sparsemed_frcln_param = paragraph_comp(text="frac_cleansing:")
    sparsemed_frcln_sbar = num_searchbar_comp(comp_id="sparsemed_frcln_id",
                                              min=0, max=1, step=0.1,
                                              default=0.8)

    ngate_ongate_param = paragraph_comp(text="online_gates:")
    ngate_ongate_sbar = dropdown_searchbar_comp(comp_id="ngate_ongate_id",
                                                options=["True", "False"],
                                                defaults=["False"])

    ngate_thrmsk_param = paragraph_comp(text="size_thresh_mask:")
    ngate_thrmsk_sbar = num_searchbar_comp(comp_id="ngate_thrmsk_id",
                                           min=0, max=10, step=1,
                                           default=5)

    return dbc.Toast([
        popup_comp(comp_id="advanced_popup"),
        line_breaks(times=1),
        header_comp("⦿ Pipeline for segmentation and/or classification "
                    "(prediction) and analysis of data.", indent=40),

        header_comp("⦿ Choosing multiple Segmentation or Prediction "
                    "algorithms will create a matrix of jobs "
                    "(multiple jobs).", indent=40),

        line_breaks(times=2),
        group_accordion([
            dbc.AccordionItem([
                input_with_dropdown(comp_id="advanced_title",
                                    drop_options=["eoghan", "max", "nadia",
                                                  "paul", "raghava"],
                                    dropdown_holder="User",
                                    input_holder="Type title...",
                                    with_button=False, width=80)
            ],
                title="Title (required)",
            ),

            dbc.AccordionItem([
                checklist_comp(comp_id="dcevent_ver_id",
                               options=["dcevent version=latest"],
                               defaults=["dcevent version=latest"]),
            ],
                title="dcevent version",
            ),

            dbc.AccordionItem([
                checklist_comp(comp_id="mlunet_id",
                               options=["mlunet"],
                               defaults=["mlunet"]),

                divider_line_comp(),

                checklist_comp(comp_id="legacy_id",
                               options=["legacy: Legacy thresholding"
                                        " with OpenCV"],
                               defaults=["legacy: Legacy thresholding"
                                         " with OpenCV"]),

                groupby_rows([legacy_thresh_param, legacy_thresh_sbar]),
                groupby_rows([legacy_blur_param, legacy_blur_sbar]),
                groupby_rows([legacy_binop_param, legacy_binop_sbar]),
                groupby_rows([legacy_difme_param, legacy_difme_sbar]),
                groupby_rows([legacy_clrbo_param, legacy_clrbo_sbar]),
                groupby_rows([legacy_filho_param, legacy_filho_sbar]),
                groupby_rows([legacy_cldis_param, legacy_cldis_sbar]),

                divider_line_comp(),

                checklist_comp(comp_id="watershed_id",
                               options=[
                                   "watershed: Watershed algorithm"],
                               defaults=[
                                   "watershed: Watershed algorithm"]),

                groupby_rows([wtrshd_clrbo_param, wtrshd_clrbo_sbar]),
                groupby_rows([wtrshd_filho_param, wtrshd_filho_sbar]),
                groupby_rows([wtrshd_cldis_param, wtrshd_cldis_sbar]),

                divider_line_comp(),

                checklist_comp(comp_id="std_id",
                               options=["std: Standard-deviation-"
                                        "based thresholding"],
                               defaults=[
                                   "std: Standard-deviation-based "
                                   "thresholding"]),

                groupby_rows([std_clrbo_param, std_clrbo_sbar]),
                groupby_rows([std_filho_param, std_filho_sbar]),
                groupby_rows([std_cldis_param, std_cldis_sbar]),
            ],
                title="Segmentation Algorithm",
            ),
            dbc.AccordionItem([
                checklist_comp(comp_id="rollmed_id",
                               options=["rollmed: Rolling median "
                                        "RT-DC background image "
                                        "computation"],
                               defaults=[
                                   "rollmed: Rolling median RT-DC "
                                   "background image computation"]),

                groupby_rows([rollmed_ksize_param, rollmed_ksize_sbar]),
                groupby_rows([rollmed_bsize_param, rollmed_bsize_sbar]),

                divider_line_comp(),

                checklist_comp(comp_id="sparsemed_id",
                               options=["sparsemed: Sparse median "
                                        "background correction with "
                                        "cleansing"],
                               defaults=["sparsemed: Sparse median "
                                         "background correction with "
                                         "cleansing"]),

                groupby_rows([sparsemed_ksize_param, sparsemed_ksize_sbar]),
                groupby_rows([sparsemed_bsize_param, sparsemed_bsize_sbar]),
                groupby_rows([sparsemed_thrcln_param, sparsemed_thrcln_sbar]),
                groupby_rows([sparsemed_frcln_param, sparsemed_frcln_sbar]),
            ],
                title="Background Correction / Subtraction Method",
            ),

            dbc.AccordionItem([
                checklist_comp(comp_id="ngate_id",
                               options=["norm gating"],
                               defaults=["norm gating"]),

                groupby_rows([ngate_ongate_param, ngate_ongate_sbar]),
                groupby_rows([ngate_thrmsk_param, ngate_thrmsk_sbar]),

                divider_line_comp(),

                checklist_comp(comp_id="repro_id",
                               options=["--reproduce=False"],
                               defaults=["--reproduce=False"])
            ],
                title="Further Options",
            ),

            dbc.AccordionItem([
                checklist_comp(comp_id="dcml_ver_id",
                               options=["dcml version"],
                               defaults=["dcml version"]),

                checklist_comp(comp_id="classifier_id",
                               options=["Classification Model"],
                               defaults=["Classification Model"]),
            ],
                title="Prediction",
            ),
            dbc.AccordionItem([
                line_breaks(times=1),
                input_with_dropdown(comp_id="input_group",
                                    drop_options=["DVC", "DCOR"],
                                    dropdown_holder="Source",
                                    input_holder="Enter DVC path or DCOR Id "
                                                 "or Circle or Dataset etc...",
                                    width=80),
                line_breaks(times=2),
                text_input_comp(comp_id="grid_filter",
                                placeholder="filter...",
                                middle=False,
                                width=20),
                create_hsmfs_grid(),
                line_breaks(times=2),
            ],
                title="Data to Process",
            )
        ],
            middle=True
        ),
        line_breaks(times=4),
        display_paths_comp(comp_id="upload_show"),
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


@callback([Output("legacy_thresh_id", "disabled"),
           Output("legacy_blur_id", "disabled"),
           Output("legacy_binop_id", "disabled"),
           Output("legacy_difme_id", "disabled"),
           Output("legacy_clrbo_id", "disabled"),
           Output("legacy_filho_id", "disabled"),
           Output("legacy_cldis_id", "disabled")],
          Input("legacy_id", "value"),
          )
def toggle_advanced_legacy_params(segm_legacy_opt):
    if len(segm_legacy_opt) == 1:
        return [False] * 7
    else:
        return [True] * 7


@callback(Output("advanced_popup", "is_open"),
          Input("create_advanced_pipeline_button", "n_clicks"),
          State("advanced_popup", "is_open")
          )
def advanced_request_submission_popup(click, popup):
    if click:
        return not popup
    return popup

# @callback(Output("create_advanced_pipeline_button", "disabled"),
#           Input("advanced_title_text", "value"),
#           Input("hsmfs_grid", "selectedRows"),
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
