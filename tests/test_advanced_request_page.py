from contextvars import copy_context

import dash_bootstrap_components as dbc
import pytest
from dash._callback_context import context_value
from dash._utils import AttributeDict

from dashboard.pages.page_advanced import (
    advanced_page_layout,
    advanced_request_submission_popup,
    advanced_segmentation_section,
    background_correction_section,
    collect_advanced_pipeline_params,
    fetch_and_show_unet_models,
    gating_options_section,
    toggle_advanced_create_pipeline_button,
    toggle_and_cache_params,
)


@pytest.mark.parametrize(
    "section_function, expected_type",
    [
        (advanced_segmentation_section, dbc.AccordionItem),
        (background_correction_section, dbc.AccordionItem),
        (gating_options_section, dbc.AccordionItem),
    ],
)
def test_section_types(section_function, expected_type):
    """Test section types"""
    assert isinstance(section_function(), expected_type)


def test_advanced_page_layout():
    """Test advanced_page_layout layout"""
    assert isinstance(advanced_page_layout("/test_refresh_path/"), dbc.Toast)


def test_show_and_cache_unet_model_meta_callback():
    """Test unet segmentation method selection"""

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
                "leg_keys": [
                    "thresh",
                    "blur",
                    "binaryops",
                    "diff_method",
                    "clear_border",
                    "fill_holes",
                    "closing_disk",
                ],
                "leg_values": ["-6", "0", "5", "1", True, True, "5"],
                "thresh_click": ["thresh: thresholding segmentation"],
                "thresh_keys": [
                    "thresh",
                    "clear_border",
                    "fill_holes",
                    "closing_disk",
                ],
                "thresh_values": ["-6", True, True, "5"],
                "water_click": ["watershed: Watershed algorithm"],
                "water_keys": ["clear_border", "fill_holes", "closing_disk"],
                "water_values": [True, True, "5"],
                "std_click": ["std: Standard-deviation-based thresholding"],
                "std_keys": ["clear_border", "fill_holes", "closing_disk"],
                "std_values": [True, True, "5"],
                "romed_click": [
                    "rollmed: Rolling median RT-DC background image "
                    "computation"
                ],
                "romed_keys": ["clear_border", "fill_holes", "closing_disk"],
                "romed_values": [True, True, "5"],
                "spmed_click": [
                    "sparsemed: Sparse median background correction "
                    "with cleansing"
                ],
                "spmed_keys": [
                    "kernel_size",
                    "split_time",
                    "thresh_cleansing",
                    "frac_cleansing",
                    "offset_correction",
                ],
                "spmed_values": [200, 1, 0, 0.8, True],
                "ngate_click": ["norm gating"],
                "ngate_keys": ["online_gates", "size_thresh_mask"],
                "ngate_values": [False, 0],
                "classifier_click": [],
                "reproduce_click": [],
                "nframe_click": [],
                "nframe_value": 10000,
            },
            # Expected Outputs:
            {
                "cache_advance_params": {
                    "mlunet": {"model_file": "test_model_file"},
                    "legacy: Legacy thresholding with OpenCV": {
                        "thresh": "-6",
                        "blur": "0",
                        "binaryops": "5",
                        "diff_method": "1",
                        "clear_border": True,
                        "fill_holes": True,
                        "closing_disk": "5",
                    },
                    "thresh: thresholding segmentation": {
                        "thresh": "-6",
                        "clear_border": True,
                        "fill_holes": True,
                        "closing_disk": "5",
                    },
                    "watershed: Watershed algorithm": {
                        "clear_border": True,
                        "fill_holes": True,
                        "closing_disk": "5",
                    },
                    "std: Standard-deviation-based thresholding": {
                        "clear_border": True,
                        "fill_holes": True,
                        "closing_disk": "5",
                    },
                    "rollmed: Rolling median RT-DC background image "
                    "computation": {
                        "clear_border": True,
                        "fill_holes": True,
                        "closing_disk": "5",
                    },
                    "sparsemed: Sparse median background correction "
                    "with cleansing": {
                        "kernel_size": 200,
                        "split_time": 1,
                        "thresh_cleansing": 0,
                        "frac_cleansing": 0.8,
                        "offset_correction": True,
                    },
                    "norm gating": {
                        "online_gates": False,
                        "size_thresh_mask": 0,
                    },
                },
                "advance_unet_toggle": {"display": "block"},
                "legacy_toggle": {"display": "block"},
                "thresh_toggle": {"display": "block"},
                "water_toggle": {"display": "block"},
                "std_toggle": {"display": "block"},
                "romed_toggle": {"display": "block"},
                "spmed_toggle": {"display": "block"},
                "ngate_toggle": {"display": "block"},
                "advance_nframe_toggle": {"display": "block"},
            },
        ),
        (
            # Test case 2: no action when togglable components are not clicked
            # and dont cache any parameters
            # is not clicked
            toggle_and_cache_params,
            # Inputs:
            {
                "unet_click": [],  # No click on unet switch
                "unet_value": None,
                "legacy_click": [],  # No click on legacy switch
                "leg_keys": [
                    "thresh",
                    "blur",
                    "binaryops",
                    "diff_method",
                    "clear_border",
                    "fill_holes",
                    "closing_disk",
                ],
                "leg_values": ["-6", "0", "5", "1", True, True, "5"],
                "thresh_click": [],  # No click on thresh switch
                "thresh_keys": [
                    "thresh",
                    "clear_border",
                    "fill_holes",
                    "closing_disk",
                ],
                "thresh_values": ["-6", True, True, "5"],
                "water_click": [],  # No click on watershed switch
                "water_keys": ["clear_border", "fill_holes", "closing_disk"],
                "water_values": [True, True, "5"],
                "std_click": [],  # No click on std switch
                "std_keys": ["clear_border", "fill_holes", "closing_disk"],
                "std_values": [True, True, "5"],
                "romed_click": [],  # No click on rollmed switch
                "romed_keys": ["clear_border", "fill_holes", "closing_disk"],
                "romed_values": [True, True, "5"],
                "spmed_click": [
                    "sparsemed: Sparse median background correction "
                    "with cleansing"
                ],  # Default click on sparsemed switch
                "spmed_keys": [
                    "kernel_size",
                    "split_time",
                    "thresh_cleansing",
                    "frac_cleansing",
                    "offset_correction",
                ],
                "spmed_values": [200, 1, 0, 0.8, True],
                "ngate_click": [],  # No click on norm gate switch
                "ngate_keys": ["online_gates", "size_thresh_mask"],
                "ngate_values": [False, 0],
                "classifier_click": [],  # No click on bloodybunny switch
                "reproduce_click": [],  # No click on reproduce switch
                "nframe_click": [],  # No click on num_frames switch
                "nframe_value": 10000,
            },
            # Expected Outputs:
            {
                "cache_advance_params": {
                    "sparsemed: Sparse median background correction "
                    "with cleansing": {
                        "kernel_size": 200,
                        "split_time": 1,
                        "thresh_cleansing": 0,
                        "frac_cleansing": 0.8,
                        "offset_correction": True,
                    },
                },
                "advance_unet_toggle": {"display": "none"},
                "legacy_toggle": {"display": "none"},
                "thresh_toggle": {"display": "none"},
                "water_toggle": {"display": "none"},
                "std_toggle": {"display": "none"},
                "romed_toggle": {"display": "none"},
                "spmed_toggle": {"display": "block"},  # only spasremed is open
                "ngate_toggle": {"display": "none"},
                "advance_nframe_toggle": {"display": "none"},
            },
        ),
    ],
)
def test_toggle_and_cache_params_callback(callback_function, args, expected):
    """Test togglable options expansion, contraction, and caching user
    selected parameters when a user clicks on respective switches switchs."""
    response = callback_function(**args)
    assert response[0] == expected["cache_advance_params"]


