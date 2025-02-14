from contextvars import copy_context

import dash_mantine_components as dmc
import pytest
from dash import no_update
from dash._callback_context import context_value
from dash._utils import AttributeDict

from dashboard.pages.page_home import (
    change_page,
    manage_pipeline_status,
    show_pipeline_data,
    show_pipeline_number,
    switch_tabs,
)


@pytest.mark.parametrize(
    "callback_function, args, expected",
    [
        (
            # Test case 1: enable and return opened tab pages
            switch_tabs,
            # Inputs:
            {
                "active_tab": "opened",
                "cache_page": {"opened": 1},
                "search_term": None,
            },
            # Expected Outputs:
            {
                "opened_content": dmc.Accordion(),
                "closed_content": no_update,
                "opened_loading": {"position": "center"},
                "closed_loading": no_update,
            },
        ),
        (
            # Test case 2: enable and return opened tab pages
            switch_tabs,
            # Inputs:
            {
                "active_tab": "closed",
                "cache_page": {"closed": 1},
                "search_term": None,
            },
            # Expected Outputs:
            {
                "opened_content": no_update,
                "closed_content": dmc.Accordion(),
                "opened_loading": no_update,
                "closed_loading": {"position": "center"},
            },
        ),
    ],
)
def test_switch_tabs_callback(callback_function, args, expected):
    """Test switch_tabs with various scenarios"""
    response = callback_function(**args)
    assert type(response[0]) is type(expected["opened_content"])
    assert type(response[1]) is type(expected["closed_content"])
    assert response[2] == expected["opened_loading"]
    assert response[3] == expected["closed_loading"]


@pytest.mark.parametrize(
    "callback_function, args, expected",
    [
        (
            # Test case 1: enable and return opened tab pages
            change_page,
            # Inputs:
            {
                "active_tab": "opened",
                "opened_curr_page": 1,
                "closed_curr_page": 1,
                "search_term": "",
                "cache_page": {"opened": 0, "closed": 0},
            },
            # Expected Outputs:
            {
                "cache_page_num": {"opened": 1, "closed": 0},
                "opened_pagination": 1,
                "closed_pagination": 1,
            },
        ),
        (
            # Test case 2: enable and return closed tab pages
            change_page,
            # Inputs:
            {
                "active_tab": "closed",
                "opened_curr_page": 1,
                "closed_curr_page": 1,
                "search_term": "",
                "cache_page": {"opened": 0, "closed": 0},
            },
            # Expected Outputs:
            {
                "cache_page_num": {"opened": 0, "closed": 1},
                "opened_pagination": 1,
                "closed_pagination": 1,
            },
        ),
        (
            # Test case 3: select wrong tab
            change_page,
            # Inputs:
            {
                "active_tab": "wrong",  # wrong doesnt exist
                "opened_curr_page": 1,
                "closed_curr_page": 1,
                "search_term": "username102",
                "cache_page": {"opened": 1, "closed": 0},
            },
            # Expected Outputs:
            {
                "cache_page_num": {"opened": 1, "closed": 0},
                "opened_pagination": 1,
                "closed_pagination": 1,
            },
        ),
        (
            # Test case 4: enable and return filtered pages
            change_page,
            # Inputs:
            {
                "active_tab": "opened",
                "opened_curr_page": 1,
                "closed_curr_page": 1,
                "search_term": "username102",
                "cache_page": {"opened": 1, "closed": 0},
            },
            # Expected Outputs:
            {
                "cache_page_num": {"opened": 1, "closed": 0},
                "opened_pagination": 1,
                "closed_pagination": 1,
            },
        ),
    ],
)
def test_change_page_callback(callback_function, args, expected):
    """Test change_page with various scenarios"""
    response = callback_function(**args)
    if response is not no_update:
        assert response[0] == expected["cache_page_num"]
        assert response[1] == expected["opened_pagination"]
        assert response[2] == expected["closed_pagination"]


