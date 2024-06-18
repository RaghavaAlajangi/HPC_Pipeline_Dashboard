from contextvars import copy_context
from unittest.mock import MagicMock

from dash import no_update
from dash._callback_context import context_value
from dash._utils import AttributeDict
import dash_bootstrap_components as dbc
import pytest

from dashboard.pages.page_simple import (collect_simple_pipeline_params,
                                         show_and_cache_segment_options,
                                         simple_data_to_process_section,
                                         simple_page_layout,
                                         simple_post_analysis_section,
                                         simple_prediction_section,
                                         simple_request_submission_popup,
                                         simple_segmentation_section,
                                         toggle_legacy_options,
                                         toggle_simple_create_pipeline_button,
                                         toggle_unet_options)


@pytest.fixture
def mock_request_gitlab_instance(mocker):
    """Mock the request_gitlab instance"""
    run_pipeline_mocker = mocker.patch(
        "dashboard.gitlab.request_gitlab.run_pipeline")

    # Simulate the behavior of request_gitlab.run_pipeline when called
    # This will skip the actual execution of run_pipeline
    run_pipeline_value = MagicMock()
    run_pipeline_value.notes.create.return_value = {"body": "mocked_GO"}

    run_pipeline_mocker.return_value = run_pipeline_value
    return run_pipeline_mocker


@pytest.fixture
def mock_dvc_gitlab_instance(mocker):
    """Mock the dvc_gitlab instance"""
    dvc_repo_mocker = mocker.patch(
        "dashboard.gitlab.dvc_gitlab.get_model_metadata")

    mocked_model_metadata = {
        "test_checkpoint_1": {"device": "accelerator", "type": "blood"},
        "test_checkpoint_2": {"device": "naiad", "type": "blood and beads"}
    }

    # Attach model metadata return value to the mocker
    dvc_repo_mocker.return_value = mocked_model_metadata

    return dvc_repo_mocker


def test_simple_title_section():
    """Test simple_title_section type"""
    assert isinstance(simple_page_layout("/test_path/"), dbc.Toast)


def test_simple_segmentation_section():
    """Test simple_segmentation_section type"""
    assert isinstance(simple_segmentation_section(), dbc.AccordionItem)


def test_simple_prediction_section():
    """Test simple_prediction_section type"""
    assert isinstance(simple_prediction_section(), dbc.AccordionItem)


def test_simple_post_analysis_section():
    """Test simple_prediction_section type"""
    assert isinstance(simple_post_analysis_section(), dbc.AccordionItem)


def test_simple_data_to_process_section():
    """Test simple_data_to_process_section type"""
    assert isinstance(simple_data_to_process_section(), dbc.AccordionItem)


def test_show_and_cache_segment_options_callback(mock_dvc_gitlab_instance):
    """Test segmentation method selection"""

    def run_callback():
        return show_and_cache_segment_options(
            unet_click=["mlunet"],
            measurement_type="model_checkpoint",
            legacy_click=["legacy"],
            legacy_thresh="-2"
        )

    # Run the callback within the appropriate context
    ctx = copy_context()
    check_boxes, segm_opt = ctx.run(run_callback)

    assert len(check_boxes) == 2
    assert check_boxes[0].value == "test_checkpoint_1"
    assert check_boxes[1].value == "test_checkpoint_2"
    assert isinstance(segm_opt, dict)
    assert "mlunet" in segm_opt.keys()


def test_toggle_unet_options_callback_activation():
    """Test unet options expansion when a user clicks on unet switch"""

    def run_callback():
        return toggle_unet_options(unet_click=["mlunet"])

    # Run the callback within the appropriate context
    ctx = copy_context()
    response = ctx.run(run_callback)
    assert isinstance(response, dict)
    assert response["display"] == "block"


def test_toggle_unet_options_callback_deactivation():
    """Test unet options contraction when a user clicks on unet switch"""

    def run_callback():
        return toggle_unet_options(unet_click=[])

    # Run the callback within the appropriate context
    ctx = copy_context()
    response = ctx.run(run_callback)
    assert isinstance(response, dict)
    assert response["display"] == "none"


