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
    gating_options_section,
    show_and_cache_unet_model_meta,
    toggle_advanced_create_pipeline_button,
    toggle_legacy_options,
    toggle_norm_gate_options,
    toggle_rollmed_options,
    toggle_sparsemed_options,
    toggle_std_options,
    toggle_thresh_seg_options,
    toggle_unet_options,
    toggle_watershed_options,
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
        return show_and_cache_unet_model_meta(
            unet_click=["mlunet"],
            measure_option="model_checkpoint",
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
            {"advanced_unet_options": {"display": "block"}},
        ),
        (
            # Test case 2: unet options contraction
            toggle_unet_options,
            # Inputs:
            {"unet_click": []},
            # Expected Outputs:
            {"advanced_unet_options": {"display": "none"}},
        ),
    ],
)
def test_toggle_unet_options_callback(callback_function, args, expected):
    """Test unet options expansion and contraction when a user clicks on unet
    switch"""
    response = callback_function(**args)
    assert type(response) is type(expected)
    assert response["display"] == expected["advanced_unet_options"]["display"]


@pytest.mark.parametrize(
    "callback_function, args, expected",
    [
        (
            # Test case 1: legacy options expansion only when legacy switch is
            # clicked
            toggle_legacy_options,
            # Inputs:
            {
                "legacy_opt": ["legacy: Legacy thresholding with OpenCV"],
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
            },
            # Expected Outputs:
            {
                "cache_legacy_params": {
                    "legacy: Legacy thresholding with OpenCV": {
                        "thresh": "-6",
                        "blur": "0",
                        "binaryops": "5",
                        "diff_method": "1",
                        "clear_border": True,
                        "fill_holes": True,
                        "closing_disk": "5",
                    }
                },
                "legacy_options": {"display": "block"},
            },
        ),
        (
            # Test case 2: legacy options contraction when legacy switch is
            # not clicked
            toggle_legacy_options,
            # Inputs:
            {
                "legacy_opt": [],  # No legacy switch is clicked
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
            },
            # Expected Outputs:
            {
                "cache_legacy_params": None,  # No legacy options are returned
                "legacy_options": {"display": "none"},
            },
        ),
    ],
)
def test_toggle_legacy_options_callback(callback_function, args, expected):
    """Test legacy options expansion and contraction when a user clicks on
    legacy switch"""
    response = callback_function(**args)
    if response[0]:
        for key, value in response[0].items():
            assert key in expected["cache_legacy_params"]
            for k, v in value.items():
                assert k in expected["cache_legacy_params"][key]
                assert v == expected["cache_legacy_params"][key][k]
    assert response[1]["display"] == expected["legacy_options"]["display"]


@pytest.mark.parametrize(
    "callback_function, args, expected",
    [
        (
            # Test case 1: thresh options expansion only when thresh switch is
            # clicked
            toggle_thresh_seg_options,
            # Inputs:
            {
                "thresh_seg_opt": ["thresh: thresholding segmentation"],
                "thresh_seg_keys": [
                    "thresh",
                    "clear_border",
                    "fill_holes",
                    "closing_disk",
                ],
                "thresh_seg_values": ["-6", True, True, "5"],
            },
            # Expected Outputs:
            {
                "cache_thresh_seg_params": {
                    "thresh: thresholding segmentation": {
                        "thresh": "-6",
                        "clear_border": True,
                        "fill_holes": True,
                        "closing_disk": "5",
                    }
                },
                "thresh_seg_options": {"display": "block"},
            },
        ),
        (
            # Test case 2: thresh options contraction when thresh switch is
            # not clicked
            toggle_thresh_seg_options,
            # Inputs:
            {
                "thresh_seg_opt": [],  # No thresh switch is clicked
                "thresh_seg_keys": [
                    "thresh",
                    "clear_border",
                    "fill_holes",
                    "closing_disk",
                ],
                "thresh_seg_values": ["-6", True, True, "5"],
            },
            # Expected Outputs:
            {
                "cache_thresh_seg_params": None,  # No thresh options
                "thresh_seg_options": {"display": "none"},
            },
        ),
    ],
)
def test_toggle_thresh_seg_options(callback_function, args, expected):
    """Test thresh options expansion and contraction when a user clicks on
    thresh switch"""
    response = callback_function(**args)
    if response[0]:
        for key, value in response[0].items():
            assert key in expected["cache_thresh_seg_params"]
            for k, v in value.items():
                assert k in expected["cache_thresh_seg_params"][key]
                assert v == expected["cache_thresh_seg_params"][key][k]
    assert response[1]["display"] == expected["thresh_seg_options"]["display"]