@pytest.mark.parametrize(
    "callback_function, triggered_inputs, args, expected",
    [
        (
            # Test case 1: When user clicks on 'create pipeline' button, a
            # popup message box will be opened.
            advanced_request_submission_popup,
            # Stimulate Inputs
            [{"prop_id": "advance_create_pipeline_click.n_clicks"}],
            # Inputs:
            {
                "_": 1,
                "cached_adv_temp": {
                    "title": "test without notes create",
                    "description": "test description",
                },
                "close_popup": 0,
                "popup": False,
            },
            # Expected Outputs:
            {"advance_popup": True},
        ),
        (
            # Test case 2: After the popup message is opened up, user clicks
            # on the 'close' button inside the popup message box.
            advanced_request_submission_popup,
            # Stimulate Inputs
            [{"prop_id": "advance_popup_close.n_clicks"}],
            # Inputs:
            {
                "_": 0,
                "cached_adv_temp": {
                    "title": "testing",
                    "description": "test description",
                },
                "close_popup": 1,
                "popup": True,
            },
            # Expected Outputs:
            {"advance_popup": False},
        ),
        (
            # Test case 3: No clcik on 'create pipeline' button and 'close'
            # button --> no action
            advanced_request_submission_popup,
            # Stimulate Inputs
            [{"prop_id": "dummy_click.n_clicks"}],
            # Inputs:
            {
                "_": 0,
                "cached_adv_temp": {
                    "title": "testing",
                    "description": "test description",
                },
                "close_popup": 0,
                "popup": False,
            },
            # Expected Outputs:
            {"advance_popup": False},
        ),
    ],
)
def test_advanced_request_submission_popup_callback(
    callback_function, triggered_inputs, args, expected
):
    """Test advanced request submission popup callback behavior."""

    def run_callback():
        context_value.set(
            AttributeDict(**{"triggered_inputs": triggered_inputs})
        )
        return callback_function(**args)

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert response == expected["advance_popup"]


