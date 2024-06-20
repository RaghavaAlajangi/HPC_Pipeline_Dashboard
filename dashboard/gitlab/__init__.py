import functools
import os

from dotenv import load_dotenv

from .base import AuthenticationError, BaseAPI
from .dvc_repo import DVCRepoAPI
from .requests_repo import RequestRepoAPI


@functools.lru_cache()
def get_gitlab_instances():
    # Load environment variables from .env file
    load_dotenv()
    request_gitlab = RequestRepoAPI(
        os.getenv("MY_REPO_URL"),
        os.getenv("REPO_TOKEN"),
        os.getenv("PROJECT_NUM")
    )
    dvc_gitlab = DVCRepoAPI(
        os.getenv("REPO_URL"),
        os.getenv("DVC_REPO_TOKEN"),
        os.getenv("DVC_REPO_PROJECT_NUM")
    )
    return request_gitlab, dvc_gitlab
