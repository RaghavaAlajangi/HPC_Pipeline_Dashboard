from dash import dcc, html
from dash import callback, Input, Output, State
import dash_bootstrap_components as dbc
from .components import title_accord_item, segment_accord_item, \
    bg_corr_sub_accord_item, input_data_accord_item, gating_opt_accord_item, \
    further_opt_accord_item, pipeline_notification


def simple_request():
    return dbc.Toast([
        pipeline_notification(comp_id="simple_pipe_notification"),
        html.H6(
            f"Pipeline for segmentation and/or classification (prediction) "
            f"and analysis of data."),
        html.H6(
            f"Choosing multiple Segmentation or Prediction algorithms "
            f"will create a matrix of jobs (multiple jobs)."),
        html.Br(), html.Br(),
        dbc.Accordion([
            title_accord_item(),

            dbc.AccordionItem([
                dbc.Checklist(
                    options=[
                        {"label": "Legacy", "value": 1},
                        {"label": "MLUNet", "value": 2},
                        {"label": "Watershed", "value": 3},
                        {"label": "STD", "value": 4},
                    ],
                    value=[1, 2],
                    switch=True,
                    labelCheckedClassName="text-success",
                    inputCheckedClassName="border border-success bg-success",
                )
            ],
                title="Segmentation",
            ),
            dbc.AccordionItem([
                html.P("Classification Model"),
                dbc.Checklist(
                    options=[
                        {"label": "MNet", "value": 1},
                        {"label": "BloodyBunny", "value": 2},
                    ],
                    value=[1],
                    switch=True,
                    labelCheckedClassName="text-success",
                    inputCheckedClassName="border border-success bg-success",
                )
            ],
                title="Prediction",
            ),
            dbc.AccordionItem([
                dbc.Checklist(
                    options=[
                        {"label": "Benchmarking", "value": 1},
                        {"label": "Scatter Plots", "value": 2},
                    ],
                    value=[2],
                    switch=True,
                    labelCheckedClassName="text-success",
                    inputCheckedClassName="border border-success bg-success",
                )
            ],
                title="Post Analysis",
            ),
            dbc.AccordionItem([
                html.P("Add the data that need to be processed!"),
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    className="dcc-upload",
                    # Allow multiple files to be uploaded
                    multiple=True
                ),
            ],
                "This is the content of the third section",
                title="Data to Process",
            ),
        ]),
        html.Br(), html.Br(), html.Br(), html.Br(),
        dbc.Button("Create pipeline",
                   id="create_simple_pipeline_button",
                   className="my-button-class mx-auto d-block"),

    ],
        id="simple_request_toast",
        header="Simple pipeline request",
        header_style={"font-size": "25px", 'background-color': "#017b70",
                      'color': 'white'},
        is_open=True,
        className="my-toast"
    )


def advanced_request():
    return dbc.Toast([
        pipeline_notification(comp_id="advanced_pipe_notification"),
        html.H6(
            f"Pipeline for segmentation and/or classification (prediction) "
            f"and analysis of data."),
        html.H6(
            f"Choosing multiple Segmentation or Prediction algorithms "
            f"will create a matrix of jobs (multiple jobs)."),
        html.Br(), html.Br(),

        dbc.Accordion([
            title_accord_item(),

            dbc.AccordionItem([
                dbc.Checklist(
                    options=[
                        {"label": "dcevent version=latest", "value": 1},
                    ],
                    value=[1],
                    switch=True,
                    labelCheckedClassName="text-success",
                    inputCheckedClassName="border border-success bg-success",
                ),
            ],
                title="dcevent version",
            ),
            segment_accord_item(),
            bg_corr_sub_accord_item(),
            gating_opt_accord_item(),
            further_opt_accord_item(),

            input_data_accord_item()

        ],
            # style={"width": "60rem"},
        ),
        html.Br(), html.Br(), html.Br(), html.Br(),
        dbc.Button("Create pipeline",
                   id="create_advanced_pipeline_button",
                   className="my-button-class mx-auto d-block"),

    ],
        id="advanced_request_toast",
        header="Advanced pipeline request",
        header_style={"font-size": "25px", 'background-color': "#017b70",
                      'color': 'white'},
        # style={"width": "20rem"},
        is_open=True,
        className="my-toast"
    )


#
# @callback(Output("open_issue_card", "children"),
#           Input("create_simple_pipeline_button", "n_clicks"),
#           )
# def update_gitlab_open_issues(click):
#     card_child = [dbc.Col(card, width=4) for card in cards]
#
#     return card_child


# @callback(
#     Output("open_issue_card", "children"),
#     [Input("simple_request_store", "data")],
# )
# def render_navlinks(request_data):
#     print(request_data)
#     request_cards = request_data or []
#     return request_cards
#
#
# @callback(
#     Output("simple_request_store", "data"),
#     [Input("create_simple_pipeline_button", "n_clicks")],
#     [State("simple_request_store", "data")],
# )
# def add_store_request_card(n_clicks, request_data):
#     if n_clicks:
#         request_card = dbc.Toast([
#             html.P("raghava")
#         ],
#             header="request 1",
#         )
#         request_data = request_data or []
#         request_data.append(request_card)
#         print(request_data)
#     return request_data

@callback(Output("simple_pipe_notification", "is_open"),
          Input("create_simple_pipeline_button", "n_clicks"),
          State("simple_pipe_notification", "is_open")
          )
def simple_request_notification(click, popup):
    if click:
        return not popup
    return popup
    # return create_gitlab_issue()


@callback(Output("advanced_pipe_notification", "is_open"),
          Input("create_advanced_pipeline_button", "n_clicks"),
          State("advanced_pipe_notification", "is_open")
          )
def advanced_request_notification(click, popup):
    if click:
        return not popup
    return popup
    # return create_gitlab_issue()