@pytest.mark.parametrize(
    "callback_function, args, expected",
    [
        (
            # Test case 1: watershed options expansion only when watershed
            # switch is clicked
            toggle_watershed_options,
            # Inputs:
            {
                "watershed_opt": ["watershed: Watershed algorithm"],
                "water_keys": ["clear_border", "fill_holes", "closing_disk"],
                "water_values": [True, True, "5"],
            },
            # Expected Outputs:
            {
                "cache_watershed_params": {
                    "watershed: Watershed algorithm": {
                        "clear_border": True,
                        "fill_holes": True,
                        "closing_disk": "5",
                    }
                },
                "watershed_options": {"display": "block"},
            },
        ),
        (
            # Test case 2: watershed options contraction when watershed switch
            # is not clicked
            toggle_watershed_options,
            # Inputs:
            {
                "watershed_opt": [],  # No watershed switch is clicked
                "water_keys": ["clear_border", "fill_holes", "closing_disk"],
                "water_values": [True, True, "5"],
            },
            # Expected Outputs:
            {
                "cache_watershed_params": None,  # No watershed options
                "watershed_options": {"display": "none"},
            },
        ),
    ],
)
def test_toggle_watershed_options_callback(callback_function, args, expected):
    """Test watershed options expansion and contraction when a user clicks on
    watershed switch"""
    response = callback_function(**args)
    if response[0]:
        for key, value in response[0].items():
            assert key in expected["cache_watershed_params"]
            for k, v in value.items():
                assert k in expected["cache_watershed_params"][key]
                assert v == expected["cache_watershed_params"][key][k]
    assert response[1]["display"] == expected["watershed_options"]["display"]


@pytest.mark.parametrize(
    "callback_function, args, expected",
    [
        (
            # Test case 1: std options expansion only when std
            # switch is clicked
            toggle_std_options,
            # Inputs:
            {
                "std_opt": ["std: Standard-deviation-based thresholding"],
                "std_keys": ["clear_border", "fill_holes", "closing_disk"],
                "std_values": [True, True, "5"],
            },
            # Expected Outputs:
            {
                "cache_std_params": {
                    "std: Standard-deviation-based thresholding": {
                        "clear_border": True,
                        "fill_holes": True,
                        "closing_disk": "5",
                    }
                },
                "std_options": {"display": "block"},
            },
        ),
        (
            # Test case 2: std options contraction when std switch
            # is not clicked
            toggle_std_options,
            # Inputs:
            {
                "std_opt": [],  # No std switch is clicked
                "std_keys": ["clear_border", "fill_holes", "closing_disk"],
                "std_values": [True, True, "5"],
            },
            # Expected Outputs:
            {
                "cache_std_params": None,  # No std options are returned,
                "std_options": {"display": "none"},
            },
        ),
    ],
)
def test_toggle_std_options_callback(callback_function, args, expected):
    """Test std options expansion and contraction when a user clicks on
    std switch"""
    response = callback_function(**args)
    if response[0]:
        for key, value in response[0].items():
            assert key in expected["cache_std_params"]
            for k, v in value.items():
                assert k in expected["cache_std_params"][key]
                assert v == expected["cache_std_params"][key][k]
    assert response[1]["display"] == expected["std_options"]["display"]


@pytest.mark.parametrize(
    "callback_function, args, expected",
    [
        (
            # Test case 1: rollmed options expansion only when rollmed
            # switch is clicked
            toggle_rollmed_options,
            # Inputs:
            {
                "rollmed_opt": [
                    "rollmed: Rolling median RT-DC background image "
                    "computation"
                ],
                "rollmed_keys": ["clear_border", "fill_holes", "closing_disk"],
                "rollmed_values": [True, True, "5"],
            },
            # Expected Outputs:
            {
                "cache_rollmed_params": {
                    "rollmed: Rolling median RT-DC background image "
                    "computation": {
                        "clear_border": True,
                        "fill_holes": True,
                        "closing_disk": "5",
                    }
                },
                "rollmed_options": {"display": "block"},
            },
        ),
        (
            # Test case 2: rollmed options contraction when rollmed switch
            # is not clicked
            toggle_rollmed_options,
            # Inputs:
            {
                "rollmed_opt": [],  # No rollmed switch is clicked
                "rollmed_keys": ["clear_border", "fill_holes", "closing_disk"],
                "rollmed_values": [True, True, "5"],
            },
            # Expected Outputs:
            {
                "cache_rollmed_params": None,  # No rollmed options
                "rollmed_options": {"display": "none"},
            },
        ),
    ],
)
def test_toggle_rollmed_options_callback(callback_function, args, expected):
    """Test rollmed options expansion and contraction when a user clicks on
    rollmed switch"""
    response = callback_function(**args)
    if response[0]:
        for key, value in response[0].items():
            assert key in expected["cache_rollmed_params"]
            for k, v in value.items():
                assert k in expected["cache_rollmed_params"][key]
                assert v == expected["cache_rollmed_params"][key][k]
    assert response[1]["display"] == expected["rollmed_options"]["display"]


