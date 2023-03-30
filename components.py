from dash import html, dcc
import dash_bootstrap_components as dbc
import re


def button_comp(label, comp_id, type="primary"):
    """
    The button_comp function is a helper function that creates a Dash
    Bootstrap Component (dbc) Button.
    Parameters
    ----------
    label
        Set the text of the button
    comp_id
        Identify the button in the callback function
    type
        Determine the color of the button
    Returns
    -------
    A button component with the given label, id and type
    """
    return dbc.Button(label, id=comp_id, color=type,
                      className="my-button-class mx-auto d-block"
                      if type == "primary" else {})


def chat_box(chat, gap=15):
    """
    The chat_box function takes a list of messages and returns a Div
    containing a Card for each message. The Card is styled to look like
    the chat box in WhatsApp, with rounded corners and no border. Each
    message is passed through the web_link_check function before being
    added to the card.
    Parameters
    ----------
    chat
        Pass the chat data to the function
    gap
        Set the margin-bottom of each message
    Returns
    -------
    A div object that contains a list of messages
    """
    comments = [html.Div(
        dbc.Card([
            dbc.CardBody(web_link_check(msg), style={"padding": "0"})
        ],
            className="message-box",
        ),
        style={"margin-bottom": f"{gap}px", "border": "0"},
    )
        for msg in chat]
    return dbc.Card(comments, body=True,
                    style={"max-height": "30rem",
                           "overflow-y": "scroll",
                           "overflowX": "hidden"},
                    className="my-card")


def checklist_comp(comp_id, options, defaults):
    """
    The checklist_comp function takes in three arguments:
    - comp_id: the id of the component, which is used to reference it later.
    - option_list: a list of strings that will be displayed as options for
    the user to select from.
    - defaults_list: a list of strings that are selected by default
    when this component is rendered on screen.
    Parameters
    ----------
    comp_id
        Give the component an id
    options
        Create the options for the checklist
    defaults
        Set the default values of the checkboxes
    Returns
    -------
    A checklist component
    """
    options = sorted(options)
    defaults = sorted(defaults)
    options = [{"label": op, "value": op} for op in options]
    defaults = [op for op in defaults]
    return dbc.Checklist(
        options=options,
        id=comp_id,
        value=defaults,
        switch=True,
        labelCheckedClassName="text-success",
        inputCheckedClassName="border border-success bg-success",
    )


def display_box(drop_value, filelist):
    filelist = html.Ul([
        html.Li(f"{drop_value} :  {name}") for name in filelist
    ])
    return html.Div([
        paragraph_comp(text="Entered List:"),
        dbc.Card(filelist, body=True,
                 style={"max-height": "15rem",
                        "overflow-y": "scroll",
                        "overflowX": "hidden"},
                 className="my-card")
    ])


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


def groupby_columns(components, width=10):
    """
    The groupby_columns function takes a list of components and returns
    a row with the components grouped into columns. The width parameter is
    optional, but defaults to 10. The function will group the components into
    as many columns as needed to fit them all in one row.
    Parameters
    ----------
    components
        Pass in the components that will be grouped together
    width
        Set the width of each column in the row
    Returns
    -------
    A row of column components
    """
    columns = dbc.Col([e for e in components], width=width)
    return dbc.Row(columns)


def groupby_rows(components, width=2):
    """
    The groupby_rows function takes a list of components and groups
    them into rows. The width parameter specifies how many columns each
    row should span. For example, if you have a list of 6 components and
    want to group them into 3-column rows:
    Parameters
    ----------
    components
        Pass in the components to be grouped
    width
        Determine the width of each column in a row
    Returns
    -------
    A row of components
    """
    rows = [dbc.Col(e, width=width) for e in components]
    return dbc.Row(rows)


def group_accordion(accord_items, middle=False, comp_id="none"):
    """
    The group_accordion function takes a list of accordion items and
    returns an HTML Div element containing the accordion. The middle
    parameter is used to determine whether the returned div should
    be centered on the page.The comp_id parameter is used to set an id
    for this component, which can be referenced by other components.
    Parameters
    ----------
    accord_items
        Pass in the accordion items
    middle
        Add a row class to the div that is returned
    comp_id
        Identify the accordion
    Returns
    -------
    The accordion items
    """
    accord_items = [a for a in accord_items]
    return html.Div(
        dbc.Accordion(accord_items,
                      id=comp_id,
                      className="my-accordion"
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
    br_list = [html.Br() for i in range(times)]
    return html.Div(children=br_list)


def input_with_dropdown(comp_id, width=80):
    return html.Div(
        dbc.InputGroup([
            dbc.Select(
                id=f"{comp_id}_drop",
                options=["HSMFS", "DVC", "DCOR", "DCOR-Colab"],
                value="HSMFS",
                style={"width": "20%"}
            ),
            dcc.Input(
                type='text',
                placeholder='Enter file path / ID',
                multiple=True,
                id=f"{comp_id}_text",
                className='form-control',
                style={"width": "80%"}

            ),
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


def paragraph_comp(text, indent=0, middle=False):
    if middle:
        style = {"text-align": "center"}
    elif not middle and indent > 0:
        style = {"marginLeft": f"{indent}px"}
    else:
        style = {}
    return html.P(text, style=style)


def progressbar_comp(comp_id, width=80):
    return dbc.Progress(id=comp_id, value=0, striped=True,
                        animated=True, color="success",
                        style={"width": f"{width}%", "margin": "0 auto"}
                        )


def popup_comp(comp_id):
    """
    The popup_comp function is used to create a modal that will pop up when
    the user clicks on the &quot;Submit&quot; button. The modal will display
    a message indicating that their pipeline request has been submitted.
    Parameters
    ----------
    comp_id
        Identify the modal in the html
    Returns
    -------
    A modal that is centered and has a white background
    """
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
    regex_exp = "(?P<url>https?://[^\s]+)"
    links = re.findall(regex_exp, text)
    split_text = re.split(regex_exp, text)
    if len(links) == 0:
        return text
    else:
        for link in links:
            link_idx = split_text.index(link)
            split_text[link_idx] = web_link(label=link, url=link)
            return split_text
