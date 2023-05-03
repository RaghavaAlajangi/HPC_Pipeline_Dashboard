def update_simple_template(params, rtdc_paths, template):
    # Uncheck all the boxes in the template before update
    template = template.replace("[x]", "[ ]")
    params_lower = [p.lower() for p in params]
    for p_low, p_nrm in zip(params_lower, params):
        if p_low in template.lower():
            template = template.replace(f"[ ] {p_low}", f"[x] {p_low}")
        elif p_nrm in template:
            template = template.replace(f"[ ] {p_nrm}", f"[x] {p_nrm}")

    template = template.split("- **Data to Process**")[0]
    template = template + "- **Data to Process**"

    for path in rtdc_paths:
        template = template + f"\n   - [x] {path}"

    return template


def update_advanced_template(params, rtdc_paths, template):
    pass
