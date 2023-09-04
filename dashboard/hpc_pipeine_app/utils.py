def update_simple_template(params, rtdc_paths, template):
    # Uncheck all the boxes in the template before update
    template = template.replace("[x]", "[ ]")

    for p_nrm in params:
        p_low = p_nrm.lower()
        if p_low in template.lower() or p_nrm in template:
            template = template.replace(f"[ ] {p_nrm}", f"[x] {p_nrm}")
            template = template.replace(f"[ ] {p_low}", f"[x] {p_low}")

    template = template.split("- **Data to Process**")[0]
    template = template + "- **Data to Process**"

    for path in rtdc_paths:
        template = template + f"\n   - [x] {path}"

    return template


def update_advanced_template(params, rtdc_paths, template):
    pass
