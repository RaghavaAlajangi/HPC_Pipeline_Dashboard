from dash import html, dcc
import dash_bootstrap_components as dbc
import re


def button_comp(label, comp_id, type="primary", disabled=False):
    return dbc.Button(
        label, id=comp_id, color=type,
        disabled=disabled,
        className="my-button-class mx-auto d-block"
        if type == "primary" else {}
    )


def chat_box(messages, gap=15):
    comment_cards = []

    for comment, date in zip(messages["comments"], messages["dates"]):
        comment_card = dbc.Card(
            [
                dbc.CardBody(web_link_check(comment), style={"padding": "0"}),
                dbc.Badge(
                    date,
                    color="secondary",
                    text_color="white",
                    className="position-absolute bottom-0 start-100",
                ),
            ],
            className="message-box",
            style={"margin-bottom": f"{gap}px", "border": "0"},
        )
        comment_cards.append(comment_card)

    return dbc.Card(
        dbc.CardBody(comment_cards),
        style={
            "max-height": "30rem",
            "width": "100%",
            "overflow-y": "scroll",
            "overflowX": "hidden",
        },
    )


def checklist_comp(comp_id, options, defaults=None):
    """Creates a checklist component.
    Parameters
    ----------
    comp_id: str
        Identify the component in the dom
    options: dict
        Checklist options with their values and whether they are disabled
        or not. The keys are labels and values are booleans indicating whether
        they should be disabled or not (True = Disabled).  This argument is
        required.
    defaults
        default selections (optional)
    Returns
    -------
    A checklist component
    """
    if defaults is None:
        defaults = []
    options = [{"label": k, "value": k, "disabled": v} for k, v in
               options.items()]
    defaults = [op for op in defaults]
    return dbc.Checklist(
        options=options,
        id=comp_id,
        value=defaults,
        switch=True,
        labelCheckedClassName="text-success",
        inputCheckedClassName="border border-success bg-success",
    )


def divider_line_comp(width=100, middle=True):
    return html.Div(
        html.Hr(style={"width": f"{width}%"}),
        className="row justify-content-center" if middle else ""
    )


def dropdown_menu_comp(name, options, indent=0, middle=False):
    """
    The dropdown_menu_comp function takes in a name, components, indent
    and middle. The name is the title of the dropdown menu. The components
    are what will be displayed in the dropdown menu. The indent is how far
    from the left side of your screen you want to place it (in pixels).
    If you set middle to True then it will center itself on your screen.
    Parameters
    ----------
    name: str
        Set the name of the dropdown menu
    options: str or dash components
        Create the dropdown menu options
    indent: int
        Indent the dropdown menu
    middle: int
        Center the dropdown menu
    Returns
    -------
    A dropdown menu with a list of components
    """
    if middle:
        style = {"text-align": "center"}
    elif not middle and indent > 0:
        style = {"marginLeft": f"{indent}px"}
    else:
        style = {}
    options = [dbc.DropdownMenuItem([c]) for c in options]
    return html.Div(
        dbc.DropdownMenu(options, label=name),
        style=style
    )


def dropdown_searchbar_comp(comp_id, options, defaults):
    """
    The dropdown_searchbar_comp function takes in three arguments
    Parameters
    ----------
    comp_id
        Identify the component
    options
        Create the dropdown options
    defaults
        Set the default value of the dropdown menu
    Returns
    -------
    A dropdown searchbar component
    """
    options = sorted(options)
    defaults = sorted(defaults)
    options = [{"label": op, "value": op} for op in options]
    defaults = [op for op in defaults]
    return dbc.Select(
        id=comp_id,
        disabled=False,
        options=options,
        value=defaults,
        style={"width": "6rem"}
    )


def form_group_dropdown(comp_id, label, options, default, box_width=6, gap=2):
    options = [{"label": op, "value": op} for op in sorted(options)]
    dropdown = dbc.Select(
        id=comp_id,
        disabled=False,
        options=options,
        value=default,
        key=label,
        style={"width": f"{box_width}rem"}
    )
    return dbc.Form(
        dbc.Row(
            [
                dbc.Label(label, width=gap),
                dbc.Col(dropdown),
            ]
        )
    )


def form_group_input(comp_id, label, min, max, step, default, box_width=6,
                     gap=2):
    input = dbc.Input(
        id=comp_id,
        disabled=False,
        min=min, max=max, step=step,
        value=default,
        type="number",
        key=label,
        placeholder="Enter a number...",
        style={"width": f"{box_width}rem"}
    )
    return dbc.Form(
        dbc.Row(
            [
                dbc.Label(label, width=gap),
                dbc.Col(input),
            ]
        )
    )


def group_items(items, horizontal=False):
    return dbc.ListGroup(
        [dbc.ListGroupItem(item) for item in items],
        horizontal=horizontal
    )


def group_accordion(children, middle=False, open_first=False, comp_id="none"):
    """Takes a list of children, and returns an accordion with those children.
    The middle parameter is used to center the accordion on the page. The
    open_first parameter determines whether the first item in the accordion
    will be opened by default."""
    accord_items = [a for a in children]
    return html.Div(
        dbc.Accordion(children=accord_items,
                      id=comp_id,
                      className="my-accordion",
                      start_collapsed=not open_first,
                      ),
        className="row justify-content-center" if middle else ""
    )


