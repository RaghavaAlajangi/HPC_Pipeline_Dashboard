from contextvars import copy_context

import dash_bootstrap_components as dbc
import pytest
from dash import no_update
from dash._callback_context import context_value
from dash._utils import AttributeDict

from dashboard.pages.page_simple import (
    collect_simple_pipeline_params,
    fetch_and_show_unet_models,
    simple_page_layout,
    simple_request_submission_popup,
    simple_segmentation_section,
    toggle_and_cache_params,
    toggle_simple_create_pipeline_button,
)


def test_simple_title_section():
    """Test simple_title_section type"""
    assert isinstance(simple_page_layout("/test_path/"), dbc.Toast)


def test_simple_segmentation_section():
    """Test simple_segmentation_section type"""
    assert isinstance(simple_segmentation_section(), dbc.AccordionItem)


def test_show_and_cache_segment_options_callback():
    """Test segmentation method selection"""

    def run_callback():
        return fetch_and_show_unet_models(
            unet_click=["mlunet"],
        )

    # Run the callback within the appropriate context
    ctx = copy_context()
    check_boxes = ctx.run(run_callback)

    assert isinstance(check_boxes, dbc.Row)


@pytest.mark.parametrize(
    "callback_function, args, expected",
    [
        (
            # Test case 1: expand togglable components with relevant click
            # and cache user selected parameters.
            toggle_and_cache_params,
            # Inputs:
            {
                "unet_click": ["mlunet"],
                "unet_value": "test_model_file",
                "legacy_click": ["legacy: Legacy thresholding with OpenCV"],
                "legacy_key": "thresh",
                "legacy_value": -5,
                "classifier_click": [],
                "reproduce_click": [],
                "nframe_click": [],
                "nframe_value": 10000,
            },
            # Expected Outputs:
            {
                "cache_simple_params": {
                    "mlunet": {"model_file": "test_model_file"},
                    "legacy: Legacy thresholding with OpenCV": {"thresh": -5},
                },
                "simple_unet_toggle": {"display": "block"},
                "simple_legacy_toggle": {"display": "block"},
                "simple_nframe_toggle": {"display": "block"},
            },
        ),
        (
            # Test case 2: no action when togglable components are not clicked
            # and dont cache any parameters
            toggle_and_cache_params,
            # Inputs:
            {
                "unet_click": [],
                "unet_value": None,
                "legacy_click": [],
                "legacy_key": "thresh",
                "legacy_value": -5,
                "classifier_click": [],
                "reproduce_click": [],
                "nframe_click": [],
                "nframe_value": 10000,
            },
            # Expected Outputs:
            {
                "cache_simple_params": {},
                "simple_unet_toggle": {"display": "none"},
                "simple_legacy_toggle": {"display": "none"},
                "simple_nframe_toggle": {"display": "none"},
                "simple_legacy_options": {"display": "none"},
            },
        ),
    ],
)
def test_toggle_and_cache_params_callback(callback_function, args, expected):
    """Test togglable options expansion, contraction, and caching user
    selected parameters when a user clicks on respective switches switchs."""
    response = callback_function(**args)
    print(response[0])
    print("-" * 50)
    print(expected["cache_simple_params"])
    assert response[0] == expected["cache_simple_params"]


@pytest.mark.parametrize(
    "callback_function, args, expected",
    [
        (
            # Test case 1: enable the 'create pipleine button' when all the
            # required entries are given (author name, title, input file/s,
            # and segmentation method)
            toggle_simple_create_pipeline_button,
            # Inputs:
            {
                "author_name": "test_username",
                "title": "test_title",
                "selected_rows": [{"filepath": "test1.rtdc"}],
                "cached_params": {"legacy": {"thresh": "-6"}},
            },
            # Expected Outputs:
            {"create_simple_pipeline_button": False},
        ),
        (
            # Test case 2: disable the 'create pipleine button', if any of the
            # required entries are missing.
            toggle_simple_create_pipeline_button,
            # Inputs:
            {
                "author_name": "test_username",
                "title": "",  # No title is given
                "selected_rows": [{"filepath": "test1.rtdc"}],
                "cached_params": {},  # No segmentation is provided
            },
            # Expected Outputs:
            {"create_simple_pipeline_button": True},
        ),
    ],
)
def test_toggle_simple_create_pipeline_button_callback(
    callback_function, args, expected
):
    """Test toggle_simple_create_pipeline_button activation and deactivation"""
    response = callback_function(**args)
    assert response == expected["create_simple_pipeline_button"]


