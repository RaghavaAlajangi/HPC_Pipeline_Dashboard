from datetime import datetime, timezone
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from dotenv import load_dotenv

from dashboard.gitlab import DVCRepoAPI, RequestRepoAPI

issue_template_dir = Path(__file__).parents[0] / "data"


def mock_gitlab_issue(iid, description):
    """Creates a mock gitlab issue"""
    mock_issue = MagicMock(
        id=f"123{iid}",
        iid=iid,
        title=f"Mock Test Issue {iid}",
        author={"name": f"mock_author_{iid}"},
        web_url=f"https://mock_issue_url{iid}",
        description=description,
        created_at=datetime.now(timezone.utc),
        test_list=["mock1", "mock2"]
    )
    mock_note = MagicMock(
        body="mock comment",
        created_at=datetime.utcnow().isoformat() + "Z"
    )
    mock_issue.notes.list.return_value = [mock_note, mock_note]
    return mock_issue


def read_mock_issue_templates():
    """Creates mock issue templates (simple and advanced)"""

    issue_templates_gen = issue_template_dir.rglob("*.md")

    simple_temp_path = ".gitlab/issue_templates/pipeline_request_simple.md"
    advanced_tem_path = ".gitlab/issue_templates/pipeline_request_advanced.md"

    issue_templates = {}
    for md_file in issue_templates_gen:
        with open(md_file, "r", encoding="utf-8") as file:
            md_content = file.read()
            if "simple" in md_file.name:
                issue_templates[simple_temp_path] = md_content
            issue_templates[advanced_tem_path] = md_content
    return issue_templates


def read_mock_model_ckp_files():
    """Creates mock model checkpoint files (.dvc)"""
    ckp_path = "model_registry/segmentation"
    mock_ckp_list = []
    for dvc_file in issue_template_dir.rglob("*.dvc"):
        with open(dvc_file, "r", encoding="utf-8") as file:
            dvc_content = file.read()
            mock_ckp_list.append(
                {"name": dvc_file.name, "path": ckp_path+f"/{dvc_file.name}",
                 "content": dvc_content})
    return mock_ckp_list


def mock_gitlab_project():
    """Gitlab project mocker"""
    mock_templates = read_mock_issue_templates()

    mock_project = MagicMock()

    # Store mock issues by iid in a dict
    mock_issues_by_iid = {}
    mock_project_files = {}

    mock_user_list = []
    for iid, (mpath, text) in enumerate(mock_templates.items(), start=100):
        # Create a mock issue dict
        mock_issue = mock_gitlab_issue(iid, text)
        mock_issues_by_iid[iid] = mock_issue

        # Create  a mock template dict for simple & advanced
        mock_file = MagicMock()
        mock_file.decode.return_value = text.encode("utf-8")
        mock_project_files[mpath] = mock_file

        # Create a mock user list
        mock_user_list.append(MagicMock(name=f"username{iid}"))

    # Define a side effect function
    def issue_side_effect(iid):
        return mock_issues_by_iid.get(iid)

    # Add repo_tree content to mock_project_files
    for mock_file in read_mock_model_ckp_files():
        mocker_file = MagicMock()
        mocker_file.decode.return_value = mock_file["content"].encode("utf-8")
        mock_project_files[str(mock_file["path"])] = mocker_file

    def files_side_effect(path, ref):
        return mock_project_files.get(path, ref)

    def repository_tree_side_effect(dir_path):
        if dir_path:
            return read_mock_model_ckp_files()
        return None

    # Set side effect function for mock_project.issues.get
    mock_project.issues.get.side_effect = issue_side_effect

    # Set return value for mock users.list
    mock_project.users.list.return_value = mock_user_list

    # Set return value for mock users.list
    mock_project.files.get.side_effect = files_side_effect

    mock_project.repository_tree.side_effect = repository_tree_side_effect

    return mock_project


@pytest.fixture(autouse=True)
def mock_gitlab_instances(mocker):
    """Fixture to mock get_gitlab_instances function and related classes"""

    mock_gitlab = mocker.patch("gitlab.Gitlab")
    mock_gitlab.return_value.projects.get.return_value = mock_gitlab_project()

    # # Load the .env.test file with override set to True
    load_dotenv(dotenv_path=".env_test", override=True)

    mock_request_repo_instance = RequestRepoAPI(
        os.getenv("MY_REPO_URL"),
        os.getenv("REPO_TOKEN"),
        os.getenv("PROJECT_NUM")
    )
    mock_dvc_repo_instance = DVCRepoAPI(
        os.getenv("DVC_REPO_URL"),
        os.getenv("DVC_REPO_TOKEN"),
        os.getenv("DVC_PROJECT_NUM")
    )

    return mock_request_repo_instance, mock_dvc_repo_instance
