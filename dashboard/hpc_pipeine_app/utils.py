from ..gitlab_api import gitlab_api

simple_template, advanced_template = gitlab_api.get_templates()


def update_simple_template(params, template=simple_template):
    # Uncheck all the boxes in the template before update
    template = template.replace(f"[x]", f"[ ]")
    params_lower = [p.lower() for p in params]
    for p_low, p_nrm in zip(params_lower, params):
        if p_low in params_lower and p_low in template.lower():
            template = template.replace(f"[ ] {p_nrm}", f"[x] {p_nrm}")
    return template
