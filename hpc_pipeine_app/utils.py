from .issue_templates import simple_template


def update_simple_template(params, template=simple_template):
    # global simple_template
    params_lower = [p.lower() for p in params]
    for pl, p in zip(params_lower, params):
        if pl in params_lower and pl in template.lower():
            template = template.replace(f"[ ] {p}", f"[x] {p}")
    return template
