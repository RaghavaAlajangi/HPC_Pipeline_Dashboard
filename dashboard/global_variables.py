import os

from .gitlab_api import get_gitlab_obj

DBC_CSS = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap"
           "-templates@V1.0.1/dbc.min.css")

PROJECT_REPO_URL = "https://gitlab.gwdg.de/blood_data_analysis/" \
                   "hpc_pipeline_dashboard"
GITLAB_LOGO_URL = "https://about.gitlab.com/images/press" \
                  "/logo/png/gitlab-icon-rgb.png"

PATHNAME_PREFIX = os.getenv("BASENAME_PREFIX")


gitlab_obj = get_gitlab_obj()
