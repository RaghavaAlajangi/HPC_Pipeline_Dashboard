import re


def update_simple_template(params, rtdc_paths, template):
    # Uncheck all the boxes in the template before update
    template = template.replace("[x]", "[ ]")

    for param in params:
        param_lower = param.lower()
        if param_lower in template.lower() or param in template:
            template = re.sub(re.escape(f"[ ] {param}"), f"[x] {param}",
                              template, flags=re.IGNORECASE)

    template = template.split("- **Data to Process**")[0]
    template = template + "- **Data to Process**"

    for path in rtdc_paths:
        template = template + f"\n   - [x] {path}"

    return template


def update_advanced_template(params, rtdc_paths, template):
    pass