def test_toggle_legacy_options_callback_activation():
    """Test legacy options expansion when a user clicks on legacy switch"""

    def run_callback():
        return toggle_legacy_options(legacy_click=["legacy"])

    # Run the callback within the appropriate context
    ctx = copy_context()
    response = ctx.run(run_callback)
    assert isinstance(response, dict)
    assert response["display"] == "block"


def test_toggle_legacy_options_callback_deactivation():
    """Test legacy options contraction when a user clicks on legacy switch"""

    def run_callback():
        return toggle_legacy_options(legacy_click=[])

    # Run the callback within the appropriate context
    ctx = copy_context()
    response = ctx.run(run_callback)
    assert isinstance(response, dict)
    assert response["display"] == "none"


def test_collect_simple_pipeline_params_callback_activation():
    """Test callback activation, user selection of parameters and update
    simple pipeline template"""

    def run_callback():
        return collect_simple_pipeline_params(
            author_name="test_username",
            simple_title="test_title",
            cached_seg_options={"legacy": {"thresh": -6},
                                "mlunet": {"model_file": "model_checkpoint"}},
            simple_classifier=["bloody-bunny_g1_bacae"],
            simple_postana=["benchmarking"],
            selected_files=[{"filepath": "test1.rtdc"},
                            {"filepath": "test2.rtdc"}]
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert "description" in response.keys()
    assert "title" in response.keys()
    assert "test_title" in response["title"]
    assert "[x] username=test_username" in response["description"]
    assert "[x] mlunet" in response["description"]
    assert "[x] model_file=model_checkpoint" in response["description"]
    assert "[x] legacy" in response["description"]
    assert "[x] bloody-bunny_g1_bacae" in response["description"]
    assert "[x] test1.rtdc" in response["description"]
    assert "[x] test2.rtdc" in response["description"]


def test_collect_simple_pipeline_params_callback_deactivation():
    """Test callback deactivation"""

    def run_callback():
        return collect_simple_pipeline_params(
            author_name="",
            simple_title="test_title",
            cached_seg_options={"legacy": {"thresh": -6},
                                "mlunet": {"model_file": "model_checkpoint"}},
            simple_classifier=["bloody-bunny_g1_bacae"],
            simple_postana=["benchmarking"],
            selected_files=[{"filepath": "test1.rtdc"},
                            {"filepath": "test2.rtdc"}]
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert response == no_update


def test_toggle_simple_create_pipeline_button_callback_activation():
    """Test create_pipeline_button activation"""

    def run_callback():
        return toggle_simple_create_pipeline_button(
            author_name="test_username",
            title="test_title",
            selected_files=[{"filepath": "test1.rtdc"}],
            cached_seg_options={"legacy": {"thresh": "-6"}},
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert not response


def test_toggle_simple_create_pipeline_button_callback_deactivation():
    """Test create_pipeline_button deactivation"""

    def run_callback():
        return toggle_simple_create_pipeline_button(
            author_name="test_username",
            title="test_title",
            selected_files=[{"filepath": "test1.rtdc"}],
            # Empty data should not activate the "Create Pipeline" button
            cached_seg_options={}
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert response


def test_simple_request_submission_popup_callback_activation(
        mock_request_gitlab_instance):
    """Test pipeline submission and activate notification popup"""

    test_template = {
        "title": "test without notes create",
        "description": "test description"
    }

    def run_callback():
        context_value.set(
            AttributeDict(**{
                "triggered_inputs": [
                    {"prop_id": "create_simple_pipeline_button.n_clicks"}]
            })
        )
        return simple_request_submission_popup(
            1, cached_template=test_template, close_popup=0, popup=False
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert response


def test_simple_request_submission_popup_callback_close_popup():
    """Test close notification popup"""

    test_template = {
        "title": "testing",
        "description": "test description"
    }

    def run_callback():
        context_value.set(
            AttributeDict(**{
                "triggered_inputs": [
                    {"prop_id": "simple_popup_close.n_clicks"}]
            })
        )
        return simple_request_submission_popup(
            0, cached_template=test_template, close_popup=1, popup=True
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert not response


def test_simple_request_submission_popup_callback_deactivation():
    """Test callback deactivation"""
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
        return simple_request_submission_popup(
            0, cached_template=test_template, close_popup=0, popup=False
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert not response
