import re


def update_simple_template(params, simple_mlunet, author_name, rtdc_paths,
                           template):
    """Update th simple issue template with user selected options"""
    # Uncheck all the boxes in the template before update
    template = template.replace("[x]", "[ ]")

    for param in params:
        param_lower = param.lower()
        if param_lower in template.lower() or param in template:
            template = re.sub(re.escape(f"[ ] {param}"), f"[x] {param}",
                              template, flags=re.IGNORECASE)

    if simple_mlunet:
        template = re.sub(re.escape("[ ] mlunet"), "[x] mlunet",
                          template, flags=re.IGNORECASE)

        # Option after which you want to add a new line
        mlunet_option = "mlunet: UNET"

        # Find the position of the mlunet option in the template
        word_index = template.find(mlunet_option)

        # Split the string at the position of the specific word
        first_part = template[:word_index + len(mlunet_option)]
        second_part = template[word_index + len(mlunet_option):]

        ckp_part = f"\n        - [x] model_file={simple_mlunet['model_file']}"

        # Join the parts with a model_file in between
        template = first_part + ckp_part + second_part

    template = template.split("- **Data to Process**")[0]
    template = template + "- **Data to Process**"

    for path in rtdc_paths:
        template = template + f"\n   - [x] {path}"

    # Add html break for smooth paring
    template = template + "\n\n    <!-- option end -->"

    # Insert the username in the issue description
    template = template + (f"\n- __Author__"
                           f"\n   - [x] username={author_name}")

    return template


def update_advanced_template(params_dict, author_name, rtdc_files, template):
    """Update th advanced issue template with user selected options"""
    # Get the parameter section of the template
    template = template.split("- **Segmentation**")[0]
    # Define the sections, subsections and their corresponding default values
    sections = {
        "Segmentation": {
            "dcevent version": {
                "dcevent version=latest": {},
            },
            "Segmentation Algorithm": {
                "mlunet: UNET": {
                    "model_file": "unet-double-d3-f3_g1_81bbe.ckp"},
                "legacy: Legacy thresholding with OpenCV": {
                    "thresh": -6,
                    "blur": 0,
                    "binaryops": 5,
                    "diff_method": 1,
                    "clear_border": True,
                    "fill_holes": True,
                    "closing_disk": 5,
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
                "norm gating": {"online_gates": False,
                                "size_thresh_mask": 0},
            },
            "Further Options": {
                "--reproduce": {},
            },
        },
        "Prediction": {
            "Classification Model": {
                "bloody-bunny_g1_bacae: Bloody Bunny": {}
            }
        },
        "Post Analysis": {
            "Benchmarking": {},
            "Scatter Plot": {},
        },
        "Data to Process": {}
    }
    # Loop through sections and subsections to update the template
    for sec_head, sub1 in sections.items():
        template += f"\n- **{sec_head}**"
        for sub2, sub3 in sub1.items():
            if sub3:
                template += f"\n  - {sub2}"
                for sub4, defaults in sub3.items():
                    sub4_check = "x" if sub4 in params_dict else " "
                    template += f"\n    - [{sub4_check}] {sub4}"
                    # Loop through hard-coded default values from above dict
                    for pkey, pval in defaults.items():
                        # If the parameter value exists in params_dict, get it.
                        # otherwise, get the default value.
                        curr_val = params_dict.get(sub4, {}).get(pkey, pval)
                        # Update template with tick, param name, and curr_value
                        template += (f"\n      - [{sub4_check}] "
                                     f"{pkey}={curr_val}")
                    template += "\n    <!-- option end -->"
            else:
                sub2_check = "x" if sub2 in params_dict else " "
                template += f"\n  - [{sub2_check}] {sub2}"
                template += "\n    <!-- option end -->"

    # Add user selected files to the template
    for path in rtdc_files:
        template += f"\n  - [x] {path}"

    # Add html break for smooth paring
    template = template + "\n\n    <!-- option end -->"

    # Insert the username in the issue description
    template = template + (f"\n- __Author__"
                           f"\n   - [x] username={author_name}")

    return template