@pytest.mark.parametrize(
    "callback_function, triggered_inputs, args, expected",
    [
        (
            # Test case 1: When user clicks on 'create pipeline' button, a
            # popup message box will be opened.
            simple_request_submission_popup,
            # Stimulate Inputs
            [{"prop_id": "simple_create_pipeline_click.n_clicks"}],
            # Inputs:
            {
                "_": 1,
                "cached_template": {
                    "title": "test without notes create",
                    "description": "test description",
                },
                "close_popup": 0,
                "popup": False,
            },
            # Expected Outputs:
            {"simple_popup": True},
        ),
        (
            # Test case 2: After the popup message is opened up, user clicks
            # on the 'close' button inside the popup message box.
            simple_request_submission_popup,
            # Stimulate Inputs
            [{"prop_id": "simple_popup_close.n_clicks"}],
            # Inputs:
            {
                "_": 0,
                "cached_template": {
                    "title": "testing",
                    "description": "test description",
                },
                "close_popup": 1,
                "popup": True,
            },
            # Expected Outputs:
            {"simple_popup": False},
        ),
        (
            # Test case 3: No clcik on 'create pipeline' button and 'close'
            # button --> no action
            simple_request_submission_popup,
            # Stimulate Inputs
            [{"prop_id": "dummy_click.n_clicks"}],
            # Inputs:
            {
                "_": 0,
                "cached_template": {
                    "title": "testing",
                    "description": "test description",
                },
                "close_popup": 0,
                "popup": False,
            },
            # Expected Outputs:
            {"simple_popup": False},
        ),
    ],
)
def test_simple_request_submission_popup_callback(
    callback_function, triggered_inputs, args, expected
):
    """Test simple_request_submission_popup callback behavior."""

    def run_callback():
        context_value.set(
            AttributeDict(**{"triggered_inputs": triggered_inputs})
        )
        return callback_function(**args)

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert response == expected["simple_popup"]


