from dash import html, dcc
import dash_bootstrap_components as dbc


def header_comp(text, indent=0, middle=False):
    if middle:
        style = {"text-align": "center"}
    elif not middle and indent > 0:
        style = {"marginLeft": f"{indent}px"}
    else:
        style = {}
    return html.Div(html.H6(text, style=style))


def paragraph_comp(text, indent=0, middle=False):
    if middle:
        style = {"text-align": "center"}
    elif not middle and indent > 0:
        style = {"marginLeft": f"{indent}px"}
    else:
        style = {}
    return html.P(text, style=style)


def line_breaks(times=1):
    br_list = [html.Br() for i in range(times)]
    return html.Div(children=br_list)


def button_comp(label, comp_id, type="primary"):
    return dbc.Button(label, id=comp_id, color=type,
                      className="my-button-class mx-auto d-block"
                      if type == "primary" else {})


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
            "Drag and Drop or ",
            html.A("Select Files")
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
        style={"color": "white"}
    )


def dropdown_menu_comp(name, components, indent=0, middle=False):
    if middle:
        style = {"text-align": "center"}
    elif not middle and indent > 0:
        style = {"marginLeft": f"{indent}px"}
    else:
        style = {}
    options = [dbc.DropdownMenuItem([c]) for c in components]
    return html.Div(
        dbc.DropdownMenu(options, label=name),
        style=style
    )


def groupby_rows(components, width=2):
    rows = [dbc.Col(e, width=width) for e in components]
    return dbc.Row(rows)


def groupby_columns(components, width=10):
    columns = dbc.Col([e for e in components], width=width)
    return dbc.Row(columns)


def group_accordion(accord_items, width, middle=False, comp_id="none"):
    accord_items = [a for a in accord_items]
    return html.Div(
        dbc.Accordion(accord_items,
                      id=comp_id,
                      style={"width": f"{width}rem"}
                      ),
        className="row justify-content-center" if middle else ""
    )


def chat_box(chat, box_width=66, gap=15):
    """
    The chat_box function takes a list of strings and returns a chat box.
    Parameters
    ----------
    chat
        Store the messages that will be displayed in the chat box
    box_width
        Set the width of the chat box
    gap
        Set the margin-bottom of each message
    Returns
    -------
        A list of comments
    """
    comments = [html.Div(
        dbc.Card([
            dbc.CardBody(msg, style={"padding": "0"})
        ],
            className="message-box",
        ),
        style={"margin-bottom": f"{gap}px",
               "border": "0"}
    )
        for msg in chat]

    return dbc.Card(comments, body=True,
                    style={"width": f"{box_width}rem"})


def loading_comp(children):
    return html.Div(
        dcc.Loading(type="dot", color="#017b70", children=children),
        className="row justify-content-center"
    )
