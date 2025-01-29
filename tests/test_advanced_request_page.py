from contextvars import copy_context

from dash._callback_context import context_value
from dash._utils import AttributeDict
import dash_bootstrap_components as dbc

from dashboard.pages.page_advanced import (
    advanced_data_to_process_section,
    advanced_page_layout,
    advanced_post_analysis_section,
    advanced_prediction_section,
    advanced_request_submission_popup,
    advanced_title_section,
    advanced_segmentation_section,
    background_correction_section,
    collect_advanced_pipeline_params,
    further_options_section,
    gating_options_section,
    show_and_cache_unet_model_meta,
    toggle_advanced_create_pipeline_button,
    toggle_legacy_options,
    toggle_norm_gate_options,
    toggle_rollmed_options,
    toggle_sparsemed_options,
    toggle_std_options,
    toggle_watershed_options,
    toggle_unet_options,
)


def test_advanced_title_section():
    """Test advanced_title_section type"""
    assert isinstance(advanced_title_section(), dbc.AccordionItem)


def test_advanced_segmentation_section():
    """Test advanced_segmentation_section type"""
    assert isinstance(advanced_segmentation_section(), dbc.AccordionItem)


def test_background_correction_section():
    """Test background_correction_section type"""
    assert isinstance(background_correction_section(), dbc.AccordionItem)


def test_gating_options_section():
    """Test gating_options_section type"""
    assert isinstance(gating_options_section(), dbc.AccordionItem)


def test_further_options_section():
    """Test further_options_section type"""
    assert isinstance(further_options_section(), dbc.AccordionItem)


def test_advanced_prediction_section():
    """Test advanced_prediction_section type"""
    assert isinstance(advanced_prediction_section(), dbc.AccordionItem)


def test_advanced_post_analysis_section():
    """Test advanced_post_analysis_section type"""
    assert isinstance(advanced_post_analysis_section(), dbc.AccordionItem)


def test_advanced_data_to_process_section():
    """Test advanced_data_to_process_section type"""
    assert isinstance(advanced_data_to_process_section(), dbc.AccordionItem)


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

    assert len(check_boxes) == 2
    assert check_boxes[0].value == "model_checkpoint_mock2.ckp"
    assert check_boxes[1].value == "model_checkpoint_mock3.ckp"
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
    threshold_key = "legacy: Legacy thresholding with OpenCV"

    def run_callback():
        return toggle_legacy_options(
            legacy_opt=[threshold_key],
            leg_keys=["thresh", "diff_method", "clear_border"],
            leg_values=["-6", "1", True])

    # Run the callback within the appropriate context
    ctx = copy_context()
    legacy_response, toggle_response = ctx.run(run_callback)
    assert isinstance(legacy_response, dict)
    assert isinstance(toggle_response, dict)
    assert threshold_key in legacy_response.keys()
    legacy_params = legacy_response[threshold_key]
    assert "thresh" in legacy_params.keys()
    assert "diff_method" in legacy_params.keys()
    assert "fill_holes" not in legacy_params.keys()
    assert toggle_response["display"] == "block"


def test_toggle_legacy_options_callback_deactivation():
    """Test legacy options contraction when a user clicks on legacy switch"""

    def run_callback():
        return toggle_legacy_options(
            legacy_opt=[],
            leg_keys=["thresh", "diff_method", "clear_border"],
            leg_values=["-6", "1", True])

    # Run the callback within the appropriate context
    ctx = copy_context()
    legacy_response, toggle_response = ctx.run(run_callback)
    assert not legacy_response
    assert isinstance(toggle_response, dict)
    assert toggle_response["display"] == "none"


def test_toggle_watershed_options_callback_activation():
    """Test watershed options expansion when a user clicks on watershed
    switch"""
    watershed_key = "watershed: Watershed algorithm"

    def run_callback():
        return toggle_watershed_options(
            watershed_opt=[watershed_key],
            water_keys=["clear_border", "closing_disk"],
            water_values=[True, "5"])

    # Run the callback within the appropriate context
    ctx = copy_context()
    watershed_response, toggle_response = ctx.run(run_callback)
    assert isinstance(watershed_response, dict)
    assert isinstance(toggle_response, dict)
    assert watershed_key in watershed_response.keys()
    legacy_params = watershed_response[watershed_key]
    assert "clear_border" in legacy_params.keys()
    assert "closing_disk" in legacy_params.keys()
    assert "fill_holes" not in legacy_params.keys()
    assert toggle_response["display"] == "block"


def test_toggle_watershed_options_callback_deactivation():
    """Test watershed options contraction when a user clicks on watershed
    switch"""

    def run_callback():
        return toggle_watershed_options(
            watershed_opt=[],
            water_keys=["clear_border", "closing_disk"],
            water_values=[True, "5"])

    # Run the callback within the appropriate context
    ctx = copy_context()
    water_response, toggle_response = ctx.run(run_callback)
    assert not water_response
    assert isinstance(toggle_response, dict)
    assert toggle_response["display"] == "none"


