from dash import html, dcc
import dash_bootstrap_components as dbc


def header_comp(text):
    return html.H6(text)


def paragraph_comp(text, middle=False):
    style = {"text-align": "center"}
    return html.P(text, style=style if middle else {})


def line_breaks(times=1):
    return [html.Br() for i in range(times)]


def horizontal_line_comp(width=50):
    return html.Hr(style={"width": f"{width}rem"})


def text_input_comp(comp_id, placeholder, width=50):
    return html.Div(
        dbc.Input(
            id=comp_id,
            disabled=False,
            type="text",
            placeholder=placeholder,
            class_name="dbc_input",
            style={"width": f"{width}rem"}
        ),
        className="row justify-content-center",
    )


def num_searchbar_comp(comp_id, min, max, step, default, width=6):
    return dbc.Input(
        id=comp_id,
        disabled=False,
        min=min, max=max, step=step,
        value=default,
        type="number",
        placeholder="Enter a number...",
        style={"width": f"{width}rem"}
    )


def dropdown_searchbar_comp(comp_id, option_list, defaults_list):
    option_list = sorted(option_list)
    defaults_list = sorted(defaults_list)
    options = [{"label": op, "value": op} for op in option_list]
    defaults = [op for op in defaults_list]
    return dbc.Select(
        id=comp_id,
        disabled=False,
        options=options,
        value=defaults,
        style={"width": "6rem"}
    )


def checklist_comp(comp_id, option_list, defaults_list):
    option_list = sorted(option_list)
    defaults_list = sorted(defaults_list)
    options = [{"label": op, "value": op} for op in option_list]
    defaults = [op for op in defaults_list]
    return dbc.Checklist(
        options=options,
        id=comp_id,
        value=defaults,
        switch=True,
        labelCheckedClassName="text-success",
        inputCheckedClassName="border border-success bg-success",
    )


def upload_comp(comp_id):
    return dcc.Upload(
        id=comp_id,
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        className="dcc-upload",
        multiple=True
    )


def popup_comp(comp_id):
    return dbc.Modal([
        dbc.ModalHeader(
            dbc.ModalTitle("Pipeline Status"), close_button=True
        ),
        dbc.ModalBody("Pipeline request has been submitted!")
    ],
        id=comp_id,
        centered=True,
        is_open=False,
        style={'color': 'white'}
    )


def groupby_horizontal(elements, width=2):
    columns = [dbc.Col(e, width=width) for e in elements]
    return dbc.Row(columns)