@pytest.mark.parametrize(
    "callback_function, triggered_inputs, args, expected",
    [
        (
            # Test case 1: skip all actions because the selected issue is None
            manage_pipeline_status,
            # Stimulate Inputs:
            [],
            # Inputs:
            {
                "active_tab": "closed",
                "pipeline_num": None,
                "run_pause_click": 0,
                "stop_pipe_click": 0,
                "pipeline_comments": 0,
                "keep_results_flag": None,
                "keep_raw_data_flag": 0,
            },
            # Expected Outputs:
            {
                "popup_is_open": no_update,
                "popup_msg": no_update,
                "run_pause_disabled": no_update,
                "run_pause_child": no_update,
                "stop_disabled": no_update,
                "keep_raw_data_disabled": no_update,
            },
        ),
        (
            # Test case 2: disable "toggle raw data flag"
            manage_pipeline_status,
            # Stimulate Inputs:
            [],
            # Inputs:
            {
                "active_tab": "closed",
                "pipeline_num": 2,
                "run_pause_click": 0,
                "stop_pipe_click": 0,
                "pipeline_comments": {"dummy chat dict": ["stop", "go"]},
                "keep_results_flag": 0,
                "keep_raw_data_flag": 0,
            },
            # Expected Outputs:
            {
                "popup_is_open": no_update,
                "popup_msg": no_update,
                "run_pause_disabled": no_update,
                "run_pause_child": no_update,
                "stop_disabled": no_update,
                "keep_raw_data_disabled": True,
            },
        ),
        (
            # Test case 3: toggle s3 results flag
            manage_pipeline_status,
            # Stimulate Inputs:
            [{"prop_id": "keep_results_flag.n_clicks"}],
            # Inputs:
            {
                "active_tab": "closed",
                "pipeline_num": 2,
                "run_pause_click": 0,
                "stop_pipe_click": 0,
                "pipeline_comments": {"dummy chat dict": ["stop", "go"]},
                "keep_results_flag": 1,
                "keep_raw_data_flag": 0,
            },
            # Expected Outputs:
            {
                "popup_is_open": True,
                "popup_msg": "The S3 results flag has been changed!",
                "run_pause_disabled": no_update,
                "run_pause_child": no_update,
                "stop_disabled": no_update,
                "keep_raw_data_disabled": True,
            },
        ),
        (
            # Test case 4: resume pipeline
            manage_pipeline_status,
            # Stimulate Inputs:
            [{"prop_id": "run_pause_click.n_clicks"}],
            # Inputs:
            {
                "active_tab": "opened",
                "pipeline_num": 3,
                "run_pause_click": 1,
                "stop_pipe_click": 0,
                "pipeline_comments": {"dummy chat dict": ["stop", "go"]},
                "keep_results_flag": 0,
                "keep_raw_data_flag": 0,
            },
            # Expected Outputs:
            {
                "popup_is_open": True,
                "popup_msg": "The pipeline has been resumed!",
                "run_pause_disabled": no_update,
                "run_pause_child": "Run Pipeline",
                "stop_disabled": no_update,
                "keep_raw_data_disabled": True,
            },
        ),
        (
            # Test case 5: pause pipeline
            manage_pipeline_status,
            # Stimulate Inputs:
            [{"prop_id": "run_pause_click.n_clicks"}],
            # Inputs:
            {
                "active_tab": "opened",
                "pipeline_num": 4,
                "run_pause_click": 1,
                "stop_pipe_click": 0,
                "pipeline_comments": {"dummy chat dict": ["stop", "go"]},
                "keep_results_flag": 0,
                "keep_raw_data_flag": 0,
            },
            # Expected Outputs:
            {
                "popup_is_open": True,
                "popup_msg": "The pipeline has been paused!",
                "run_pause_disabled": no_update,
                "run_pause_child": no_update,
                "stop_disabled": no_update,
                "keep_raw_data_disabled": True,
            },
        ),
        (
            # Test case 6: cancel pipeline
            manage_pipeline_status,
            # Stimulate Inputs:
            [{"prop_id": "stop_pipe_click.n_clicks"}],
            # Inputs:
            {
                "active_tab": "opened",
                "pipeline_num": 4,
                "run_pause_click": 1,
                "stop_pipe_click": 0,
                "pipeline_comments": {"dummy chat dict": ["stop", "go"]},
                "keep_results_flag": 0,
                "keep_raw_data_flag": 0,
            },
            # Expected Outputs:
            {
                "popup_is_open": True,
                "popup_msg": "The pipeline has been canceled!",
                "run_pause_disabled": True,
                "run_pause_child": no_update,
                "stop_disabled": True,
                "keep_raw_data_disabled": True,
            },
        ),
        (
            # Test case 7: disable run/pause button when there is an error
            manage_pipeline_status,
            # Stimulate Inputs:
            [],
            # Inputs:
            {
                "active_tab": "opened",
                "pipeline_num": 5,
                "run_pause_click": 0,
                "stop_pipe_click": 0,
                "pipeline_comments": {"dummy chat dict": ["stop", "go"]},
                "keep_results_flag": 0,
                "keep_raw_data_flag": 0,
            },
            # Expected Outputs:
            {
                "popup_is_open": no_update,
                "popup_msg": no_update,
                "run_pause_disabled": True,
                "run_pause_child": no_update,
                "stop_disabled": False,
                "keep_raw_data_disabled": True,
            },
        ),
        (
            # Test case 8: toggle s3 raw data flag
            manage_pipeline_status,
            # Stimulate Inputs:
            [{"prop_id": "keep_raw_data_flag.n_clicks"}],
            # Inputs:
            {
                "active_tab": "closed",
                "pipeline_num": 2,
                "run_pause_click": 0,
                "stop_pipe_click": 0,
                "pipeline_comments": {"dummy chat dict": ["stop", "go"]},
                "keep_results_flag": 0,
                "keep_raw_data_flag": 1,
            },
            # Expected Outputs:
            {
                "popup_is_open": True,
                "popup_msg": "The S3 raw data flag has been changed!",
                "run_pause_disabled": no_update,
                "run_pause_child": no_update,
                "stop_disabled": no_update,
                "keep_raw_data_disabled": True,
            },
        ),
    ],
)
def test_manage_pipeline_status_callback(
    callback_function, triggered_inputs, args, expected
):
    """Test manage_pipeline_status with various scenarios"""

    def run_callback():
        context_value.set(
            AttributeDict(**{"triggered_inputs": triggered_inputs})
        )
        return callback_function(**args)

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert response[0] == expected["popup_is_open"]
    assert response[1] == expected["popup_msg"]
    assert response[2] == expected["run_pause_disabled"]
    assert response[3] == expected["run_pause_child"]
    assert response[5] == expected["stop_disabled"]
    assert response[6] == expected["keep_raw_data_disabled"]


