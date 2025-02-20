def update_template(params_dict, author_name, rtdc_files, template, sections):
    """Update an issue template with user-selected options."""
    # Remove existing selections from the template
    template = template.split("- **Segmentation**")[0]

    # Define the sections, subsections, and their corresponding default values
    for main_dict_key, sub_dict_1 in sections.items():
        template += f"\n- **{main_dict_key}**"
        for sub_dict_key_1, sub_dict_1 in sub_dict_1.items():
            # Check if sub_dict_1 is a not empty dict
            if sub_dict_1:
                template += f"\n  - {sub_dict_key_1}"
                for sub_dict_key_2, hard_values in sub_dict_1.items():
                    opt2_check = "x" if sub_dict_key_2 in params_dict else " "
                    user_values = params_dict.get(sub_dict_key_2, {})
                    # Check if defaults
                    if isinstance(hard_values, dict):
                        template += f"\n    - [{opt2_check}] {sub_dict_key_2}"
                        # Loop through hard-coded default values from above
                        # dict
                        for pkey, pval in hard_values.items():
                            # If the parameter value exists in params_dict,
                            # get it. Otherwise, get the default value.
                            cval = user_values.get(pkey, pval)
                            # Update template with tick, param name, and
                            # curr_value
                            template += (
                                f"\n      - [{opt2_check}] {pkey}={cval}"
                            )
                        template += "\n    <!-- option end -->"
                    else:
                        uval = params_dict.get(sub_dict_key_2, "")

                        template += (
                            f"\n    - [{opt2_check}] {sub_dict_key_2} {uval}"
                        )
            else:
                opt1_check = "x" if sub_dict_key_1 in params_dict else " "
                template += f"\n  - [{opt1_check}] {sub_dict_key_1}"
        template += "\n    <!-- option end -->"

    # Add user selected files to the template
    template += "\n- **Data to Process**"
    for path in rtdc_files:
        template += f"\n  - [x] {path}"

    # Add html break for smooth paring
    template = template + "\n    <!-- option end -->"

    # Insert the username in the issue description
    template = template + (
        f"\n- __Author__" f"\n   - [x] username={author_name}"
    )

    return template


def update_simple_template(params_dict, author_name, rtdc_files, template):
    """Update the simple issue template."""
    sections = {
        "Segmentation": {
            "dcevent version": {"dcevent version=latest": {}},
            "Segmentation Algorithm": {
                "mlunet: UNET": {
                    "model_file": "unet-double-d3-f3_g1_81bbe.ckp"
                },
                "legacy: Legacy thresholding with OpenCV": {"thresh": -6},
                "thresh: thresholding segmentation": {},
                "watershed: Watershed algorithm": {},
                "std: Standard-deviation-based thresholding": {},
            },
            "Further Options": {"--reproduce": None, "--num-frames": 1000},
        },
        "Prediction": {
            "Classification Model": {
                "bloody-bunny_g1_bacae: Bloody Bunny": None
            }
        },
        "Post Analysis": {"Benchmarking": {}, "Scatter Plot": {}},
    }
    return update_template(
        params_dict, author_name, rtdc_files, template, sections
    )


def update_advanced_template(params_dict, author_name, rtdc_files, template):
    """Update the advanced issue template."""
    sections = {
        "Segmentation": {
            "dcevent version": {"dcevent version=latest": {}},
            "Segmentation Algorithm": {
                "mlunet: UNET": {
                    "model_file": "unet-double-d3-f3_g1_81bbe.ckp"
                },
                "legacy: Legacy thresholding with OpenCV": {
                    "thresh": -6,
                    "blur": 0,
                    "binaryops": 5,
                    "diff_method": 1,
                    "clear_border": True,
                    "fill_holes": True,
                    "closing_disk": 5,
                },
                "thresh: thresholding segmentation": {
                    "clear_border": "True",
                    "closing_disk": 2,
                    "fill_holes": "True",
                    "thresh": -6,
                },
                "watershed: Watershed algorithm": {
                    "clear_border": True,
                    "fill_holes": True,
                    "closing_disk": 5,
                },
                "std: Standard-deviation-based thresholding": {
                    "clear_border": True,
                    "fill_holes": True,
                    "closing_disk": 5,
                },
            },
            "Background Correction/Subtraction Method": {
                "rollmed: Rolling median RT-DC background image computation": {
                    "kernel_size": 100,
                    "batch_size": 10000,
                },
                "sparsemed: Sparse median background correction with "
                "cleansing": {
                    "kernel_size": 2,
                    "split_time": 1.0,
                    "thresh_cleansing": 0,
                    "frac_cleansing": 0.8,
                },
            },
            "Available gating options": {
                "norm gating": {"online_gates": False, "size_thresh_mask": 0}
            },
            "Further Options": {"--reproduce": None, "--num-frames": 1000},
        },
        "Prediction": {
            "Classification Model": {
                "bloody-bunny_g1_bacae: Bloody Bunny": None
            }
        },
        "Post Analysis": {"Benchmarking": {}, "Scatter Plot": {}},
    }
    return update_template(
        params_dict, author_name, rtdc_files, template, sections
    )