@pytest.mark.parametrize(
    "callback_function, args, expected",
    [
        (
            # Test case 1: if pipeline author, title, and input file/s are
            # provided, the function should update the pipeline template
            # with the user options and return it.
            collect_simple_pipeline_params,
            # Inputs:
            {
                "author_name": "test_username",
                "simple_title": "test_title",
                "cached_params": {
                    "legacy: Legacy thresholding with OpenCV": {"thresh": -6},
                    "mlunet: UNET": {"model_file": "model_checkpoint"},
                    "bloody-bunny_g1_bacae: Bloody Bunny": None,
                },
                "selected_rows": [
                    {"filepath": "HSMFS: test1.rtdc"},
                    {"filepath": "HSMFS: test2.rtdc"},
                ],
            },
            # Expected Outputs:
            {
                "cache_simple_template": {
                    "title": "test_title",
                    "description": """
                    - **Segmentation**\n
                        - dcevent version\n
                            - [ ] dcevent version=latest\n
                        - Segmentation Algorithm\n
                            - [x] mlunet: UNET\n
                                - [x] model_file=model_checkpoint\n
                            - [x] legacy: Legacy thresholding with OpenCV\n
                                - [x] thresh=-6\n
                            - [ ] thresh: thresholding segmentation\n
                            - [ ] watershed: Watershed algorithm\n
                            - [ ] std: Standard-deviation-based thresholding\n
                            - Further Options\n
                                - [ ] --reproduce\n
                                - [ ] --num-frames\n
                    - **Prediction**\n
                        - Classification Model\n
                            - [x] bloody-bunny_g1_bacae: Bloody Bunny\n
                    - **Post Analysis**\n
                      - [ ] Benchmarking\n
                      - [ ] Scatter Plot\n
                    - **Data to Process**\n
                      - [x] HSMFS: test1.rtdc\n
                      - [x] HSMFS: test2.rtdc\n
                    - __Author__\n
                       - [x] username=test_username
                    """,
                }
            },
        ),
        (
            # Test case 2: if any of the values (pipeline author, title,
            # and input file/s) are missing, the function should return None
            collect_simple_pipeline_params,
            # Inputs:
            {
                "author_name": "",  # No username
                "simple_title": "test_title",
                "cached_params": {
                    "legacy: Legacy thresholding with OpenCV": {"thresh": -6},
                    "mlunet: UNET": {"model_file": "model_checkpoint"},
                    "bloody-bunny_g1_bacae: Bloody Bunny": None,
                },
                "selected_rows": [
                    {"filepath": "HSMFS: test1.rtdc"},
                    {"filepath": "HSMFS: test2.rtdc"},
                ],
            },
            # Expected Outputs:
            {"cache_simple_template": no_update},
        ),
        (
            # Test case 3: check for num-frames and reproduce flag options
            collect_simple_pipeline_params,
            # Inputs:
            {
                "author_name": "test_username",
                "simple_title": "test_title",
                "cached_params": {
                    "legacy: Legacy thresholding with OpenCV": {"thresh": -6},
                    "mlunet: UNET": {"model_file": "model_checkpoint"},
                    "bloody-bunny_g1_bacae: Bloody Bunny": None,
                    "--reproduce": None,
                    "--num-frames": 12000,
                },
                "selected_rows": [
                    {"filepath": "HSMFS: test1.rtdc"},
                    {"filepath": "HSMFS: test2.rtdc"},
                ],
            },
            # Expected Outputs:
            {
                "cache_simple_template": {
                    "title": "test_title",
                    "description": """
                    - **Segmentation**\n
                        - dcevent version\n
                            - [ ] dcevent version=latest\n
                        - Segmentation Algorithm\n
                            - [x] mlunet: UNET\n
                                - [x] model_file=model_checkpoint\n
                            - [x] legacy: Legacy thresholding with OpenCV\n
                                - [x] thresh=-6\n
                            - [ ] thresh: thresholding segmentation\n
                            - [ ] watershed: Watershed algorithm\n
                            - [ ] std: Standard-deviation-based thresholding\n
                            - Further Options\n
                                - [x] --reproduce\n
                                - [x] --num-frames 12000\n
                    - **Prediction**\n
                        - Classification Model\n
                            - [x] bloody-bunny_g1_bacae: Bloody Bunny\n
                    - **Post Analysis**\n
                      - [ ] Benchmarking\n
                      - [ ] Scatter Plot\n
                    - **Data to Process**\n
                      - [x] HSMFS: test1.rtdc\n
                      - [x] HSMFS: test2.rtdc\n
                    - __Author__\n
                       - [x] username=test_username
                    """,
                }
            },
        ),
    ],
)
def test_collect_simple_pipeline_params_callback(
    callback_function, args, expected
):
    """Test collection of user input and update simple pipeline template"""

    response = callback_function(**args)

    if response is not no_update:
        assert "description" in response.keys()
        assert "title" in response.keys()
        res_desc_str = response["description"]
        exp_desc_str = expected["cache_simple_template"]["description"]

        # Normalize and split lines
        res_desc_lines = [
            line.strip() for line in res_desc_str.split("\n") if line.strip()
        ]
        exp_desc_lines = [
            line.strip() for line in exp_desc_str.split("\n") if line.strip()
        ]
        # Check each expected line
        for line in exp_desc_lines:
            assert any(
                line in res_line for res_line in res_desc_lines
            ), f"Missing: {line}"