@pytest.mark.parametrize(
    "callback_function, args, expected",
    [
        (
            # Test case 1: enable the 'create pipleine button' when all the
            # required entries are given (author name, title, input file/s,
            # and any segmentation method)
            toggle_advanced_create_pipeline_button,
            # Inputs:
            {
                "author_name": "test_username",
                "title": "test_title",
                "selected_rows": [{"filepath": "test1.rtdc"}],
                "cached_params": {
                    "mlunet: UNET": {"model_file": "test_checkpoint"}
                },
            },
            # Expected Outputs:
            {"create_advanced_pipeline_button": False},
        ),
        (
            # Test case 2: disable the 'create pipleine button', if any of the
            # required entries are missing.
            toggle_advanced_create_pipeline_button,
            # Inputs:
            {
                "author_name": "test_username",
                "title": "",  # No title is given
                "selected_rows": [{"filepath": "test1.rtdc"}],
                "cached_params": {
                    "mlunet: UNET": {"model_file": "test_checkpoint"}
                },
            },
            # Expected Outputs:
            {"create_advanced_pipeline_button": True},
        ),
    ],
)
def test_toggle_advanced_create_pipeline_button_callback(
    callback_function, args, expected
):
    """Test create_pipeline_button activation and deactivation."""
    response = callback_function(**args)
    assert response == expected["create_advanced_pipeline_button"]