def test_toggle_std_options_callback_activation():
    """Test std options expansion when a user clicks on std switch"""

    std_key = "std: Standard-deviation-based thresholding"

    def run_callback():
        return toggle_std_options(
            std_opt=[std_key],
            std_keys=["clear_border", "closing_disk"],
            std_values=[True, "5"])

    # Run the callback within the appropriate context
    ctx = copy_context()
    std_response, toggle_response = ctx.run(run_callback)
    assert isinstance(std_response, dict)
    assert isinstance(toggle_response, dict)
    assert std_key in std_response.keys()
    std_params = std_response[std_key]
    assert "clear_border" in std_params.keys()
    assert "closing_disk" in std_params.keys()
    assert "fill_holes" not in std_params.keys()
    assert toggle_response["display"] == "block"


def test_toggle_std_options_callback_deactivation():
    """Test std options contraction when a user clicks on std switch"""

    def run_callback():
        return toggle_std_options(
            std_opt=[],
            std_keys=["clear_border", "closing_disk"],
            std_values=[True, "5"])

    # Run the callback within the appropriate context
    ctx = copy_context()
    std_response, toggle_response = ctx.run(run_callback)
    assert not std_response
    assert isinstance(toggle_response, dict)
    assert toggle_response["display"] == "none"


def test_toggle_rollmed_options_callback_activation():
    """Test rolling medium options expansion when a user clicks on rollmed
    switch"""
    rollmed_key = "rollmed: Rolling median RT-DC background image computation"

    def run_callback():
        return toggle_rollmed_options(
            rollmed_opt=[rollmed_key],
            rollmed_keys=["kernel_size"],
            rollmed_values=[200])

    # Run the callback within the appropriate context
    ctx = copy_context()
    rollmed_response, toggle_response = ctx.run(run_callback)
    assert isinstance(rollmed_response, dict)
    assert isinstance(toggle_response, dict)
    assert rollmed_key in rollmed_response.keys()
    rollmed_params = rollmed_response[rollmed_key]
    assert "kernel_size" in rollmed_params.keys()
    assert "fill_holes" not in rollmed_params.keys()
    assert toggle_response["display"] == "block"


def test_toggle_rollmed_options_callback_deactivation():
    """Test rolling medium options contraction when a user clicks on rollmed
    switch"""

    def run_callback():
        return toggle_rollmed_options(
            rollmed_opt=[],
            rollmed_keys=["clear_border", "closing_disk"],
            rollmed_values=[True, "5"])

    # Run the callback within the appropriate context
    ctx = copy_context()
    rollmed_response, toggle_response = ctx.run(run_callback)
    assert not rollmed_response
    assert isinstance(toggle_response, dict)
    assert toggle_response["display"] == "none"


def test_toggle_sparsemed_options_callback_activation():
    """Test sparse medium options expansion when a user clicks on sparsemed
    switch"""
    sparemed_key = "sparsemed: Sparse median background correction " \
                   "with cleansing"

    def run_callback():
        return toggle_sparsemed_options(
            sparsemed_opt=[sparemed_key],
            sparsemed_keys=["kernel_size"],
            sparsemed_values=[8])

    # Run the callback within the appropriate context
    ctx = copy_context()
    sparsemed_response, toggle_response = ctx.run(run_callback)
    assert isinstance(sparsemed_response, dict)
    assert isinstance(toggle_response, dict)
    assert sparemed_key in sparsemed_response.keys()
    sparsemed_response = sparsemed_response[sparemed_key]
    assert "kernel_size" in sparsemed_response.keys()
    assert "fill_holes" not in sparsemed_response.keys()
    assert toggle_response["display"] == "block"


def test_toggle_sparsemed_options_callback_deactivation():
    """Test sparse medium options contraction when a user clicks on sparsemed
    switch"""

    def run_callback():
        return toggle_sparsemed_options(
            sparsemed_opt=[],
            sparsemed_keys=["clear_border", "closing_disk"],
            sparsemed_values=[True, "5"])

    # Run the callback within the appropriate context
    ctx = copy_context()
    sparsemed_response, toggle_response = ctx.run(run_callback)
    assert not sparsemed_response
    assert isinstance(toggle_response, dict)
    assert toggle_response["display"] == "none"


def test_toggle_norm_gate_options_callback_activation():
    """Test sparse medium options expansion when a user clicks on sparsemed
    switch"""
    norm_gate_key = "norm gating"

    def run_callback():
        return toggle_norm_gate_options(
            ngate_opt=[norm_gate_key],
            ngate_keys=["online_gates"],
            ngate_values=[False])

    # Run the callback within the appropriate context
    ctx = copy_context()
    norm_gate_response, toggle_response = ctx.run(run_callback)
    assert isinstance(norm_gate_response, dict)
    assert isinstance(toggle_response, dict)
    assert norm_gate_key in norm_gate_response.keys()
    norm_gate_response = norm_gate_response[norm_gate_key]
    assert "online_gates" in norm_gate_response.keys()
    assert "fill_holes" not in norm_gate_response.keys()
    assert toggle_response["display"] == "block"


