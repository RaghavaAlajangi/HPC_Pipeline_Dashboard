import os

from .gitlab_api import GitLabAPI

# Define the URL for the Dash Bootstrap CSS
DBC_CSS = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap"
           "-templates@V1.0.1/dbc.min.css")

# Define the URL for the GitLab project repository
PROJECT_REPO_URL = "https://gitlab.gwdg.de/blood_data_analysis/" \
                   "hpc_pipeline_dashboard"

# Define the URL for the GitLab logo image
GITLAB_LOGO_URL = "https://about.gitlab.com/images/press" \
                  "/logo/png/gitlab-icon-rgb.png"

REPO_URL = os.getenv("REPO_URL")
REPO_TOKEN = os.getenv("REPO_TOKEN")
PROJECT_NUM = os.getenv("PROJECT_NUM")
PATHNAME_PREFIX = os.getenv("BASENAME_PREFIX")

# Create an instance of the GitLabAPI with the retrieved or default values
gitlab_obj = GitLabAPI(REPO_URL, REPO_TOKEN, PROJECT_NUM)