@pytest.mark.parametrize(
    "callback_function, args, expected",
    [
        (
            # Test case 1: if pipeline author, title, and input file/s are
            # provided, the function should update the pipeline template
            # with the user options and return it.
            collect_advanced_pipeline_params,
            # Inputs:
            {
                "author_name": "test_username",
                "advance_title": "test_title",
                "cache_params": {
                    "mlunet: UNET": {"model_file": "test_checkpoint"},
                    "norm gating": {
                        "online_gates": False,
                        "size_thresh_mask": 0,
                    },
                    "sparsemed: Sparse median background correction with "
                    "cleansing": {
                        "kernel_size": 200,
                        "split_time": 1,
                        "thresh_cleansing": 0,
                        "frac_cleansing": 0.8,
                    },
                },
                "selected_rows": [{"filepath": "HSMFS: test.rtdc"}],
            },
            # Expected Outputs:
            {
                "cache_advanced_template": {
                    "title": "test_title",
                    "description": """
- **Segmentation**\n
    - dcevent version\n
        - [ ] dcevent version=latest\n
    - Segmentation Algorithm\n
        - [x] mlunet: UNET\n
            - [x] model_file=test_checkpoint\n
        - [ ] legacy: Legacy thresholding with OpenCV\n
            - [ ] thresh=-6\n
            - [ ] blur=0\n
            - [ ] binaryops=5\n
            - [ ] diff_method=1\n
            - [ ] clear_border=True\n
            - [ ] fill_holes=True\n
            - [ ] closing_disk=5\n
        - [ ] thresh: thresholding segmentation\n
            - [ ] clear_border=True\n
            - [ ] closing_disk=2\n
            - [ ] fill_holes=True\n
            - [ ] thresh=-6\n
        - [ ] watershed: Watershed algorithm\n
            - [ ] clear_border=True\n
            - [ ] fill_holes=True\n
            - [ ] closing_disk=5\n
        - [ ] std: Standard-deviation-based thresholding\n
            - [ ] clear_border=True\n
            - [ ] fill_holes=True\n
            - [ ] closing_disk=5\n
    - Background Correction/Subtraction Method\n
        - [ ] rollmed: Rolling median RT-DC background image computation\n
            - [ ] kernel_size=100\n
            - [ ] batch_size=10000\n
        - [x] sparsemed: Sparse median background correction with cleansing\n
            - [x] kernel_size=200\n
            - [x] split_time=1\n
            - [x] thresh_cleansing=0\n
            - [x] frac_cleansing=0.8\n
    - Available gating options\n
        - [x] norm gating\n
        - [x] online_gates=False\n
            - [x] size_thresh_mask=0\n
    - Further Options\n
        - [ ] --reproduce\n
        - [ ] --num-frames\n
- **Prediction**\n
    - Classification Model\n
        - [ ] bloody-bunny_g1_bacae: Bloody Bunny\n
- **Post Analysis**\n
    - [ ] Benchmarking\n
    - [ ] Scatter Plot\n
- **Data to Process**\n
    - [x] HSMFS: test.rtdc\n
- __Author__\n
    - [x] username=test_user
        """,
                }
            },
        ),
        (
            # Test case 2: if any of the values (pipeline author, title,
            # and input file/s) are missing, the function should return None
            collect_advanced_pipeline_params,
            # Inputs:
            {
                "author_name": "test_username",
                "advance_title": "",  # No title is provided ()
                "cache_params": {
                    "--num-frames": 200,
                    "--reproduce": None,
                    "sparsemed: Sparse median background correction with "
                    "cleansing": {
                        "kernel_size": 200,
                        "split_time": 1,
                        "thresh_cleansing": 0,
                        "frac_cleansing": 0.8,
                    },
                    "norm gating": {
                        "online_gates": False,
                        "size_thresh_mask": 0,
                    },
                },
                "selected_rows": [{"filepath": "HSMFS: test.rtdc"}],
            },
            # Expected Outputs:
            {"cache_advanced_template": None},
        ),
        (
            # Test case 3: check for num-frames and reproduce flag options
            collect_advanced_pipeline_params,
            # Inputs:
            {
                "author_name": "test_username",
                "advance_title": "test_title",
                "cache_params": {
                    "mlunet: UNET": {"model_file": "test_checkpoint"},
                    "--num-frames": 200,
                    "--reproduce": None,
                    "sparsemed: Sparse median background correction with "
                    "cleansing": {
                        "kernel_size": 200,
                        "split_time": 1,
                        "thresh_cleansing": 0,
                        "frac_cleansing": 0.8,
                    },
                    "norm gating": {
                        "online_gates": False,
                        "size_thresh_mask": 0,
                    },
                },
                "selected_rows": [{"filepath": "HSMFS: test.rtdc"}],
            },
            # Expected Outputs:
            {
                "cache_advanced_template": {
                    "title": "test_title",
                    "description": """
- **Segmentation**\n
    - dcevent version\n
        - [ ] dcevent version=latest\n
    - Segmentation Algorithm\n
        - [x] mlunet: UNET\n
            - [x] model_file=test_checkpoint\n
        - [ ] legacy: Legacy thresholding with OpenCV\n
            - [ ] thresh=-6\n
            - [ ] blur=0\n
            - [ ] binaryops=5\n
            - [ ] diff_method=1\n
            - [ ] clear_border=True\n
            - [ ] fill_holes=True\n
            - [ ] closing_disk=5\n
        - [ ] thresh: thresholding segmentation\n
            - [ ] clear_border=True\n
            - [ ] closing_disk=2\n
            - [ ] fill_holes=True\n
            - [ ] thresh=-6\n
        - [ ] watershed: Watershed algorithm\n
            - [ ] clear_border=True\n
            - [ ] fill_holes=True\n
            - [ ] closing_disk=5\n
        - [ ] std: Standard-deviation-based thresholding\n
            - [ ] clear_border=True\n
            - [ ] fill_holes=True\n
            - [ ] closing_disk=5\n
    - Background Correction/Subtraction Method\n
        - [ ] rollmed: Rolling median RT-DC background image computation\n
            - [ ] kernel_size=100\n
            - [ ] batch_size=10000\n
        - [x] sparsemed: Sparse median background correction with cleansing\n
            - [x] kernel_size=200\n
            - [x] split_time=1\n
            - [x] thresh_cleansing=0\n
            - [x] frac_cleansing=0.8\n
    - Available gating options\n
        - [x] norm gating\n
        - [x] online_gates=False\n
            - [x] size_thresh_mask=0\n
    - Further Options\n
        - [x] --reproduce\n
        - [x] --num-frames 200\n
- **Prediction**\n
    - Classification Model\n
        - [ ] bloody-bunny_g1_bacae: Bloody Bunny\n
- **Post Analysis**\n
    - [ ] Benchmarking\n
    - [ ] Scatter Plot\n
- **Data to Process**\n
    - [x] HSMFS: test.rtdc\n
- __Author__\n
    - [x] username=test_user
        """,
                }
            },
        ),
    ],
)
def test_collect_advanced_pipeline_params_callback(
    callback_function, args, expected
):
    """Test collection of user input and update advanced pipeline template"""

    response = callback_function(**args)

    if response:
        assert "description" in response.keys()
        assert "title" in response.keys()
        res_desc_str = response["description"]
        exp_desc_str = expected["cache_advanced_template"]["description"]

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
