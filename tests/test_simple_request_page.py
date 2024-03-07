from contextvars import copy_context
import dash_bootstrap_components as dbc
from dash._callback_context import context_value
from dash._utils import AttributeDict
import pytest

from ..dashboard.pages.page_simple import (
    simple_page_layout, toggle_simple_create_pipeline_button,
    simple_request_submission_popup, collect_simple_pipeline_params
)
from ..dashboard.gitlab import request_gitlab


def test_simple_request_layout():
    """Test simple_request layout"""
    assert isinstance(simple_page_layout("/test_path/"), dbc.Toast)


@pytest.fixture
def mock_request_gitlab(mocker):
    # Create a mock for request_gitlab.run_pipeline
    return mocker.patch.object(request_gitlab, "run_pipeline")


def test_simple_request_popup_to_open(mock_request_gitlab, mocker):
    """Test open notification popup when the user clicks on create pipeline
    button"""
    test_template = {
        "title": "testing",
        "description": "test description"
    }
    # Simulate the behavior of request_gitlab.run_pipeline when called
    # This will skip the actual execution of run_pipeline
    mock_request_gitlab.return_value = None

    def run_callback():
        context_value.set(
            AttributeDict(**{
                "triggered_inputs": [
                    {"prop_id": "create_simple_pipeline_button.n_clicks"}]
            })
        )
        return simple_request_submission_popup(0, test_template, 0, False)

    ctx = copy_context()
    output = ctx.run(run_callback)
    assert output


def test_simple_request_popup_to_close():
    """Test close notification popup when the user clicks on close button the
    popup"""
    test_template = {
        "title": "testing",
        "description": "test description"
    }

    def run_callback():
        context_value.set(
            AttributeDict(**{
                "triggered_inputs": [{"prop_id": "dummy_click.n_clicks"}]
            })
        )
        return simple_request_submission_popup(0, test_template, 1, True)

    ctx = copy_context()
    output = ctx.run(run_callback)
    assert not output


def test_simple_request_popup_default():
    """Test default behaviour of notification popup"""
    test_template = {
        "title": "testing",
        "description": "test description"
    }

    def run_callback():
        context_value.set(
            AttributeDict(**{
                "triggered_inputs": [{"prop_id": "dummy_click.n_clicks"}]
            })
        )
        return simple_request_submission_popup(0, test_template, 0, False)

    ctx = copy_context()
    output = ctx.run(run_callback)
    assert not output


def test_simple_create_pipeline_button_enable():
    """Test enabling create_pipeline_button"""

    def run_callback():
        return toggle_simple_create_pipeline_button("test_title", ["f1", "f2"])

    ctx = copy_context()
    output = ctx.run(run_callback)
    assert not output


def test_simple_create_pipeline_button_disable():
    """Test disabling create_pipeline_button"""

    def run_callback():
        return toggle_simple_create_pipeline_button("", ["f1", "f2"])

    ctx = copy_context()
    output = ctx.run(run_callback)
    assert output


def test_collect_simple_pipeline_params():
    """Test collection of user input and update simple template"""

    def run_callback():
        return collect_simple_pipeline_params(
            "test title",
            ["legacy", "mlunet"],
            ["bloody-bunny_g1_bacae"],
            ["benchmarking"],
            [{"filepath": "test1.rtdc"}, {"filepath": "test2.rtdc"}]
        )

    ctx = copy_context()
    output = ctx.run(run_callback)
    assert "description" in output.keys()
    assert "title" in output.keys()
    assert "test title" in output["title"]
    assert "[x] mlunet" in output["description"]
    assert "[x] legacy" in output["description"]
    assert "[x] bloody-bunny_g1_bacae" in output["description"]
    assert "[x] test1.rtdc" in output["description"]
    assert "[x] test2.rtdc" in output["description"]
