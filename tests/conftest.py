import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from dotenv import load_dotenv

from dashboard.gitlab import DVCRepoAPI, RequestRepoAPI

issue_template_dir = Path(__file__).parents[0] / "data"


def mock_comment(comment_text):
    """Creates a mock issue comment."""
    return MagicMock(
        body=comment_text,
        created_at=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    )


def mock_gitlab_issue(iid, state, description, comment_list):
    """Creates a mock GitLab issue."""
    mock_issue = MagicMock(
        id=f"123{iid}",
        iid=iid,
        state=state,
        title=f"Mock Test Issue {iid}",
        author={"name": f"mock_author_{iid}"},
        web_url=f"https://mock_issue_url{iid}",
        description=description,
        created_at=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    )
    mock_issue.notes.list.return_value = [
        mock_comment(msg) for msg in comment_list
    ]
    return mock_issue


def read_mock_issue_templates():
    """Reads mock issue templates (simple and advanced)."""
    issue_templates = {}
    for md_file in issue_template_dir.rglob("*.md"):
        with open(md_file, "r", encoding="utf-8") as file:
            md_content = file.read()
            if "simple" in md_file.name:
                issue_templates[
                    ".gitlab/issue_templates/pipeline_request_simple.md"
                ] = md_content
            else:
                issue_templates[
                    ".gitlab/issue_templates/pipeline_request_advanced.md"
                ] = md_content
    return issue_templates


def read_mock_model_ckp_files():
    """Reads mock model checkpoint files (.dvc)."""
    ckp_path = "model_registry/segmentation"
    return [
        {
            "name": dvc_file.name,
            "path": f"{ckp_path}/{dvc_file.name}",
            "content": dvc_file.read_text(encoding="utf-8"),
        }
        for dvc_file in issue_template_dir.rglob("*.dvc")
    ]


def read_mock_dcevent_defaults():
    """Reads mock dcevent default params file (.yaml)."""
    param_path = "dashboard_dcevent_defaults.yaml"
    local_param_path = issue_template_dir / param_path
    return {
        "path": param_path,
        "content": local_param_path.read_text(encoding="utf-8"),
    }


def mock_gitlab_project():
    """Creates a mock GitLab project with issues, users, and repository
    content."""

    # Read mock data
    issue_templates = read_mock_issue_templates()
    model_ckp_files = read_mock_model_ckp_files()
    dcevent_defaults = read_mock_dcevent_defaults()

    mock_project = MagicMock()
    mock_issues_by_iid = {}
    mock_project_files = {}
    mock_user_list = []

    # Define mock issues
    issue_definitions = [
        (
            1,
            "opened",
            issue_templates[
                ".gitlab/issue_templates/pipeline_request_simple.md"
            ],
            ["mock comment1", "mock comment2"],
        ),
        (
            2,
            "opened",
            issue_templates[
                ".gitlab/issue_templates/pipeline_request_advanced.md"
            ],
            [
                "Completed job 1",
                "Completed job 2",
                "We have 2 pipelines",
                "STATE: queued",
                "STATE: setup",
            ],
        ),
        (
            3,
            "opened",
            issue_templates[
                ".gitlab/issue_templates/pipeline_request_advanced.md"
            ],
            ["STATE: invalid", "test", "Go"],
        ),
        (
            4,
            "opened",
            issue_templates[
                ".gitlab/issue_templates/pipeline_request_advanced.md"
            ],
            ["test", "Go"],
        ),
        (
            5,
            "opened",
            issue_templates[
                ".gitlab/issue_templates/pipeline_request_advanced.md"
            ],
            ["STATE: error", "Go"],
        ),
        (
            6,
            "closed",
            issue_templates[
                ".gitlab/issue_templates/pipeline_request_advanced.md"
            ],
            ["STATE: error", "Go"],
        ),
    ]

    for iid, state, description, comments in issue_definitions:
        mock_issues_by_iid[iid] = mock_gitlab_issue(
            iid, state, description, comments
        )
        mock_user_list.append(MagicMock(name=f"username{iid}"))

    # Define issue retrieval functions
    def issue_side_effect(iid):
        return mock_issues_by_iid.get(iid)

    def issue_list_side_effect_by_state(
        state=None, per_page=1, search=None, get_all=True, page=1
    ):
        return [
            issue
            for issue in mock_issues_by_iid.values()
            if issue.state == (state or "closed")
        ]

    # Store project files
    for path, text in issue_templates.items():
        mock_file = MagicMock()
        mock_file.decode.return_value = text.encode("utf-8")
        mock_project_files[path] = mock_file

    for file_data in model_ckp_files:
        mock_file = MagicMock()
        mock_file.decode.return_value = file_data["content"].encode("utf-8")
        mock_project_files[file_data["path"]] = mock_file

    mock_file = MagicMock()
    mock_file.decode.return_value = dcevent_defaults["content"].encode("utf-8")
    mock_project_files[dcevent_defaults["path"]] = mock_file

    # Define file retrieval functions
    def files_side_effect(path, ref):
        return mock_project_files.get(path, ref)

    def repository_tree_side_effect(dir_path):
        return model_ckp_files if dir_path else None

    # Assign side effects
    mock_project.issues.get.side_effect = issue_side_effect
    mock_project.issues.list.side_effect = issue_list_side_effect_by_state
    mock_project.users.list.return_value = mock_user_list
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
        os.getenv("PROJECT_NUM"),
    )
    mock_dvc_repo_instance = DVCRepoAPI(
        os.getenv("DVC_REPO_URL"),
        os.getenv("DVC_REPO_TOKEN"),
        os.getenv("DVC_PROJECT_NUM"),
    )

    return mock_request_repo_instance, mock_dvc_repo_instance
