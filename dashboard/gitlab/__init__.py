import os

from dotenv import load_dotenv

from .base import AuthenticationError
from .dvc_repo import DVCRepoAPI
from .requests_repo import RequestRepoAPI

# Load environment variables from .env file
load_dotenv()
REPO_URL = os.getenv("REPO_URL")
REPO_TOKEN = os.getenv("REPO_TOKEN")
PROJECT_NUM = os.getenv("PROJECT_NUM")
DVC_REPO_TOKEN = os.getenv("DVC_REPO_TOKEN")
DVC_REPO_PROJECT_NUM = os.getenv("DVC_REPO_PROJECT_NUM")

# Create instances of RequestRepoAPI and DVCRepoAPI
try:
    request_gitlab = RequestRepoAPI(REPO_URL, REPO_TOKEN, PROJECT_NUM)
except AuthenticationError as auth_error:
    print(auth_error)

try:
    dvc_gitlab = DVCRepoAPI(REPO_URL, DVC_REPO_TOKEN, DVC_REPO_PROJECT_NUM)
except AuthenticationError as auth_error:
    print(auth_error)
