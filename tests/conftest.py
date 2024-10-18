from datetime import datetime, timezone
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from dotenv import load_dotenv

from dashboard.gitlab import DVCRepoAPI, RequestRepoAPI

issue_template_dir = Path(__file__).parents[0] / "data"


def mock_comment(comment_text):
    """Creates a mock issue comment"""
    return MagicMock(
        body=comment_text,
        created_at=datetime.utcnow().isoformat() + "Z"
    )


def mock_gitlab_issue(iid, state, description, comment_list):
    """Creates a mock gitlab issue"""
    mock_issue = MagicMock(
        id=f"123{iid}",
        iid=iid,
        state=state,
        title=f"Mock Test Issue {iid}",
        author={"name": f"mock_author_{iid}"},
        web_url=f"https://mock_issue_url{iid}",
        description=description,
        created_at=datetime.now(timezone.utc),
    )
    mock_issue.notes.list.return_value = [mock_comment(msg) for msg in
                                          comment_list]
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
                {"name": dvc_file.name, "path": ckp_path + f"/{dvc_file.name}",
                 "content": dvc_content})
    return mock_ckp_list


def read_mock_dcevent_defaults():
    """Creates mock dcevent default params file (.yaml)"""
    param_path = "dashboard_dcevent_defaults.yaml"
    local_param_path = issue_template_dir / param_path
    with open(local_param_path, "r", encoding="utf-8") as file:
        param_content = file.read()
    return {"path": param_path, "content": param_content}


def mock_gitlab_project():
    """Gitlab project mocker"""
    mock_templates = read_mock_issue_templates()

    adv_txt, sim_txt = mock_templates.values()

    mock_project = MagicMock()

    # Store mock issues by iid in a dict
    mock_issues_by_iid = {}
    mock_project_files = {}

    mock_user_list = []

    # Simple mock issue
    mk_iid1 = 1
    mock_issues_by_iid[mk_iid1] = mock_gitlab_issue(
        mk_iid1, "opened", sim_txt, ["mock comment1", "mock comment2"])
    mock_user_list.append(MagicMock(name=f"username{mk_iid1}"))

    # Advanced mock issue
    mk_iid2 = 2
    mock_issues_by_iid[mk_iid2] = mock_gitlab_issue(
        mk_iid2, "opened", adv_txt, ["Completed job 1", "Completed job 2",
                                     "We have 2 pipelines", "STATE: queued",
                                     "STATE: setup"])
    mock_user_list.append(MagicMock(name=f"username{mk_iid2}"))

    # This mock issue helps to test pausing pipeline
    mk_iid3 = 3
    mock_issues_by_iid[mk_iid3] = mock_gitlab_issue(
        mk_iid3, "opened", adv_txt, ["STATE: invalid", "test", "Go"])
    mock_user_list.append(MagicMock(name=f"username{mk_iid3}"))

    # This mock issue helps to test resume pipeline
    mk_iid3 = 4
    mock_issues_by_iid[mk_iid3] = mock_gitlab_issue(
        mk_iid3, "opened", adv_txt, ["test", "Go"])
    mock_user_list.append(MagicMock(name=f"username{mk_iid3}"))

    # This mock issue helps to pagination of closed pipelines
    mk_iid3 = 5
    mock_issues_by_iid[mk_iid3] = mock_gitlab_issue(
        mk_iid3, "opened", adv_txt, ["STATE: error", "Go"])
    mock_user_list.append(MagicMock(name=f"username{mk_iid3}"))

    # This mock issue helps to test disable run/resume button when there is
    # an error in the pipeline
    mk_iid3 = 6
    mock_issues_by_iid[mk_iid3] = mock_gitlab_issue(
        mk_iid3, "closed", adv_txt, ["STATE: error", "Go"])
    mock_user_list.append(MagicMock(name=f"username{mk_iid3}"))

    # Define a side effect that allow us to fetch an issue based on iid
    def issue_side_effect(iid):
        return mock_issues_by_iid.get(iid)

    def issue_list_side_effect_by_state(state=None, per_page=1, search=None,
                                        get_all=True):
        if not state:
            return [ii for ii in mock_issues_by_iid.values() if
                    ii.state == "closed"]
        return [ii for ii in mock_issues_by_iid.values() if ii.state == state]

    # Add mock templates simple & advanced as project files
    for mpath, text in mock_templates.items():
        mock_file = MagicMock()
        mock_file.decode.return_value = text.encode("utf-8")
        mock_project_files[mpath] = mock_file

    # Add repo_tree content to mock_project_files
    for mock_file in read_mock_model_ckp_files():
        mocker_file = MagicMock()
        mocker_file.decode.return_value = mock_file["content"].encode("utf-8")
        mock_project_files[str(mock_file["path"])] = mocker_file

    # Add mock dcevent default params to mock project
    defaults = read_mock_dcevent_defaults()
    mocker_default = MagicMock()
    mocker_default.decode.return_value = defaults["content"].encode("utf-8")
    mock_project_files[str(defaults["path"])] = mocker_default

    def files_side_effect(path, ref):
        return mock_project_files.get(path, ref)

    def repository_tree_side_effect(dir_path):
        if dir_path:
            return read_mock_model_ckp_files()
        return None

    # Set side effect function for mock_project.issues.get
    mock_project.issues.get.side_effect = issue_side_effect

    # Set side effect function for issues.list (for opened & closed states)
    mock_project.issues.list.side_effect = issue_list_side_effect_by_state

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