def test_toggle_norm_gate_options_callback_deactivation():
    """Test sparse medium options contraction when a user clicks on sparsemed
    switch"""

    def run_callback():
        return toggle_norm_gate_options(
            ngate_opt=[],
            ngate_keys=["clear_border", "closing_disk"],
            ngate_values=[True, "5"])

    # Run the callback within the appropriate context
    ctx = copy_context()
    sparsemed_response, toggle_response = ctx.run(run_callback)
    assert not sparsemed_response
    assert isinstance(toggle_response, dict)
    assert toggle_response["display"] == "none"


def test_collect_advanced_pipeline_params_callback_activation():
    """Test collection of user input and update advanced pipeline template
    when the user provides required options"""

    def run_callback():
        return collect_advanced_pipeline_params(
            author_name="test_username",
            advanced_title="test_title",
            reproduce_flag=[],
            classifier_name=["bloody-bunny_g1_bacae: Bloody Bunny"],
            post_analysis_flag=[],
            cache_unet_model_path={
                "mlunet: UNET": {"model_file": "test_checkpoint"}},
            cache_legacy_params={},
            cache_thresh_seg_params={},
            cache_watershed_params={},
            cache_std_params={},
            cache_rollmed_params={
                "rollmed: Rolling median RT-DC background image computation": {
                    "kernel_size": 200, "batch_size": 5000}},
            cache_sparsemed_params=None,
            cache_norm_gate_params={},
            selected_rows=[{"filepath": "test.rtdc"}]
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert "description" in response.keys()
    assert "title" in response.keys()
    assert "test_title" in response["title"]
    assert "[x] mlunet: UNET" in response["description"]
    assert "[x] model_file=test_checkpoint" in response["description"]
    assert "[x] bloody-bunny_g1_bacae: Bloody Bunny" in response["description"]
    assert "[x] test.rtdc" in response["description"]
    assert "[x] rollmed:" in response["description"]
    assert "[x] kernel_size=200" in response["description"]
    assert "[x] batch_size=5000" in response["description"]


def test_collect_advanced_pipeline_params_callback_deactivation():
    """Test collection of user input and update advanced template when
    the user does not provide required options"""

    def run_callback():
        return collect_advanced_pipeline_params(
            author_name="test_username",
            advanced_title="",
            reproduce_flag=[],
            classifier_name=["bloody-bunny_g1_bacae: Bloody Bunny"],
            post_analysis_flag=[],
            cache_unet_model_path={
                "mlunet: UNET": {"model_file": "test_checkpoint"}},
            cache_legacy_params={},
            cache_thresh_seg_params={},
            cache_watershed_params={},
            cache_std_params={},
            cache_rollmed_params={
                "rollmed: Rolling median RT-DC background image computation": {
                    "kernel_size": 200, "batch_size": 5000}},
            cache_sparsemed_params=None,
            cache_norm_gate_params={},
            selected_rows=[{"filepath": "test.rtdc"}]
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert not response


def test_advanced_request_submission_popup_callback_activation():
    """Test pipeline submission and activate notification popup"""

    test_template = {
        "title": "test without notes create",
        "description": "test description"
    }

    def run_callback():
        context_value.set(
            AttributeDict(**{
                "triggered_inputs": [
                    {"prop_id": "create_advanced_pipeline_button.n_clicks"}]
            })
        )
        return advanced_request_submission_popup(
            1, cached_adv_temp=test_template, close_popup=0, popup=False
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert response


def test_advanced_request_submission_popup_callback_close_popup():
    """Test close notification popup"""

    test_template = {
        "title": "testing",
        "description": "test description"
    }

    def run_callback():
        context_value.set(
            AttributeDict(**{
                "triggered_inputs": [
                    {"prop_id": "advanced_popup_close.n_clicks"}]
            })
        )
        return advanced_request_submission_popup(
            0, cached_adv_temp=test_template, close_popup=1, popup=True
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert not response


def test_advanced_request_submission_popup_callback_deactivation():
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
        return advanced_request_submission_popup(
            0, cached_adv_temp=test_template, close_popup=0, popup=False
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert not response


def test_toggle_advanced_create_pipeline_button_callback_activation():
    """Test create_pipeline_button activation"""

    def run_callback():
        return toggle_advanced_create_pipeline_button(
            author_name="test_username",
            title="test_title",
            selected_files=[{"filepath": "test1.rtdc"}],
            cached_unet_model_path={
                "mlunet: UNET": {"model_file": "test_checkpoint"}},
            cached_legacy_params={},
            cache_watershed_params={},
            cache_std_params={}
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert not response


def test_toggle_advanced_create_pipeline_button_callback_deactivation():
    """Test create_pipeline_button deactivation"""

    def run_callback():
        return toggle_advanced_create_pipeline_button(
            author_name="test_username",
            title="test_title",
            selected_files=[{"filepath": "test1.rtdc"}],
            # Empty data should not activate the "Create Pipeline" button
            cached_unet_model_path={},
            cached_legacy_params={},
            cache_watershed_params={},
            cache_std_params={}
        )

    ctx = copy_context()
    response = ctx.run(run_callback)
    assert response
