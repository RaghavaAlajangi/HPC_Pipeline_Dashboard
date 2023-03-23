from dash import html, dcc
import dash_bootstrap_components as dbc


def pipeline_notification(comp_id):
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Pipeline Status"), close_button=True),
        dbc.ModalBody("Pipeline request has been submitted!")
    ],
        id=comp_id,
        style={'color': 'white'},
        centered=True,
        is_open=False
    )


def title_accord_item():
    return dbc.AccordionItem([
        dbc.Input(id="advanced_request_title",
                  placeholder="Type title...", type="text",
                  style={"width": "50rem"})
    ],
        title="Title (required)",
    )


def input_data_accord_item():
    return dbc.AccordionItem([
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

    )


def dcevent_accord_item():
    return dbc.AccordionItem([
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


def segment_accord_item():
    return dbc.AccordionItem([
        dbc.Checklist(
            options=[
                {"label": "MLUNet", "value": 1},
            ],
            value=[1],
            switch=True,
            labelCheckedClassName="text-success",
            inputCheckedClassName="border border-success bg-success",
        ),
        html.Hr(style={"width": "50rem"}),
        dbc.Checklist(
            options=[
                {"label": "legacy: Legacy thresholding with OpenCV",
                 "value": 1},
            ],
            value=[1],
            switch=True,
            labelCheckedClassName="text-success",
            inputCheckedClassName="border border-success bg-success",
        ),
        # html.Hr(style={"width": "50rem"}),

        dbc.Row([
            dbc.Col(
                html.P('thresh'),
                width=2,
            ),
            dbc.Col(
                dbc.Input(type="number", min=-10, max=10, step=1,
                          value=-6,
                          style={"width": "6rem"}),
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.P('blur'),
                width=2,
            ),
            dbc.Col(
                dbc.Input(type="number", min=0, max=10, step=1,
                          value=0,
                          style={"width": "6rem"}),
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.P('binaryops'),
                width=2,
            ),
            dbc.Col(
                dbc.Input(type="number", min=0, max=10, step=1,
                          value=5,
                          style={"width": "6rem"}),
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.P('diff_method'),
                width=2,
            ),
            dbc.Col(
                dbc.Input(type="number", min=0, max=10, step=1,
                          value=1,
                          style={"width": "6rem"}),
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.P('clear_border'),
                width=2,
            ),
            dbc.Col(
                dbc.Select(
                    options=[
                        {"label": "True", "value": "1"},
                        {"label": "False", "value": "2"},
                    ],
                    value=["1"],
                    style={"width": "6rem"}
                )
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.P('fill_holes'),
                width=2,
            ),
            dbc.Col(
                dbc.Select(
                    options=[
                        {"label": "True", "value": "1"},
                        {"label": "False", "value": "2"},
                    ],
                    value=["1"],
                    style={"width": "6rem"}
                )
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.P('closing_disk'),
                width=2,
            ),
            dbc.Col(
                dbc.Input(type="number", min=0, max=10, step=1,
                          value=5,
                          style={"width": "6rem"})
            )
        ]),
        html.Hr(style={"width": "50rem"}),
        dbc.Checklist(
            options=[
                {"label": "watershed: Watershed algorithm",
                 "value": 1},
            ],
            value=[1],
            switch=True,
            labelCheckedClassName="text-success",
            inputCheckedClassName="border border-success bg-success",
        ),
        dbc.Row([
            dbc.Col(
                html.P('clear_border'),
                width=2,
            ),
            dbc.Col(
                dbc.Select(
                    options=[
                        {"label": "True", "value": "1"},
                        {"label": "False", "value": "2"},
                    ],
                    value=["1"],
                    style={"width": "6rem"}
                )
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.P('fill_holes'),
                width=2,
            ),
            dbc.Col(
                dbc.Select(
                    options=[
                        {"label": "True", "value": "1"},
                        {"label": "False", "value": "2"},
                    ],
                    value=["1"],
                    style={"width": "6rem"}
                )
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.P('closing_disk'),
                width=2,
            ),
            dbc.Col(
                dbc.Input(type="number", min=0, max=10, step=1,
                          value=5,
                          style={"width": "6rem"})
            )
        ]),
        html.Hr(style={"width": "50rem"}),
        dbc.Checklist(
            options=[
                {"label": "std: Standard-deviation-based thresholding",
                 "value": 1},
            ],
            value=[1],
            switch=True,
            labelCheckedClassName="text-success",
            inputCheckedClassName="border border-success bg-success",
        ),
        dbc.Row([
            dbc.Col(
                html.P('clear_border'),
                width=2,
            ),
            dbc.Col(
                dbc.Select(
                    options=[
                        {"label": "True", "value": "1"},
                        {"label": "False", "value": "2"},
                    ],
                    value=["1"],
                    style={"width": "6rem"}
                )
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.P('fill_holes'),
                width=2,
            ),
            dbc.Col(
                dbc.Select(
                    options=[
                        {"label": "True", "value": "1"},
                        {"label": "False", "value": "2"},
                    ],
                    value=["1"],
                    style={"width": "6rem"}
                )
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.P('closing_disk'),
                width=2,
            ),
            dbc.Col(
                dbc.Input(type="number", min=0, max=10, step=1,
                          value=5,
                          style={"width": "6rem"})
            )
        ]),
    ],
        title="Segmentation Algorithm",
    )


def bg_corr_sub_accord_item():
    return dbc.AccordionItem([
        dbc.Checklist(
            options=[
                {"label": f"rollmed: Rolling median RT-DC "
                          f"background image computation",
                 "value": 1},
            ],
            value=[1],
            switch=True,
            labelCheckedClassName="text-success",
            inputCheckedClassName="border border-success bg-success",
        ),
        dbc.Row([
            dbc.Col(
                html.P('kernel_size'),
                width=2,
            ),
            dbc.Col(
                dbc.Input(type="number", min=50, max=500, step=1,
                          value=100,
                          style={"width": "6rem"})
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.P('batch_size'),
                width=2,
            ),
            dbc.Col(
                dbc.Input(type="number", min=1000, max=100000,
                          step=100, value=10000,
                          style={"width": "6rem"})
            )
        ]),
        html.Hr(style={"width": "50rem"}),

        dbc.AccordionItem([
            dbc.Checklist(
                options=[
                    {"label": f"sparsemed: Sparse median background"
                              f" correction with cleansing",
                     "value": 1},
                ],
                value=[1],
                switch=True,
                labelCheckedClassName="text-success",
                inputCheckedClassName="border border-success bg-success",
            ),
            dbc.Row([
                dbc.Col(
                    html.P('kernel_size'),
                    width=2,
                ),
                dbc.Col(
                    dbc.Input(type="number", min=50, max=500, step=1,
                              value=100,
                              style={"width": "6rem"})
                )
            ]),
            dbc.Row([
                dbc.Col(
                    html.P('batch_size'),
                    width=2,
                ),
                dbc.Col(
                    dbc.Input(type="number", min=1000, max=100000,
                              step=1, value=10000,
                              style={"width": "6rem"})
                )
            ]),
            dbc.Row([
                dbc.Col(
                    html.P('thresh_cleansing'),
                    width=2,
                ),
                dbc.Col(
                    dbc.Input(type="number", min=0, max=10,
                              step=1, value=0,
                              style={"width": "6rem"})
                )
            ]),
            dbc.Row([
                dbc.Col(
                    html.P('frac_cleansing'),
                    width=2,
                ),
                dbc.Col(
                    dbc.Input(type="number", min=0, max=1,
                              step=0.1, value=0.8,
                              style={"width": "6rem"})
                )
            ]),
        ]),
    ],
        title="Background Correction / Subtraction Method",
    )


def gating_opt_accord_item():
    return dbc.AccordionItem([
        dbc.Checklist(
            options=[
                {"label": f"norm gating",
                 "value": 1},
            ],
            value=[1],
            switch=True,
            labelCheckedClassName="text-success",
            inputCheckedClassName="border border-success bg-success",
        ),
        dbc.Row([
            dbc.Col(
                html.P('online_gates'),
                width=2,
            ),
            dbc.Col(
                dbc.Select(
                    options=[
                        {"label": "True", "value": "1"},
                        {"label": "False", "value": "2"},
                    ],
                    value=["2"],
                    style={"width": "6rem"}
                )
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.P('size_thresh_mask'),
                width=2,
            ),
            dbc.Col(
                dbc.Input(type="number", min=0, max=10, step=1,
                          value=5,
                          style={"width": "6rem"})
            )
        ]),
    ],
        title="Available gating options",
    )


def further_opt_accord_item():
    return dbc.AccordionItem([
        dbc.Checklist(
            options=[
                {"label": f"--reproduce=False",
                 "value": 1},
            ],
            value=[1],
            switch=True,
            labelCheckedClassName="text-success",
            inputCheckedClassName="border border-success bg-success",
        ),
    ],
        title="Further Options",
    )


def prediction_accord_item():
    return dbc.AccordionItem([
        dbc.Checklist(
            options=[
                {"label": f"dcml version", "value": 1},
            ],
            value=[1],
            switch=True,
            labelCheckedClassName="text-success",
            inputCheckedClassName="border border-success bg-success",
        ),

        dbc.Checklist(
            options=[
                {"label": f"Classification Model", "value": 1},
            ],
            value=[1],
            switch=True,
            labelCheckedClassName="text-success",
            inputCheckedClassName="border border-success bg-success",
        ),
    ],
        title="Prediction",
    ),
