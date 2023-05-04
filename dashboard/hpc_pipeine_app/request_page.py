import os
import functools

from pathlib import Path
import dash
from dash import callback_context as cc
import dash_bootstrap_components as dbc
from dash import callback, Input, Output, State, dcc, html, ALL, MATCH

from ..gitlab_api import get_gitlab_obj
from .utils import update_simple_template
from ..components import (header_comp, paragraph_comp, checklist_comp,
                          text_input_comp, groupby_rows, num_searchbar_comp,
                          dropdown_searchbar_comp, popup_comp, button_comp,
                          divider_line_comp, group_accordion, line_breaks,
                          input_with_dropdown)

# HSMFS drive path
hsm_path = Path(__file__).parents[3] / "HSMFS"
gitlab_obj = get_gitlab_obj()

# hsm_path = Path(r"C:\Users\ralajan\Desktop\Raghava_Desktop\copy")


def os_suffix(path):
    return os.path.splitext(path)[1]


def os_bname(path):
    return os.path.basename(path)


@functools.lru_cache(maxsize=None, typed=True)
def get_dir_contents(path, mode="dir_rtdc"):
    if mode == "only_rtdc":
        contents = [d for d in os.scandir(path) if os_suffix(d) == ".rtdc"]
    else:
        contents = [d for d in os.scandir(path) if
                    d.is_dir() or os_suffix(d) == ".rtdc"]
    return contents


def file_checkbox_comp(pathlib_path, margin=5, tickbox=False):
    checkbox_item = dbc.Checklist(
        options=[
            {"label": pathlib_path.name, "value": pathlib_path.path}
        ],
        id={"type": "file_checkbox", "index": pathlib_path.path},
        input_checked_class_name="border-success bg-success",
        value=[pathlib_path.path] if tickbox else []
    )
    return html.Div(
        checkbox_item,
        style={"margin-bottom": f"{margin}px",
               "margin-top": f"{margin}px"}
    )


def dir_checkbox_comp(pathlib_path, margin=5):
    # Get the list of rtdc files of the given pathlib_path
    dir_contents = get_dir_contents(pathlib_path, mode="only_rtdc")
    # Check whether dir has rtdc files
    is_dir_empty = True if len(dir_contents) == 0 else False
    list_item = html.Li(
        children=[
            dbc.Checklist(
                options=[
                    {"label": "", "value": pathlib_path.path,
                     # disable the dir checkbox if it does not
                     # have the rtdc files
                     "disabled": is_dir_empty
                     }
                ],
                value=[], style={"display": "inline-block"},
                id={"type": "dir_checkbox", "index": pathlib_path.path},
                key=pathlib_path.path,
                label_checked_class_name="text-danger",
                input_checked_class_name="border-danger bg-danger"
            ),
            html.Span(
                pathlib_path.name,
                id={"type": "dir", "index": pathlib_path.path},
                key=pathlib_path.path,
                n_clicks=0
            ),
            html.Ul(
                id={"type": "dir_children", "index": pathlib_path.path},
            )
        ],
        style={"cursor": "pointer"}
    )
    return html.Div(
        list_item,
        style={"margin-bottom": f"{margin}px", "margin-top": f"{margin}px"}
    )


def hsm_drive_comp(hsm_path):
    """
    The hsm_drive_comp function is a Dash component that displays the
    contents of the HSMFS shared drive. It takes in one argument, hsm_path,
    which is a string representing the path to an HSMFS directory.
    The function returns a Div containing:
    - A dcc.Store object, which stores all selected paths for later use; and
    - A Card containing, subdirectories and rtdc files
    """
    dir_contents = get_dir_contents(hsm_path)
    div_children = [
        dir_checkbox_comp(item)
        if item.is_dir() else file_checkbox_comp(item) for
        item in dir_contents
    ]
    return html.Div([
        # dcc.Store(id="store_final_paths", data=[]),
        dcc.Store(id="store_input_paths", data=[]),
        paragraph_comp(text="HSMFS shared drive:", middle=True),
        dbc.Card(
            children=div_children,
            style={"max-height": "30rem", "width": "80%",
                   "overflow-y": "scroll"},
        )
    ],
        className="row justify-content-center"
    )


def display_paths_comp(comp_id):
    return html.Div(
        className="row justify-content-center",
        children=[
            paragraph_comp(text="Selected files:", middle=True),
            dbc.Card(
                id=comp_id,
                body=True,
                style={"max-height": "25rem", "width": "80%",
                       "overflow-x": "scroll"},
            )
        ])


def create_html_path_list(str_paths):
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
        ) for name in str_paths
    ]


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
                text_input_comp(comp_id="simple_title",
                                placeholder="Type title...")
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
                input_with_dropdown(comp_id="input_group", width=80),
                # line_breaks(times=1),
                # paragraph_comp(text="OR", middle=True),
                # upload_comp(comp_id="simple_drop_down_upload"),
                line_breaks(times=2),
                hsm_drive_comp(hsm_path),
                line_breaks(times=2),
            ],
                title="Data to Process",
            )
        ],
            middle=True
        ),
        line_breaks(times=4),
        display_paths_comp(comp_id="simple_upload_show"),
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


@callback(Output("store_simple_template", "data"),
          Input("simple_title", "value"),
          Input("simp_segm_id", "value"),
          Input("simp_classifier_id", "value"),
          Input("simp_postana_id", "value"),
          Input({"type": "file_checkbox", "index": ALL}, "value"),
          Input("store_input_paths", "data"))
