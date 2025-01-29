from contextvars import copy_context

from dash import no_update
from dash._callback_context import context_value
from dash._utils import AttributeDict
import pytest

from dashboard.pages.page_home import change_page, manage_pipeline_status, \
    show_pipeline_data, show_pipeline_number


@pytest.mark.parametrize(
    "active_tab, opened_curr_page, closed_curr_page, search_term, cache_page, "
    "expected_cache_page, expected_opened_pages, expected_closed_pages",
    [
        # Test case 1: enable and return opened tab pages
        (
                "opened", 1, 1, "", {"opened": 0, "closed": 0},
                {"opened": 1, "closed": 0}, 1, 1
        ),
        # Test case 2: enable and return closed tab pages
        (
                "closed", 1, 1, "", {"opened": 0, "closed": 0},
                {"opened": 0, "closed": 1}, 1, 1
        ),
        # Test case 3: enable and return filtered pages
        (
                "opened", 1, 1, "username102", {"opened": 0, "closed": 0},
                {"opened": 1, "closed": 0}, 1, 1
        )
    ]
)
def test_change_page_callback(active_tab, opened_curr_page, closed_curr_page,
                              search_term, cache_page,
                              expected_cache_page, expected_opened_pages,
                              expected_closed_pages):
    """Test functionality of previous buttons in opened and closed tabs"""

    def run_callback():
        return change_page(active_tab=active_tab,
                           opened_curr_page=opened_curr_page,
                           closed_curr_page=closed_curr_page,
                           search_term=search_term, cache_page=cache_page)

    ctx = copy_context()
    response = ctx.run(run_callback)
    cache_page, open_pages, close_pages = response

    assert cache_page == expected_cache_page
    assert open_pages == expected_opened_pages
    assert close_pages == expected_closed_pages


@pytest.mark.parametrize(
    "triggered_inputs, active_tab, pipeline_num, run_pause_click, "
    "stop_pipe_click, pipeline_comments, keep_results_flag, "
    "keep_raw_data_flag, expected_popup_is_open, expected_popup_msg, "
    "expected_run_pause_disabled, expected_run_pause_child, "
    "expected_stop_disabled, expected_keep_raw_data_disabled",
    [
        # Test case 1: skip all actions because the selected issue is None
        (
                [],
                "closed", None, 0, 0, None, 0, 0,
                no_update, no_update, no_update, no_update, no_update,
                no_update
        ),
        # Test case 2: disable "toggle raw data flag" because test issue does
        # not have the HSM paths
        (
                [],
                "closed", 2, 0, 0, {"dummy chat dict": ["stop", "go"]}, 0, 0,
                no_update, no_update, no_update, no_update, no_update, True
        ),
        # Test case 3: toggle s3 results flag
        (
                [{"prop_id": "keep_results_flag.n_clicks"}],
                "closed", 2, 0, 0, {"dummy chat dict": ["stop", "go"]}, 1, 0,
                True, "The S3 results flag has been changed!", no_update,
                no_update, no_update, True
        ),
        # Test case 4: resume pipeline
        (
                [{"prop_id": "run_pause_click.n_clicks"}],
                "opened", 3, 1, 0, {"dummy chat dict": ["go"]}, 0, 0,
                True, "The pipeline has been resumed!", no_update,
                "Run Pipeline", no_update, True
        ),
        # Test case 5: pause pipeline
        (
                [{"prop_id": "run_pause_click.n_clicks"}],
                "opened", 4, 1, 0, {"dummy chat dict": ["stop", "go"]}, 0, 0,
                True, "The pipeline has been paused!", no_update, no_update,
                no_update, True
        ),
        # Test case 6: cancel pipeline
        (
                [{"prop_id": "stop_pipe_click.n_clicks"}],
                "opened", 4, 1, 0, {"dummy chat dict": ["stop", "go"]}, 0, 0,
                True, "The pipeline has been canceled!", True, no_update,
                True, True
        ),
        # Test case 7: disable run/pause button when there is an error
        (
                [],
                "opened", 5, 0, 0, {"dummy chat dict": ["stop", "go"]}, 0, 0,
                no_update, no_update, True, no_update, False, True
        ),
        # Test case 8: toggle s3 raw data flag
        (
                [{"prop_id": "keep_raw_data_flag.n_clicks"}],
                "closed", 2, 0, 0, {"dummy chat dict": ["stop", "go"]}, 0, 1,
                True, "The S3 raw data flag has been changed!", no_update,
                no_update, no_update, True
        )
    ]
)
def test_manage_pipeline_status_callback(triggered_inputs, active_tab,
                                         pipeline_num, run_pause_click,
                                         stop_pipe_click, pipeline_comments,
                                         keep_results_flag,
                                         keep_raw_data_flag,
                                         expected_popup_is_open,
                                         expected_popup_msg,
                                         expected_run_pause_disabled,
                                         expected_run_pause_child,
                                         expected_stop_disabled,
                                         expected_keep_raw_data_disabled):
    """Test manage_pipeline_status with various scenarios"""

    def run_callback():
        context_value.set(
            AttributeDict(**{
                "triggered_inputs": triggered_inputs
            })
        )
        return manage_pipeline_status(
            active_tab=active_tab,
            pipeline_num=pipeline_num,
            run_pause_click=run_pause_click,
            stop_pipe_click=stop_pipe_click,
            pipeline_comments=pipeline_comments,
            keep_results_flag=keep_results_flag,
            keep_raw_data_flag=keep_raw_data_flag
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert response[0] == expected_popup_is_open
    assert response[1] == expected_popup_msg
    assert response[2] == expected_run_pause_disabled
    assert response[3] == expected_run_pause_child
    assert response[5] == expected_stop_disabled
    assert response[6] == expected_keep_raw_data_disabled


@pytest.mark.parametrize(
    "pipeline_num, expected_result_path_msg, expected_jobs, "
    "expected_progress, expected_progress_str",
    [
        # Test case 1: skip all actions
        (
                None,
                no_update, no_update, no_update, no_update
        ),
        # Test case 2: if total_job == 0
        (
                1,
                "Result path is not found!", "Jobs: [0 / 0]", None, None
        ),
        # Test case 3: with two jobs that are completed
        (
                2,
                "Result path is not found!", "Jobs: [2 / 2]", 95, "95 %"

        )
    ]
)
def test_show_pipeline_data_callback(pipeline_num, expected_result_path_msg,
                                     expected_jobs, expected_progress,
                                     expected_progress_str):
    """Test show_pipeline_data with various scenarios"""

    def run_callback():
        return show_pipeline_data(pipeline_num=pipeline_num)

    ctx = copy_context()
    response = ctx.run(run_callback)

    assert response[1] == expected_result_path_msg
    assert response[2] == expected_jobs
    assert response[3] == expected_progress
    assert response[4] == expected_progress_str


@pytest.mark.parametrize(
    "pathname, expected_open_num, expected_close_num",
    [
        # Test case 1: skip all actions
        (
                "/wrong_pathname/",
                no_update, no_update
        ),
        # Test case 2: show only pathname is given
        (
                "/local-dashboard/",
                5, 1
        )
    ]
)
def test_show_pipeline_number_callback(pathname, expected_open_num,
                                       expected_close_num):
    """Test show_pipeline_number with various scenarios"""

    def run_callback():
        return show_pipeline_number(pathname=pathname)

    ctx = copy_context()
    response = ctx.run(run_callback)

    assert response[0] == expected_open_num
    assert response[1] == expected_close_num
