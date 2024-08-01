from contextvars import copy_context

from dash import no_update
from dash._callback_context import context_value
from dash._utils import AttributeDict
import pytest

from dashboard.pages.page_home import change_page, manage_pipeline_status


def test_manage_pipeline_status_callback_deactivation():
    """Test manage_pipeline_status deactivation"""

    def run_callback():
        context_value.set(
            AttributeDict(**{
                "triggered_inputs": [
                    {"prop_id": "run_pause_click.n_clicks"},
                    {"prop_id": "stop_pipe_click.n_clicks"}
                ]
            })
        )
        return manage_pipeline_status(
            active_tab="closed",
            pipeline_num=100,
            run_pause_click=0,
            stop_pipe_click=0,
            pipeline_comments={"dummy chat dict": ["stop", "go"]}
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert all(res == no_update for res in response)


def test_manage_pipeline_status_callback_activation():
    """Test manage_pipeline_status activation"""

    def run_callback():
        context_value.set(
            AttributeDict(**{
                "triggered_inputs": [
                    # {"prop_id": "run_pause_click.n_clicks"},
                    # {"prop_id": "stop_pipe_click.n_clicks"}
                ]
            })
        )
        return manage_pipeline_status(
            active_tab="opened",
            pipeline_num=101,
            run_pause_click=0,
            stop_pipe_click=0,
            pipeline_comments={"dummy chat dict": ["stop", "go"]}
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    popup_open, popup_message, run_pause_disabled, stop_disabled = response
    assert not popup_open
    assert not popup_message
    assert not run_pause_disabled
    assert not stop_disabled


def test_manage_pipeline_status_callback_resume_pipeline():
    """Test resume pipeline"""

    def run_callback():
        context_value.set(
            AttributeDict(**{
                "triggered_inputs": [
                    {"prop_id": "run_pause_click.n_clicks"},
                    {"prop_id": "stop_pipe_click.n_clicks"}
                ]
            })
        )
        return manage_pipeline_status(
            active_tab="opened",
            # This specific issue defined in `tests/conftest.py` to test
            # this callback.
            pipeline_num=102,
            run_pause_click=1,
            stop_pipe_click=0,
            pipeline_comments={"dummy chat dict": ["stop", "go"]}
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    popup_open, popup_message, run_pause_disabled, stop_disabled = response
    assert popup_open
    assert popup_message == "The issue has been resumed."
    assert not run_pause_disabled
    assert not stop_disabled


def test_manage_pipeline_status_callback_pause_pipeline():
    """Test pause pipeline"""

    def run_callback():
        context_value.set(
            AttributeDict(**{
                "triggered_inputs": [
                    {"prop_id": "run_pause_click.n_clicks"},
                    {"prop_id": "stop_pipe_click.n_clicks"}
                ]
            })
        )
        return manage_pipeline_status(
            active_tab="opened",
            # This specific issue defined in `tests/conftest.py` to test
            # this callback.
            pipeline_num=103,
            run_pause_click=1,
            stop_pipe_click=0,
            pipeline_comments={"dummy chat dict": ["stop", "go"]}
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    popup_open, popup_message, run_pause_disabled, stop_disabled = response
    assert popup_open
    assert popup_message == "The issue has been paused."
    assert not run_pause_disabled
    assert not stop_disabled


def test_manage_pipeline_status_callback_stop_pipeline():
    """Test stop pipeline"""

    def run_callback():
        context_value.set(
            AttributeDict(**{
                "triggered_inputs": [{"prop_id": "stop_pipe_click.n_clicks"}]
            })
        )
        return manage_pipeline_status(
            active_tab="opened",
            # This specific issue defined in `tests/conftest.py` to test
            # this callback.
            pipeline_num=103,
            run_pause_click=0,
            stop_pipe_click=1,
            pipeline_comments={"dummy chat dict": ["stop", "go"]}
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    popup_open, popup_message, run_pause_disabled, stop_disabled = response
    assert popup_open
    assert popup_message == "The issue has been stopped."
    assert run_pause_disabled
    assert stop_disabled


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
                           cnclick=cnclick,
                           active_tab=active_tab,
                           cache_page=cache_page)

    ctx = copy_context()
    response = ctx.run(run_callback)
    cache_page, opened_prev_disabled, closed_prev_disabled = response

    assert cache_page == expected_cache_page
    assert opened_prev_disabled == expected_opened_prev_disabled
    assert closed_prev_disabled == expected_closed_prev_disabled
