import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

from ..gitlab import get_gitlab_instances
from .common_components import (
    button_comp,
    checklist_comp,
    divider_line_comp,
    form_group_input,
    hover_card,
    line_breaks,
)
from .hsm_grid import create_hsm_grid, create_show_grid


def title_section(dropdown_id, text_id):
    """Creates a title section for the pipeline."""
    # Get the members list from request repo
    req_gitlab, _ = get_gitlab_instances()
    return dbc.AccordionItem(
        title="Title (required)",
        children=[
            html.Div(
                dbc.InputGroup(
                    children=[
                        dbc.Select(
                            placeholder="Select Username",
                            id=dropdown_id,
                            options=[
                                {
                                    "label": member.name,
                                    "value": member.username,
                                }
                                for member in req_gitlab.get_project_members()
                            ],
                            style={"width": "18%"},
                        ),
                        dbc.Input(
                            type="text",
                            id=text_id,
                            placeholder="Enter title of the pipeline...",
                            style={"width": "72%"},
                            class_name="custom-placeholder",
                        ),
                    ],
                    style={"width": "90%"},
                ),
                className="row justify-content-center",
            )
        ],
    )


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
                        description="If you select wrong sample, "
                        "segmentation might not be reliable. If you select "
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


def post_analysis_section(option_id):
    """Creates the post analysis section of the pipeline."""
    return dbc.AccordionItem(
        title="Post Analysis (Not Implemented)",
        children=[
            checklist_comp(
                comp_id=option_id,
                options=[
                    {
                        "label": "Benchmarking",
                        "value": "Benchmarking",
                        "disabled": True,
                    },
                    {
                        "label": "Scatter Plot",
                        "value": "Scatter Plot",
                        "disabled": True,
                    },
                ],
            )
        ],
    )


def cell_classifier_section(classifier_id):
    """Creates the cell classifier section of the pipeline."""
    return dbc.AccordionItem(
        title="Classification Model",
        children=[
            html.P(
                "- First generation cell classification algorithm. Not "
                "stable performance!",
                style={"color": "red"},
            ),
            checklist_comp(
                comp_id=classifier_id,
                options=[
                    {
                        "label": "Bloody Bunny (cell classifier)",
                        "value": "bloody-bunny_g1_bacae: Bloody Bunny",
                        "disabled": False,
                    },
                ],
                defaults=[],
            ),
        ],
    )


def input_data_selection_section():
    """Creates the input data section of the pipeline."""
    return dbc.AccordionItem(
        title="Data to Process",
        item_id="hsm_accord",
        children=[
            create_hsm_grid(),
            line_breaks(times=2),
        ],
    )


def input_data_display_section(show_grid_id, button_id):
    return html.Div(
        [
            line_breaks(times=2),
            create_show_grid(show_grid_id=show_grid_id),
            line_breaks(times=2),
            button_comp(
                label="Create pipeline",
                disabled=True,
                comp_id=button_id,
            ),
            line_breaks(times=2),
            dbc.Alert(
                "Note: Username, pipeline title, and data paths are "
                "mandatory fields to activate 'Create Pipeline' button.",
                color="warning",
                style={
                    "color": "black",
                    "width": "fit-content",
                    "margin": "auto",
                },
            ),
            line_breaks(times=3),
        ]
    )


def further_options_section(
    reproduce_flag_id, num_frames_id, num_frames_toggle_id, num_frames_value
):
    """Creates the further option section of the pipeline."""
    # Get the default parameters from request repo
    request_gitlab, _ = get_gitlab_instances()
    dcevent_params = request_gitlab.get_defaults()
    foptions = dcevent_params["further_options"]
    reproduce_def = foptions["reproduce"]["default"]
    reproduce_flag = True if reproduce_def.lower() == "true" else False
    return dbc.AccordionItem(
        title="Further Options",
        children=[
            # --reproduce checkbox (switch)
            checklist_comp(
                comp_id=reproduce_flag_id,
                options=[
                    {
                        "label": "--reproduce",
                        "value": "--reproduce",
                        "disabled": False,
                    }
                ],
                defaults=["--reproduce"] if reproduce_flag else [],
            ),
            divider_line_comp(),
            html.P(
                "- If you want to run the analysis with a fixed number of "
                "frames, use this option. (by default, all the frames are "
                "used)",
                style={"color": "red"},
            ),
            # --num-frames checkbox (switch)
            checklist_comp(
                comp_id=num_frames_id,
                options=[
                    {
                        "label": "--num-frames",
                        "value": "--num-frames",
                        "disabled": False,
                    }
                ],
                defaults=["--num-frames"] if reproduce_flag else [],
            ),
            # --num-frames option (input box to enter a number)
            html.Ul(
                id=num_frames_toggle_id,
                children=[
                    form_group_input(
                        comp_id=num_frames_value,
                        label="frames",
                        label_key="--num-frames",
                        min=foptions["num_frames"]["min"],
                        max=foptions["num_frames"]["max"],
                        step=foptions["num_frames"]["step"],
                        default=foptions["num_frames"]["default"],
                    ),
                ],
            ),
        ],
    )


def format_params(switch, values, keys=None):
    """Helper function to format given parameters"""
    if keys and isinstance(values, list):
        params = {k: v for k, v in zip(keys, values)}
        return {switch[0]: params} if switch else {}
    else:
        return {switch[0]: values} if switch else {}
