import re

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify


def button_comp(label, comp_id, type="primary", disabled=False):
    return dbc.Button(
        label,
        id=comp_id,
        color=type,
        disabled=disabled,
        className=(
            "my-button-class mx-auto d-block" if type == "primary" else {}
        ),
    )


def chat_box(messages, gap=18):
    """Creates a list of dbc.Card items from a dictionary of comments.

    Parameters
    ----------
        messages: dict
            Pass the messages dataframe to the chat_box function
        gap: int
            Set the vertical space between each comment card

    Returns
    -------
        A dbc.ListGroupItem with a list of dbc.Card components
    """
    comment_cards = []

    for comment, author, date in zip(
        messages["comments"], messages["comment_authors"], messages["dates"]
    ):
        comment_card = dbc.Card(
            children=[
                dmc.Stack(
                    children=[
                        html.P(
                            web_link_check(comment),
                            style={
                                "color": "white",
                                "fontSize": 15,
                                "margin": "0",
                            },
                        ),
                        html.Code(
                            date,
                            lang="python",
                            style={
                                "color": "black",
                                "fontSize": 12,
                                "margin": "1",
                            },
                        ),
                    ],
                    spacing=0,
                ),
                dbc.Badge(
                    author,
                    pill=False,
                    color="primary",
                    text_color="white",
                    style={"font-weight": "normal"},
                    className="position-absolute top-0 start-100 "
                    "translate-middle",
                ),
            ],
            className="message-box",
            style={
                "margin-bottom": f"{gap}px",
                "margin-top": f"{gap}px",
                "border": "0",
            },
        )
        comment_cards.append(comment_card)
    return dbc.ListGroupItem(
        children=comment_cards,
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
    options = [
        {"label": k, "value": k, "disabled": v} for k, v in options.items()
    ]
    defaults = [op for op in defaults]
    return dbc.Checklist(
        options=options,
        id=comp_id,
        value=defaults,
        switch=True,
        labelCheckedClassName="text-success",
        inputCheckedClassName="border border-success bg-success",
    )


def create_badge(content, color):
    return dbc.Badge(
        children=content, className="me-2", color=color, text_color="black"
    )


def divider_line_comp(variant="dashed", pad=10):
    return html.Div(
        dmc.Divider(variant=variant),
        style={"padding-top": f"{pad}px", "padding-bottom": f"{pad}px"},
    )


def form_group_dropdown(
    comp_id, label, label_key, options, default, box_width=6, gap=2
):
    options = [{"label": op, "value": op} for op in sorted(options)]
    dropdown = dbc.Select(
        id=comp_id,
        disabled=False,
        options=options,
        value=default,
        key=label_key,
        style={"width": f"{box_width}rem"},
    )
    return dbc.Form(
        dbc.Row(
            [
                dbc.Label(label, width=gap),
                dbc.Col(dropdown),
            ]
        )
    )


def form_group_input(
    comp_id, label, label_key, min, max, step, default, box_width=6, gap=2
):
    dbc_input = dbc.Input(
        id=comp_id,
        disabled=False,
        min=min,
        max=max,
        step=step,
        value=default,
        type="number",
        key=label_key,
        placeholder="Enter a number...",
        style={"width": f"{box_width}rem"},
    )
    return dbc.Form(dbc.Row([dbc.Label(label, width=gap), dbc.Col(dbc_input)]))


def create_list_group(children, horizontal=False):
    return dbc.ListGroup(
        children=[dbc.ListGroupItem(child) for child in children],
        horizontal=horizontal,
    )


def group_accordion(children, middle=False, open_first=False, comp_id="none"):
    """Takes a list of children, and returns an accordion with those children.
    The middle parameter is used to center the accordion on the page. The
    open_first parameter determines whether the first item in the accordion
    will be opened by default."""
    accord_items = [a for a in children]
    return html.Div(
        dbc.Accordion(
            children=accord_items,
            id=comp_id,
            className="my-accordion",
            start_collapsed=not open_first,
        ),
        className="row justify-content-center" if middle else "",
    )


def header_comp(text, indent=0, middle=False):
    if middle:
        style = {"text-align": "center"}
    elif not middle and indent > 0:
        style = {"marginLeft": f"{indent}px"}
    else:
        style = {}
    return html.Div(html.H6(text, style=style))


def hover_card(target, notes):
    return dmc.HoverCard(
        children=[
            dmc.HoverCardTarget(target),
            dmc.HoverCardDropdown(
                dmc.Text(notes, size="sm", color="black"),
            ),
        ],
        position="right",
        shadow="xs",
        width=400,
        withArrow=True,
        transition="pop",
    )


def line_breaks(times=1):
    br_list = [html.Br() for _ in range(times)]
    return html.Div(children=br_list)


def paragraph_comp(text, comp_id="dummy", indent=0, middle=False):
    if middle:
        style = {"text-align": "center"}
    elif not middle and indent > 0:
        style = {"marginLeft": f"{indent}rem"}
    else:
        style = {}
    return dbc.Label(id=comp_id, children=text, style=style)


def progressbar_comp(comp_id, height=20, width=80):
    return dbc.Progress(
        id=comp_id,
        value=0,
        striped=True,
        animated=True,
        color="success",
        style={
            "height": f"{height}px",
            "width": f"{width}%",
            "margin": "0 auto",
        },
    )


def popup_comp(comp_id, refresh_path, text):
    """Creates a modal (notification window) that will appear when the user
    clicks on a targeted button. The refresh_path argument sets where we want
    to redirect after the user closes out of this popup window."""

    return dbc.Modal(
        [
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
                    href=refresh_path,
                )
            ),
        ],
        id=comp_id,
        centered=True,
        is_open=False,
        keyboard=True,
        backdrop="static",
        style={"color": "white"},
    )


