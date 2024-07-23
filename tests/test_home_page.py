from contextvars import copy_context

from dash import no_update
from dash._callback_context import context_value
from dash._utils import AttributeDict

from dashboard.pages.page_home import manage_pipeline_status


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