@pytest.mark.parametrize(
    "callback_function, args, expected",
    [
        (
            # Test case 1: sparsemed options expansion only when sparsemed
            # switch is clicked
            toggle_sparsemed_options,
            # Inputs:
            {
                "sparsemed_opt": [
                    "sparsemed: Sparse median background correction "
                    "with cleansing"
                ],
                "sparsemed_keys": [
                    "kernel_size",
                    "split_time",
                    "thresh_cleansing",
                    "frac_cleansing",
                    "offset_correction",
                ],
                "sparsemed_values": [200, 1, 0, 0.8, True],
            },
            # Expected Outputs:
            {
                "cache_sparsemed_params": {
                    "sparsemed: Sparse median background correction "
                    "with cleansing": {
                        "kernel_size": 200,
                        "split_time": 1,
                        "thresh_cleansing": 0,
                        "frac_cleansing": 0.8,
                        "offset_correction": True,
                    }
                },
                "sparsemed_options": {"display": "block"},
            },
        ),
        (
            # Test case 2: sparsemed options contraction when sparsemed switch
            # is not clicked
            toggle_sparsemed_options,
            # Inputs:
            {
                "sparsemed_opt": [],  # No sparsemed switch is clicked
                "sparsemed_keys": [
                    "kernel_size",
                    "split_time",
                    "thresh_cleansing",
                    "frac_cleansing",
                    "offset_correction",
                ],
                "sparsemed_values": [200, 1, 0, 0.8, True],
            },
            # Expected Outputs:
            {
                "cache_sparsemed_params": None,  # No sparsemed options
                "sparsemed_options": {"display": "none"},
            },
        ),
    ],
)
def test_toggle_sparsemed_options_callback(callback_function, args, expected):
    """Test sparsemed options expansion and contraction when a user clicks on
    sparsemed switch"""
    response = callback_function(**args)
    if response[0]:
        for key, value in response[0].items():
            assert key in expected["cache_sparsemed_params"]
            for k, v in value.items():
                assert k in expected["cache_sparsemed_params"][key]
                assert v == expected["cache_sparsemed_params"][key][k]
    assert response[1]["display"] == expected["sparsemed_options"]["display"]


@pytest.mark.parametrize(
    "callback_function, args, expected",
    [
        (
            # Test case 1: norm gate options expansion only when norm gate
            # switch is clicked
            toggle_norm_gate_options,
            # Inputs:
            {
                "ngate_opt": ["norm gating"],
                "ngate_keys": ["online_gates", "size_thresh_mask"],
                "ngate_values": [False, 0],
            },
            # Expected Outputs:
            {
                "cache_norm_gate_params": {
                    "norm gating": {
                        "online_gates": False,
                        "size_thresh_mask": 0,
                    }
                },
                "norm_gate_options": {"display": "block"},
            },
        ),
        (
            # Test case 2: norm gate options contraction when norm gate switch
            # is not clicked
            toggle_norm_gate_options,
            # Inputs:
            {
                "ngate_opt": [],  # No norm gate switch is clicked
                "ngate_keys": ["online_gates", "size_thresh_mask"],
                "ngate_values": [False, 0],
            },
            # Expected Outputs:
            {
                "cache_norm_gate_params": None,  # No norm gate options
                "norm_gate_options": {"display": "none"},
            },
        ),
    ],
)
def test_toggle_norm_gate_options_callback(callback_function, args, expected):
    """Test norm gate options expansion and contraction when a user clicks on
    norm gate switch"""
    response = callback_function(**args)
    if response[0]:
        for key, value in response[0].items():
            assert key in expected["cache_norm_gate_params"]
            for k, v in value.items():
                assert k in expected["cache_norm_gate_params"][key]
                assert v == expected["cache_norm_gate_params"][key][k]
    assert response[1]["display"] == expected["norm_gate_options"]["display"]