def collect_simple_pipeline_params(simple_title, simple_segment,
                                   simple_classifier, simple_postana,
                                   file_checkboxes, stored_input):
    params = simple_segment + simple_classifier + simple_postana
    rtdc_files = [f for sub in file_checkboxes for f in sub] + stored_input
    pipeline_template = {}
    if simple_title is not None and len(rtdc_files) != 0:
        simple_template = gitlab_obj.get_simple_template()
        pipeline_template["title"] = simple_title
        description = update_simple_template(params,
                                             rtdc_files,
                                             simple_template)
        pipeline_template["description"] = description
        return pipeline_template


@callback([Output({"type": "dir_children", "index": MATCH}, "style"),
           Output({"type": "dir_children", "index": MATCH}, "children")],
          Input({"type": "dir", "index": MATCH}, "n_clicks"),
          Input({"type": "dir", "index": MATCH}, "key"),
          Input({"type": "dir_checkbox", "index": MATCH}, "value")
          )
def dir_tree_dropdown(dir_click, dir_key, dir_checkbox):
    if dir_click % 2 == 0:
        return [{"display": "none"}, dash.no_update]
    else:
        dir_contents = get_dir_contents(dir_key)
        if len(dir_contents) > 0:
            # Tick all the checkboxes of rtdc files in the child dir
            # if user select the checkbox of the parent dir
            tick = True if dir_key in dir_checkbox else False
            children = [
                dir_checkbox_comp(item)
                if item.is_dir() else file_checkbox_comp(item, tickbox=tick)
                for item in dir_contents
            ]
            return [{"display": "block"}, children]
        else:
            return [{"display": "none"}, dash.no_update]


@callback([Output("store_input_paths", "data"),
           Output("input_group_drop", "value"),
           Output("input_group_text", "value")],
          Input("input_group_button", "n_clicks"),
          Input("input_group_drop", "value"),
          Input("input_group_text", "value"),
          Input({"type": "remove_file", "index": ALL}, "n_clicks"),
          Input({"type": "remove_file", "index": ALL}, "key"),
          State("store_input_paths", "data"))
def store_input_group_paths(add_button, drop_input, text_input,
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


@callback(Output("simple_upload_show", "children"),
          Input({"type": "dir_checkbox", "index": ALL}, "value"),
          Input({"type": "file_checkbox", "index": ALL}, "value"),
          Input("store_input_paths", "data"),
          State("simple_upload_show", "children"))
def show_selected_paths(dir_checkboxes, file_checkboxes, stored_input,
                        display_children):
    # print(dir_checkboxes)
    # folder_checklist = [Path(f) for sub in dir_checkboxes for f in sub]
    #
    # # Get the rtdc file checkboxes based on folder checkbox
    # file_checklist1 = [str(f) for fc in folder_checklist for f in
    #                    fc.iterdir() if f.suffix == ".rtdc"]
    #
    # # Get the rtdc file checkboxes based on file checkboxes
    # file_checklist2 = [f for sub in file_checkboxes for f in sub]
    #
    # # Get the rtdc files checkboxes that are selected by the user
    # final_list = list(set(file_checklist1).union(file_checklist2))
    #
    # selected_paths = final_list + stored_input

    selected_paths = [f for sub in file_checkboxes for f in sub] + stored_input
    if display_children is not None and len(display_children) == len(
            selected_paths):
        return display_children
    else:
        return create_html_path_list(selected_paths)


@callback(
    Output({"type": "file_checkbox", "index": ALL}, "value"),
    Input({"type": "remove_file", "index": ALL}, "n_clicks"),
    Input({"type": "remove_file", "index": ALL}, "key"),
    State({"type": "file_checkbox", "index": ALL}, "value"))
def remove_files_from_list(remove_buttons, button_keys, file_checkboxes):
    remove_buttons = [0 if b % 2 == 0 else 1 for b in remove_buttons]
    if 1 in remove_buttons:
        index = remove_buttons.index(1)
        key = button_keys[index]
        file_checkboxes = [[] if i == key else i for i in file_checkboxes]
    return file_checkboxes


@callback(Output("create_simple_pipeline_button", "disabled"),
          Input("simple_title", "value"),
          Input({"type": "file_checkbox", "index": ALL}, "value"),
          Input("store_input_paths", "data"))
def toggle_create_pipeline_button(title, file_checkboxes, stored_input):
    selected_paths = [f for sub in file_checkboxes for f in sub] + stored_input
    if title is None or title == "":
        return True
    elif len(selected_paths) == 0:
        return True
    else:
        return False


@callback(Output("simple_popup", "is_open"),
          Input("create_simple_pipeline_button", "n_clicks"),
          Input("store_simple_template", "data"),
          State("simple_popup", "is_open"))
def simple_request_notification(click, store_simple_template, popup):
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
                text_input_comp(comp_id="advanced_title",
                                placeholder="Type title...",
                                width=80)
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
                input_with_dropdown(comp_id="input_group", width=60),
                # line_breaks(times=1),
                # paragraph_comp(text="OR", middle=True),
                # upload_comp(comp_id="simple_drop_down_upload"),
                line_breaks(times=2),
                hsm_drive_comp(hsm_path),
                line_breaks(times=2),
            ],
                title="Data to Process",
            )
        ],
            middle=True
        ),

        line_breaks(times=4),
        display_paths_comp(comp_id="simple_upload_show"),
        button_comp(label="Create pipeline",
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
def advanced_request_notification(click, popup):
    if click:
        return not popup
    return popup
