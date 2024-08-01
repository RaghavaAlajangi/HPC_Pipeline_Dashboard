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
    "triggered_inputs, opclick, onclick, cpclick, cnclick, active_tab, "
    "cache_page, expected_cache_page, expected_opened_prev_disabled, "
    "expected_closed_prev_disabled",
    [
        # Test case 1: enable functionality of previous button in opened tab
        (
                [{"prop_id": "opened_next_button.n_clicks"}],
                0, 1, 0, 0, "opened",
                {"opened": 2, "closed": 1},
                {"opened": 3, "closed": 1},
                False, True
        ),
        # Test case 2: disable functionality of previous button in opened tab
        (
                [{"prop_id": "opened_next_button.n_clicks"}],
                0, 1, 0, 0, "opened",
                {"opened": 0, "closed": 1},
                {"opened": 1, "closed": 1},
                True, True
        ),
        # Test case 3: enable functionality of previous button in closed tab
        (
                [{"prop_id": "closed_next_button.n_clicks"}],
                0, 0, 0, 1, "closed",
                {"opened": 1, "closed": 2},
                {"opened": 1, "closed": 3},
                True, False
        ),
        # Test case 4: disable functionality of previous button in closed tab
        (
                [{"prop_id": "closed_next_button.n_clicks"}],
                0, 0, 0, 1, "closed",
                {"opened": 1, "closed": 0},
                {"opened": 1, "closed": 1},
                True, True
        ),
    ]
)
def test_change_page_callback(triggered_inputs, opclick, onclick, cpclick,
                              cnclick, active_tab, cache_page,
                              expected_cache_page,
                              expected_opened_prev_disabled,
                              expected_closed_prev_disabled):
    """Test functionality of previous buttons in opened and closed tabs"""

    def run_callback():
        context_value.set(
            AttributeDict(**{
                "triggered_inputs": triggered_inputs
            })
        )
        return change_page(opclick=opclick, onclick=onclick, cpclick=cpclick,
                           cnclick=cnclick, active_tab=active_tab,
                           cache_page=cache_page)

    ctx = copy_context()
    response = ctx.run(run_callback)
    cache_page, opened_prev_disabled, closed_prev_disabled = response

    assert cache_page == expected_cache_page
    assert opened_prev_disabled == expected_opened_prev_disabled
    assert closed_prev_disabled == expected_closed_prev_disabled