def header_comp(text, indent=0, middle=False):
    if middle:
        style = {"text-align": "center"}
    elif not middle and indent > 0:
        style = {"marginLeft": f"{indent}px"}
    else:
        style = {}
    return html.Div(html.H6(text, style=style))


def line_breaks(times=1):
    br_list = [html.Br() for _ in range(times)]
    return html.Div(children=br_list)


def drop_input_button(comp_id, drop_options, disable_drop=False,
                      drop_placeholder="Source", default_drop=None,
                      input_placeholder="text", disable_input=False,
                      disable_button=False,
                      with_button=True, width=100
                      ):
    default_drop = default_drop if default_drop else []
    return html.Div(
        dbc.InputGroup([
            dbc.Select(
                placeholder=drop_placeholder,
                id=f"{comp_id}_drop",
                options=[
                    {"label": i, "value": i} for i in drop_options
                ],
                value=default_drop,
                style={"width": "15%"},
                disabled=disable_drop
            ),
            dbc.Input(
                type="text", id=f"{comp_id}_text",
                placeholder=input_placeholder,
                style={"width": "75%"},
                class_name="custom-placeholder",
                disabled=disable_input,
            ),
            dbc.Button(
                "Add", id=f"{comp_id}_button", color="info",
                style={"width": "10%"},
                disabled=disable_button
            ) if with_button else None,
        ],
            style={"width": f"{width}%"}
        ),
        className="row justify-content-center",
    )


def loading_comp(children):
    """
    The loading_comp function takes in a list of children and returns a
    dbc.Spinner component with the given children and color set to
    &quot;success&quot;. The size is set to &quot;sm&quot; by default.
    Parameters
    ----------
    children
        Pass the children of the component
    Returns
    -------
    A spinner component
    """
    return dbc.Spinner(size="sm", children=children, color="success")


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


def paragraph_comp(text, comp_id="dummy", indent=0, middle=False):
    if middle:
        style = {"text-align": "center"}
    elif not middle and indent > 0:
        style = {"marginLeft": f"{indent}rem"}
    else:
        style = {}
    return dbc.Label(id=comp_id, children=text, style=style)


def progressbar_comp(comp_id, width=80):
    return dbc.Progress(id=comp_id, value=0, striped=True,
                        animated=True, color="success",
                        style={"width": f"{width}%", "margin": "0 auto"}
                        )


def popup_comp(comp_id, refresh_path, text):
    """Creates a modal (notification window) that will appear when the user
    clicks on a targeted button. The refresh_path argument sets where we want
    to redirect after the user closes out of this popup window."""

    return dbc.Modal([
        dbc.ModalHeader(
            dbc.ModalTitle("Pipeline Status"), close_button=False
        ),
        dbc.ModalBody(text),
        dbc.ModalFooter(
            html.A(
                dbc.Button(
                    "Close",
                    id=f"{comp_id}_close",
                    className="ms-auto",
                    n_clicks=0,
                ),
                href=refresh_path
            )
        ),
    ],
        id=comp_id,
        centered=True,
        is_open=False,
        keyboard=True,
        backdrop="static",
        style={"color": "white"}
    )


def text_input_comp(comp_id, placeholder, width=50, middle=True):
    return html.Div(
        dbc.Input(
            id=comp_id,
            disabled=False,
            type="text",
            placeholder=placeholder,
            class_name="custom-placeholder",
            style={"width": f"{width}rem"}
        ),
        className="row justify-content-center" if middle else "",
    )


def upload_comp(comp_id):
    """
    The upload_comp function is a helper function that creates an upload
    component. It takes in the id of the component and returns a
    dcc.Upload object with children, className, and multiple attributes
    set to specific values.
    Parameters
    ----------
    comp_id
        Identify the component in the callback function
    Returns
    -------
    A dcc.Upload component
    """
    return dcc.Upload(
        id=comp_id,
        children=html.Div([
            "Drag and Drop or ",
            html.A("Select Files")
        ]),
        className="dcc-upload",
        multiple=True
    )


def web_link(label, url):
    return html.A(label, href=url, target="_blank",
                  style={"text-decoration": "none"}
                  )


def web_link_check(text):
    """
    The web_link_check function takes a string as input and returns the
    same string with any web links replaced by a clickable link. The
    function uses regular expressions to find all instances of web links
    in the input text, then replaces each instance with an HTML hyperlink
    tag that will display as a clickable link when
    rendered.
    Parameters
    ----------
    text: str
        Pass the text to be checked for links
    Returns
    -------
    A list of strings and web_link objects
    """
    regex_exp = r"(?P<url>https?://[^\s]+)"
    links = re.findall(regex_exp, text)
    split_text = re.split(regex_exp, text)
    if len(links) == 0:
        return text
    else:
        for link in links:
            link_idx = split_text.index(link)
            split_text[link_idx] = web_link(label=link, url=link)
            return split_text
