from contextvars import copy_context

import dash_bootstrap_components as dbc
import pytest
from dash import no_update
from dash._callback_context import context_value
from dash._utils import AttributeDict

from dashboard.pages.page_simple import (
    collect_simple_pipeline_params,
    show_and_cache_segment_options,
    simple_page_layout,
    simple_request_submission_popup,
    simple_segmentation_section,
    toggle_legacy_options,
    toggle_simple_create_pipeline_button,
    toggle_unet_options,
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
        return show_and_cache_segment_options(
            unet_click=["mlunet"],
            measurement_type="model_checkpoint",
            legacy_click=["legacy"],
            legacy_thresh="-2",
        )

    # Run the callback within the appropriate context
    ctx = copy_context()
    check_boxes, segm_opt = ctx.run(run_callback)

    assert isinstance(check_boxes, dbc.Row)
    assert isinstance(segm_opt, dict)
    assert "mlunet" in segm_opt.keys()


@pytest.mark.parametrize(
    "callback_function, args, expected",
    [
        (
            # Test case 1: unet options expansion
            toggle_unet_options,
            # Inputs:
            {"unet_click": ["mlunet"]},
            # Expected Outputs:
            {"simple_unet_options": {"display": "block"}},
        ),
        (
            # Test case 2: unet options contraction
            toggle_unet_options,
            # Inputs:
            {"unet_click": []},
            # Expected Outputs:
            {"simple_unet_options": {"display": "none"}},
        ),
    ],
)
def test_toggle_unet_options_callback(callback_function, args, expected):
    """Test unet options expansion and contraction when a user clicks on unet
    switch"""
    response = callback_function(**args)
    assert type(response) is type(expected)
    assert response["display"] == expected["simple_unet_options"]["display"]


@pytest.mark.parametrize(
    "callback_function, args, expected",
    [
        (
            # Test case 1: legacy options expansion only when legacy switch is
            # clicked
            toggle_legacy_options,
            # Inputs:
            {"legacy_click": ["legacy"]},
            # Expected Outputs:
            {"simple_legacy_options": {"display": "block"}},
        ),
        (
            # Test case 2: legacy options contraction when legacy switch is
            # not clicked
            toggle_legacy_options,
            # Inputs:
            {"legacy_click": []},
            # Expected Outputs:
            {"simple_legacy_options": {"display": "none"}},
        ),
    ],
)
def test_toggle_legacy_options_callback(callback_function, args, expected):
    """Test legacy options expansion and contraction when a user clicks on
    legacy switch"""
    response = callback_function(**args)
    assert type(response) is type(expected)
    assert response["display"] == expected["simple_legacy_options"]["display"]


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
                "selected_files": [{"filepath": "test1.rtdc"}],
                "cached_seg_options": {"legacy": {"thresh": "-6"}},
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
                "selected_files": [{"filepath": "test1.rtdc"}],
                "cached_seg_options": {},  # No segmentation is provided
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
            [{"prop_id": "create_simple_pipeline_button.n_clicks"}],
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
                "cached_seg_options": {
                    "legacy": {"thresh": -6},
                    "mlunet": {"model_file": "model_checkpoint"},
                },
                "cached_num_frames": {},
                "simple_classifier": ["bloody-bunny_g1_bacae"],
                "reproduce_flag": [],
                "selected_files": [
                    {"filepath": "HSMFS: test1.rtdc"},
                    {"filepath": "HSMFS: test2.rtdc"},
                ],
            },
            # Expected Outputs:
            {
                "cache_simple_template": {
                    "title": "test_title",
                    "description": """
                    **Segmentation**
                        - [x] mlunet
                        - [x] model_file=model_checkpoint
                    **Classification Model
                        - [x] bloody-bunny_g1_bacae
                    **Data to Process
                        - [x] HSMFS: test1.rtdc"
                        - [x] HSMFS: test2.rtdc
                    __Author_name__
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
                "author_name": "",  # No user is provided
                "simple_title": "test_title",
                "cached_seg_options": {
                    "legacy": {"thresh": -6},
                    "mlunet": {"model_file": "model_checkpoint"},
                },
                "cached_num_frames": {},
                "simple_classifier": ["bloody-bunny_g1_bacae"],
                "reproduce_flag": [],
                "selected_files": [
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
                "author_name": "test user",  # No user is provided
                "simple_title": "test_title",
                "cached_seg_options": {
                    "legacy": {"thresh": -6},
                    "mlunet": {"model_file": "model_checkpoint"},
                },
                "cached_num_frames": {"--num-frames": {"--num-frames": 500}},
                "simple_classifier": ["bloody-bunny_g1_bacae"],
                "reproduce_flag": ["--reproduce"],
                "selected_files": [
                    {"filepath": "HSMFS: test1.rtdc"},
                    {"filepath": "HSMFS: test2.rtdc"},
                ],
            },
            # Expected Outputs:
            {
                "cache_simple_template": {
                    "title": "test_title",
                    "description": """
                    **Segmentation**
                        - [x] mlunet
                        - [x] model_file=model_checkpoint
                        - [x] --reproduce
                        - [x] --num-frames
                          - [x] --nume-frames=500
                    **Classification Model
                        - [x] bloody-bunny_g1_bacae
                    **Data to Process
                        - [x] HSMFS: test1.rtdc"
                        - [x] HSMFS: test2.rtdc
                    __Author_name__
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
        red_desc = response["description"]
        exp_desc = expected["cache_simple_template"]["description"]

        for line in exp_desc:
            assert line in red_desc
