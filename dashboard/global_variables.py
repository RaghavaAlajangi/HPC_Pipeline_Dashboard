import os

from .gitlab_api import GitLabAPI, AuthenticationError

# Define the URL for the Dash Bootstrap CSS
DBC_CSS = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap"
           "-templates@V1.0.1/dbc.min.css")

# Define the URL for the GitLab project repository
PROJECT_REPO_URL = "https://gitlab.gwdg.de/blood_data_analysis/" \
                   "hpc_pipeline_dashboard"

# Define the URL for the GitLab logo image
GITLAB_LOGO_URL = "https://about.gitlab.com/images/press" \
                  "/logo/png/gitlab-icon-rgb.png"

# Set the app prefix
PATHNAME_PREFIX = os.getenv("BASENAME_PREFIX")
GITLAB_URL = os.getenv("REPO_URL")

# Get the HPC_Pipeline_requests repo credentials as environment variables
REQUEST_REPO_TOKEN = os.getenv("REPO_TOKEN")
REQUEST_PROJECT_NUM = os.getenv("PROJECT_NUM")

# Get the HPC_Pipeline_data repo credentials as environment variables
DVC_REPO_TOKEN = os.getenv("DVC_REPO_TOKEN")
DVC_REPO_PROJECT_NUM = os.getenv("DVC_REPO_PROJECT_NUM")

# Create a HPC_Pipeline_requests repo gitlab instance
try:
    request_gitlab = GitLabAPI(GITLAB_URL, REQUEST_REPO_TOKEN,
                               REQUEST_PROJECT_NUM)
except AuthenticationError as auth_error:
    print(auth_error)

# Create a HPC_Pipeline_data repo gitlab instance
try:
    dvc_gitlab = GitLabAPI(GITLAB_URL, DVC_REPO_TOKEN, DVC_REPO_PROJECT_NUM)
except AuthenticationError as auth_error:
    print(auth_error)
