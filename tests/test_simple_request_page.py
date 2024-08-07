from contextvars import copy_context

from dash import no_update
from dash._callback_context import context_value
from dash._utils import AttributeDict
import dash_bootstrap_components as dbc
import pytest

from dashboard.pages.page_simple import (collect_pipeline_params,
                                         data_to_process_section,
                                         pipeline_parameters_section,
                                         request_submission_popup,
                                         simple_page_layout,
                                         toggle_create_pipeline_button)


def test_simple_title_section():
    """Test simple_title_section type"""
    assert isinstance(simple_page_layout("/test_path/"), dbc.Toast)


def test_data_to_process_section():
    """Test data_to_process_section type"""
    assert isinstance(data_to_process_section(), dbc.AccordionItem)


def test_pipeline_parameters_section():
    """Test pipeline_parameters_section type"""
    assert isinstance(pipeline_parameters_section(), dbc.AccordionItem)


def test_collect_pipeline_params_callback_activation():
    """Test collection of user input and update simple pipeline template"""

    def run_callback():
        return collect_pipeline_params(
            author_name="test_username",
            simple_title="test_title",
            dprocess_key=["mp_mode", "mp_batch_size"],
            dprocess_val=["mp", 16000],
            selected_files=[{"filepath": "test1.rtdc"},
                            {"filepath": "test2.rtdc"}]
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert "description" in response.keys()
    assert "title" in response.keys()
    assert "test_title" in response["title"]
    assert "[x] username=test_username" in response["description"]
    assert "mp_mode: mp" in response["description"]
    assert "mp_batch_size: 16000" in response["description"]


def test_collect_pipeline_params_callback_deactivation():
    """Test callback deactivation"""

    def run_callback():
        return collect_pipeline_params(
            author_name="",
            simple_title="test_title",
            dprocess_key=["mp_mode", "mp_batch_size"],
            dprocess_val=["mp", 16000],
            selected_files=[{"filepath": "test1.rtdc"},
                            {"filepath": "test2.rtdc"}]
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert response == no_update


@pytest.mark.parametrize(
    "author_name, title, selected_files, expected_response",
    [
        # Test case 1: activate create pipeline button
        (
                "test_username",
                "test_title",
                [{"filepath": "test1.hdf5"}],
                False
        ),
        # Test case 2: deactivate create pipeline button
        (
                "test_username",
                "",
                [{"filepath": "test1.hdf5"}],
                True
        )
    ]
)
def test_toggle_create_pipeline_button_callback(author_name,
                                                title, selected_files,
                                                expected_response):
    """Test functionality of toggle_create_pipeline_button callback"""

    def run_callback():
        return toggle_create_pipeline_button(author_name, title,
                                             selected_files)

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert response == expected_response


@pytest.mark.parametrize(
    "triggered_inputs, bclick, cached_template, close_popup, popup, "
    "expected_response",
    [
        # Test case 1: pipeline submission and activate notification popup
        (
                [{"prop_id": "simple_popup_close.n_clicks"}],
                0,
                {"title": "testing",
                 "description": "test description"
                 }, 1, True,
                False
        ),
        # Test case 2: close notification popup
        (
                [{"prop_id": "create_simple_pipeline_button.n_clicks"}],
                1,
                {"title": "testing",
                 "description": "test description"
                 }, 0, False,
                False
        ),
        # Test case 3: callback deactivation
        (
                [{"prop_id": "dummy_click.n_clicks"}],
                0,
                {"title": "testing",
                 "description": "test description"
                 }, 0, False,
                False
        )
    ]
)
def test_request_submission_popup_callback(triggered_inputs, bclick,
                                           cached_template, close_popup, popup,
                                           expected_response):
    """Test functionality of request_submission_popup callback"""

    def run_callback():
        context_value.set(
            AttributeDict(**{
                "triggered_inputs": triggered_inputs
            })
        )
        return request_submission_popup(
            bclick, cached_template, close_popup, popup
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert response == expected_response