@pytest.mark.parametrize(
    "callback_function, args, expected",
    [
        (
            # Test case 1: skip all actions
            show_pipeline_data,
            # Inputs:
            {"pipeline_num": None},
            # Expected Outputs:
            {
                "pipeline_comments": no_update,
                "s3_proxy_path": no_update,
                "pipeline_progress_num": no_update,
                "pipeline_progress_bar_val": no_update,
                "pipeline_progress_bar_lbl": no_update,
                "cache_pipeline_notes": no_update,
            },
        ),
        (
            # Test case 2: show only pathname is given
            show_pipeline_data,
            # Inputs:
            {"pipeline_num": 1},
            # Expected Outputs:
            {
                "s3_proxy_path": "Result path is not found!",
                "pipeline_progress_num": "Jobs: [0 / 0]",
                "pipeline_progress_bar_val": None,
                "pipeline_progress_bar_lbl": None,
            },
        ),
        (
            # Test case 3: with two jobs that are completed
            show_pipeline_data,
            {"pipeline_num": 2},
            # Expected Outputs:
            {
                "s3_proxy_path": "Result path is not found!",
                "pipeline_progress_num": "Jobs: [2 / 2]",
                "pipeline_progress_bar_val": 95,
                "pipeline_progress_bar_lbl": "95 %",
            },
        ),
    ],
)
def test_show_pipeline_data_callback(callback_function, args, expected):
    """Test show_pipeline_number with various scenarios"""
    response = callback_function(**args)
    assert response[1] == expected["s3_proxy_path"]
    assert response[2] == expected["pipeline_progress_num"]
    assert response[3] == expected["pipeline_progress_bar_val"]
    assert response[4] == expected["pipeline_progress_bar_lbl"]


@pytest.mark.parametrize(
    "callback_function, args, expected",
    [
        (
            # Test case 1: skip all actions
            show_pipeline_number,
            # Inputs:
            {"pathname": "/wrong_pathname/"},
            # Expected Outputs:
            {"open_tab_badge": no_update, "close_tab_badge": no_update},
        ),
        (
            # Test case 2: show only pathname is given
            show_pipeline_number,
            # Inputs:
            {"pathname": "/local-dashboard/"},
            # Expected Outputs:
            {
                # 5 opened test issues are defined in conftest.py
                "open_tab_badge": 5,
                # 1 closed test issues are defined in conftest.py
                "close_tab_badge": 1,
            },
        ),
    ],
)
def test_show_pipeline_number_callback(callback_function, args, expected):
    """Test show_pipeline_number with various scenarios"""
    response = callback_function(**args)
    assert response[0] == expected["open_tab_badge"]
    assert response[1] == expected["close_tab_badge"]