def web_link(label, url):
    return html.A(label, href=url, target="_blank", className="custom-link")


def web_link_check(text):
    """Replaces any web links in the given input string with clickable link.

    Parameters
    ----------
    text: str
        Pass the text to be checked for links
    Returns
    -------
        A list of strings and web_link objects
    """
    regex_exp = r"(https?://[^\s]+)"

    # Find all links and their indices
    matches = re.finditer(regex_exp, text)
    links = [(match.group(), match.start(), match.end()) for match in matches]

    # If no links found, return original text
    if not links:
        return text

    # Initialize variables
    replaced_text_parts = []
    start_idx = 0

    # Iterate over each link found
    for link, start, end in links:
        # Add text before the link
        replaced_text_parts.append(text[start_idx:start])

        # Add clickable link
        replaced_text_parts.append(web_link(label=link, url=link))

        # Update start index for next iteration
        start_idx = end

    # Add remaining text after last link
    replaced_text_parts.append(text[start_idx:])

    return replaced_text_parts


def unet_segmentation_section(unet_switch_id, unet_toggle_id, unet_options_id):
    """Creates a section for U-Net segmentation options.

    Parameters
    ----------
    unet_switch_id: str
        The ID for the U-Net switch component.
    unet_toggle_id: str
        The ID for the U-Net toggle container.
    unet_options_id: str
        The ID for the U-Net options radio group.

    Returns
    -------
    A Div containing the U-Net segmentation section.
    """
    return html.Div(
        [
            dmc.Group(
                children=[
                    # UNet checkbox (switch)
                    dbc.Checklist(
                        options=[
                            {
                                "label": "U-Net Segmentation",
                                "value": "mlunet: UNET",
                            },
                        ],
                        id=unet_switch_id,
                        switch=True,
                        value=[],
                        labelCheckedClassName="text-success",
                        inputCheckedClassName="border-success bg-success",
                    ),
                    # UNet question mark icon and hover info
                    hover_card(
                        target=DashIconify(
                            icon="mage:message-question-mark-round-fill",
                            color="yellow",
                            width=20,
                        ),
                        notes="A deep learning based image segmentation "
                        "method.\n Warning: U-Net is trained on "
                        "specific cell types. When you select correct "
                        "option from below, appropriate model file "
                        "will be used for segmentation.",
                    ),
                ],
                spacing=5,
            ),
            # UNet segmentation options
            html.Ul(
                id=unet_toggle_id,
                children=[
                    dmc.RadioGroup(
                        id=unet_options_id,
                        label="Select your Device and Sample",
                        description="If you select wrong sample, segmentation "
                        "might not be reliable. If you select "
                        "wrong device pipeline will fail.",
                        orientation="vertical",
                        withAsterisk=True,
                        offset="md",
                        mb=10,
                        spacing=10,
                    )
                ],
            ),
        ]
    )


def unet_segmentation_options(unet_options):
    """Creates radio group options for U-Net segmentation.

    Parameters
    ----------
    unet_options: dict
        A dictionary containing the U-Net segmentation options.

    Returns
    -------
    A list of Radio components for U-Net segmentation options.
    """
    radio_groups = {"naiad": [], "accelerator": []}

    for model_ckp, meta in unet_options.items():
        if meta["device"] in radio_groups:
            radio_groups[meta["device"]].extend(
                [
                    dmc.Radio(
                        label=meta["label"], value=model_ckp, color="green"
                    ),
                    line_breaks(1),
                ]
            )

    accelerator_card = dbc.Card(
        dbc.CardBody(
            [
                html.H5("Accelerator Devices:", className="card-title"),
                html.P("- Only available for image size 250x80 pixels"),
                *radio_groups["accelerator"],
            ]
        ),
        color="success",
        outline=True,
    )

    naiad_card = dbc.Card(
        dbc.CardBody(
            [
                html.H5("Naiad Devices:", className="card-title"),
                html.P("- For image size 320x80 pixels"),
                *radio_groups["naiad"],
            ]
        ),
        color="success",
        outline=True,
    )

    cards = dbc.Row(
        [
            dbc.Col(accelerator_card, width=5),
            dbc.Col(naiad_card, width=5),
        ]
    )

    return cards
