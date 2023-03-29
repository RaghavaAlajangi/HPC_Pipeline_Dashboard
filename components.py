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


def chat_box(chat, box_width=66, gap=15):
    """
    The chat_box function takes a list of strings and returns a Dash
    Bootstrap Card object. The card is styled to look like the chat box
    in WhatsApp, with each message in its own card body. The function also
    checks for links within the messages and converts them into
    clickable hyperlinks.
    Parameters
    ----------
    chat: list of str
        Pass the chat data into the function
    box_width: int
        Set the width of the chat box
    gap: int
        Adjust the spacing between messages
    Returns
    -------
    A card with the messages in a chat
    """
    comments = [html.Div(
        dbc.Card([
            dbc.CardBody(web_link_check(msg), style={"padding": "0"})
        ],
            className="message-box",
        ),
        style={"margin-bottom": f"{gap}px",
               "border": "0"}
    )
        for msg in chat]

    return dbc.Card(comments, body=True,
                    style={"width": f"{box_width}rem"})


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


def group_accordion(accord_items, width, middle=False, comp_id="none"):
    """
    The group_accordion function takes a list of accordion items, and
    returns a html.Div containing a Bootstrap Accordion component with the
    given width (in rems). The middle parameter is optional, and if set to
    True will add the &quot;row justify-content-center&quot; className to
    the returned div.
    Parameters
    ----------
    accord_items
        Pass in a list of accordion items
    width
        Set the width of the accordion
    middle
        Center the accordion
    comp_id
        Identify the component
    Returns
    -------
    A group of accordions
    """
    accord_items = [a for a in accord_items]
    return html.Div(
        dbc.Accordion(accord_items,
                      id=comp_id,
                      style={"width": f"{width}rem"}
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


def horizontal_line_comp(width=50):
    return html.Hr(style={"width": f"{width}rem"})


def line_breaks(times=1):
    br_list = [html.Br() for i in range(times)]
    return html.Div(children=br_list)


def loading_comp(children):
    """
    The loading_comp function is a wrapper for the dcc.Loading component,
    which is used to display a loading indicator while data is being fetched
    from the server. The function takes in one argument, children, which
    should be an array of components that will be displayed once the data
    has been loaded.
    Parameters
    ----------
    children
        Specify the children of the loading component
    Returns
    -------
    A loading component, which is a div that contains a dcc
    """
    return dcc.Loading(type="default", color="#017b70", children=children)


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


def progressbar_comp(comp_id):
    return dbc.Progress(id=comp_id, value=0, color="success",
                        animated=True, striped=True,
                        style={"transform": "translate(10%, 50%)"})


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
