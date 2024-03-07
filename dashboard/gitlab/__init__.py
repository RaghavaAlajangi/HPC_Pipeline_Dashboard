import os
from pathlib import Path

import yaml

from .base import AuthenticationError
from .dvc_repo import DVCRepoAPI
from .requests_repo import RequestRepoAPI

secret_yaml_path = Path(__file__).parents[2] / "secrets.yaml"


def load_auth_data():
    """Loads auth_data from either environment variables or a secrets.yaml.
    """
    auth_data = {}
    if os.getenv("REPO_URL"):
        print("Loading SECRETS from environment variables")
        # Load from environment variables
        auth_data["REPO_URL"] = os.getenv("REPO_URL")
        auth_data["REPO_TOKEN"] = os.getenv("REPO_TOKEN")
        auth_data["PROJECT_NUM"] = os.getenv("PROJECT_NUM")
        auth_data["DVC_REPO_TOKEN"] = os.getenv("DVC_REPO_TOKEN")
        auth_data["DVC_REPO_PROJECT_NUM"] = os.getenv("DVC_REPO_PROJECT_NUM")
    else:
        print("Loading SECRETS from secrets.yaml")
        # Load from secret_data.yaml
        with open(secret_yaml_path, "r") as file:
            auth_data = yaml.safe_load(file)
    return auth_data


# Load auth_data
auth_data = load_auth_data()

# Create instances of RequestRepoAPI and DVCRepoAPI
try:
    request_gitlab = RequestRepoAPI(auth_data.get("REPO_URL"),
                                    auth_data.get("REPO_TOKEN"),
                                    auth_data.get("PROJECT_NUM"))
except AuthenticationError as auth_error:
    print(auth_error)

try:
    dvc_gitlab = DVCRepoAPI(auth_data.get("REPO_URL"),
                            auth_data.get("DVC_REPO_TOKEN"),
                            auth_data.get("DVC_REPO_PROJECT_NUM"))
except AuthenticationError as auth_error:
    print(auth_error)
