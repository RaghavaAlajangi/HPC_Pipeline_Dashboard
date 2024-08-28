from contextvars import copy_context

from dash import no_update
from dash._callback_context import context_value
from dash._utils import AttributeDict
import pytest

from dashboard.pages.page_home import change_page, manage_pipeline_status


@pytest.mark.parametrize(
    "triggered_inputs, active_tab, pipeline_num, run_pause_click, "
    "stop_pipe_click, pipeline_comments, expected_responses",
    [
        # Test case 1: manage_pipeline_status deactivation
        (
                [
                    {"prop_id": "run_pause_click.n_clicks"},
                    {"prop_id": "stop_pipe_click.n_clicks"}
                ],
                "closed", 100, 0, 0, {"dummy chat dict": ["stop", "go"]},
                (no_update, no_update, no_update, no_update)
        ),
        # Test case 2: manage_pipeline_status activation
        (
                [],
                "opened", 101, 0, 0, {"dummy chat dict": ["stop", "go"]},
                (False, None, False, False)
        ),
        # Test case 3: resume pipeline
        (
                [
                    {"prop_id": "run_pause_click.n_clicks"},
                    {"prop_id": "stop_pipe_click.n_clicks"}
                ],
                "opened", 102, 1, 0, {"dummy chat dict": ["stop", "go"]},
                (True, "The issue has been resumed.", False, False)
        ),
        # Test case 4: pause pipeline
        (
                [
                    {"prop_id": "run_pause_click.n_clicks"},
                    {"prop_id": "stop_pipe_click.n_clicks"}
                ],
                "opened", 103, 1, 0, {"dummy chat dict": ["stop", "go"]},
                (True, "The issue has been paused.", False, False)
        ),
        # Test case 5: stop pipeline
        (
                [{"prop_id": "stop_pipe_click.n_clicks"}],
                "opened", 103, 0, 1, {"dummy chat dict": ["stop", "go"]},
                (True, "The issue has been stopped.", True, True)
        ),
        # Test case 5: disable run/resume button when there is an error
        (
                [],
                "opened", 104, 0, 0, {"dummy chat dict": ["stop", "go"]},
                (False, None, True, False)
        )
    ]
)
def test_manage_pipeline_status_callback(triggered_inputs, active_tab,
                                         pipeline_num, run_pause_click,
                                         stop_pipe_click, pipeline_comments,
                                         expected_responses):
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
            pipeline_comments=pipeline_comments
        )

    ctx = copy_context()
    response = ctx.run(run_callback)

    assert response == expected_responses


@pytest.mark.parametrize(
    "active_tab, active_page, search_term, cache_page, "
    "expected_cache_page, expected_num_pages",
    [
        # Test case 1: enable and return opened tab pages
        (
                "opened", 1, "", {"opened": 0, "closed": 0},
                {"opened": 1, "closed": 0}, 1
        ),
        # Test case 2: enable and return closed tab pages
        (
                "closed", 1, "", {"opened": 0, "closed": 0},
                {"opened": 0, "closed": 1}, 11
        ),
        # Test case 3: enable and return filtered pages
        (
                "opened", 1, "username102", {"opened": 0, "closed": 0},
                {"opened": 1, "closed": 0}, 1
        )
    ]
)
def test_change_page_callback(active_tab, active_page, search_term, cache_page,
                              expected_cache_page, expected_num_pages):
    """Test functionality of previous buttons in opened and closed tabs"""

    def run_callback():
        return change_page(active_tab=active_tab, active_page=active_page,
                           search_term=search_term, cache_page=cache_page)

    ctx = copy_context()
    response = ctx.run(run_callback)
    cache_page, num_pages = response

    assert cache_page == expected_cache_page
    assert num_pages == expected_num_pages