@pytest.mark.parametrize(
    "callback_function, triggered_inputs, args, expected",
    [
        (
            # Test case 1: When user clicks on 'create pipeline' button, a
            # popup message box will be opened.
            advanced_request_submission_popup,
            # Stimulate Inputs
            [{"prop_id": "create_advanced_pipeline_button.n_clicks"}],
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
            {"advanced_popup": True},
        ),
        (
            # Test case 2: After the popup message is opened up, user clicks
            # on the 'close' button inside the popup message box.
            advanced_request_submission_popup,
            # Stimulate Inputs
            [{"prop_id": "advanced_popup_close.n_clicks"}],
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
            {"advanced_popup": False},
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
            {"advanced_popup": False},
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
    assert response == expected["advanced_popup"]


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
                "selected_files": [{"filepath": "test1.rtdc"}],
                "cached_unet_model_path": {
                    "mlunet: UNET": {"model_file": "test_checkpoint"}
                },
                "cached_legacy_params": {},
                "cache_watershed_params": {},
                "cache_std_params": {},
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
                "selected_files": [{"filepath": "test1.rtdc"}],
                "cached_unet_model_path": {
                    "mlunet: UNET": {"model_file": "test_checkpoint"}
                },
                "cached_legacy_params": {},
                "cache_watershed_params": {},
                "cache_std_params": {},
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
                "advanced_title": "test_title",
                "reproduce_flag": [],
                "classifier_name": [],
                "cache_unet_model_path": {
                    "mlunet: UNET": {"model_file": "test_checkpoint"}
                },
                "cache_legacy_params": {},
                "cache_thresh_seg_params": {},
                "cache_watershed_params": {},
                "cache_std_params": {},
                "cache_rollmed_params": {},
                "cache_sparsemed_params": {
                    "sparsemed: Sparse median background correction with "
                    "cleansing": {
                        "kernel_size": 200,
                        "split_time": 1,
                        "thresh_cleansing": 0,
                        "frac_cleansing": 0.8,
                    }
                },
                "cache_norm_gate_params": {
                    "norm gating": {
                        "online_gates": False,
                        "size_thresh_mask": 0,
                    }
                },
                "cache_num_frames": {},
                "selected_rows": [{"filepath": "HSMFS: test.rtdc"}],
            },
            # Expected Outputs:
            {
                "cache_advanced_template": {
                    "title": "test_title",
                    "description": """
                    **Segmentation**
                        - [x] mlunet: UNET
                          - [x] model_file=test_checkpoint
                        - [x] sparsemed:
                          - [x] kernel_size=200
                          - [x] split_time=1
                          - [x] thresh_cleansing=0
                          - [x] frac_cleansing=0.8
                        - [x] norm gating
                          - [x] online_gates=False
                          - [x] size_thresh_mask=0
                    **Data to Process**
                    - [x] HSMFS: test.rtdc
                    __Author_name__
                    [x] username=test_username
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
                "advanced_title": "",  # No title is provided ()
                "reproduce_flag": [],
                "classifier_name": [],
                "cache_unet_model_path": {},
                "cache_legacy_params": {},
                "cache_thresh_seg_params": {},
                "cache_watershed_params": {},
                "cache_std_params": {},
                "cache_rollmed_params": {},
                "cache_sparsemed_params": {
                    "sparsemed: Sparse median background correction with "
                    "cleansing": {
                        "kernel_size": 200,
                        "split_time": 1,
                        "thresh_cleansing": 0,
                        "frac_cleansing": 0.8,
                    }
                },
                "cache_norm_gate_params": {
                    "norm gating": {
                        "online_gates": False,
                        "size_thresh_mask": 0,
                    }
                },
                "cache_num_frames": {"--num-frames": {"--num-frames": 200}},
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
                "advanced_title": "test_title",
                "reproduce_flag": ["--reproduce"],
                "classifier_name": [],
                "cache_unet_model_path": {
                    "mlunet: UNET": {"model_file": "test_checkpoint"}
                },
                "cache_legacy_params": {},
                "cache_thresh_seg_params": {},
                "cache_watershed_params": {},
                "cache_std_params": {},
                "cache_rollmed_params": {},
                "cache_sparsemed_params": {
                    "sparsemed: Sparse median background correction with "
                    "cleansing": {
                        "kernel_size": 200,
                        "split_time": 1,
                        "thresh_cleansing": 0,
                        "frac_cleansing": 0.8,
                    }
                },
                "cache_norm_gate_params": {
                    "norm gating": {
                        "online_gates": False,
                        "size_thresh_mask": 0,
                    }
                },
                "cache_num_frames": {"--num-frames": {"--num-frames": 200}},
                "selected_rows": [{"filepath": "HSMFS: test.rtdc"}],
            },
            # Expected Outputs:
            {
                "cache_advanced_template": {
                    "title": "test_title",
                    "description": """
                    **Segmentation**
                        - [x] mlunet: UNET
                          - [x] model_file=test_checkpoint
                        - [x] sparsemed:
                          - [x] kernel_size=200
                          - [x] split_time=1
                          - [x] thresh_cleansing=0
                          - [x] frac_cleansing=0.8
                        - [x] norm gating
                          - [x] online_gates=False
                          - [x] size_thresh_mask=0
                        - [x] --reproduce
                        - [x] --num-frames
                          - [x] --num-frames=200
                    **Data to Process**
                    - [x] HSMFS: test.rtdc
                    __Author_name__
                    [x] username=test_username
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
        red_desc = response["description"]
        exp_desc = expected["cache_advanced_template"]["description"]

        for line in exp_desc:
            assert line in red_desc
