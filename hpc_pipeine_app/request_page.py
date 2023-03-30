import dash_bootstrap_components as dbc
from dash import callback, Input, Output, State, dcc, html

from ..gitlab_api import gitlab_api
from .utils import update_simple_template
from ..components import header_comp, paragraph_comp, checklist_comp, \
    upload_comp, text_input_comp, dropdown_searchbar_comp, \
    groupby_rows, num_searchbar_comp, popup_comp, divider_line_comp, \
    group_accordion, line_breaks, button_comp, input_with_dropdown, display_box


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
                               options=["MNet", "Bloody Bunny"],
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
                input_with_dropdown(comp_id="simple_input_bar"),
                line_breaks(times=1),
                paragraph_comp(text="OR", middle=True),
                upload_comp(comp_id="simple_drop_down_upload"),
                line_breaks(times=3),
                html.Div(id='simple_upload_show'),
                # dbc.Accordion([
                #     dbc.AccordionItem([
                #         dbc.Accordion([
                #             dbc.AccordionItem(title="sub dir1"),
                #             dbc.AccordionItem(title="sub dir2")
                #         ]),
                #         dbc.Checklist(
                #             options=[
                #                 {"label": "Option 1", "value": 1},
                #                 {"label": "Option 2", "value": 2},
                #                 {"label": "Option 3", "value": 3},
                #             ],
                #             value=[1, 2],
                #         ),
                #         ],
                #         title="test1"
                #     ),
                #     dbc.AccordionItem([
                #         dbc.Checklist(
                #             options=[
                #                 {"label": "Option 1", "value": 1},
                #                 {"label": "Option 2", "value": 2},
                #                 {"label": "Option 3", "value": 3},
                #             ],
                #             value=1,
                #         )],
                #         title="test2"
                #     )],
                # style={"width": "50%"}
                # )

            ],
                title="Data to Process",
            )
        ],
            middle=True
        ),
        line_breaks(times=4),
        button_comp(label="Create pipeline",
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
                                placeholder="Type title...")
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
                input_with_dropdown(comp_id="advanced_input_bar"),
                # text_input_comp(comp_id="advanced_upload_input",
                #                 placeholder="Enter DCOR id..."),
                line_breaks(times=1),
                paragraph_comp(text="OR", middle=True),
                upload_comp(comp_id="advance_drop_down_upload"),
            ],
                title="Data to Process",
            )
        ],
            middle=True
        ),

        line_breaks(times=4),

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


@callback(Output("store_simple_template", "data"),
          Input("simple_title", "value"),
          Input("simp_segm_id", "value"),
          Input("simp_classifier_id", "value"),
          Input("simp_postana_id", "value"),
          Input("simple_input_bar_drop", "value"),
          Input("simple_input_bar_text", "value"),
          Input("simple_drop_down_upload", "filename"),
          State("store_simple_template", "data")
          )
def collect_simple_pipeline_params(simple_title, simple_segment,
                                   simple_classifier, simple_postana,
                                   simple_input_drop, simple_input_text,
                                   simple_upload_drop,
                                   store_simple_template):
    params = simple_segment + simple_classifier + simple_postana

    # print(simple_upload_dcor, simple_upload_drop)

    final_issue_template = {}
    if simple_title is not None:
        final_issue_template["title"] = simple_title
        final_issue_template["description"] = update_simple_template(params)
        return final_issue_template


@callback(Output("simple_upload_show", "children"),
          Input("simple_input_bar_drop", "value"),
          Input("simple_input_bar_text", "value"),
          Input("simple_drop_down_upload", "filename"),
          )
def display_uploaded_filepaths(drop_value, simple_input_text,
                               simple_upload_drop):
    filelist = str(simple_input_text).split(",")
    if len(filelist) > 1:
        return display_box(drop_value, filelist)


@callback(Output("simple_popup", "is_open"),
          Input("create_simple_pipeline_button", "n_clicks"),
          Input("store_simple_template", "data"),
          State("simple_popup", "is_open")
          )
def simple_request_notification(click, store_simple_template, popup):
    if click:
        gitlab_api.run_pipeline(store_simple_template)
        return not popup
    return popup


@callback(Output("advanced_popup", "is_open"),
          Input("create_advanced_pipeline_button", "n_clicks"),
          State("advanced_popup", "is_open")
          )
def advanced_request_notification(click, popup):
    if click:
        return not popup
    return popup
