import functools
import os
import gitlab
# import pathlib

# secrets_path = pathlib.Path(__file__).parents[1] / "SECRETS.txt"
#
# with open(secrets_path) as f:
#     lines = f.readlines()
#     repo_url = str(lines[0].strip().split("=")[1])
#     repo_token = str(lines[1].strip().split("=")[1])
#     project_num = str(lines[2].strip().split("=")[1])

repo_url = os.getenv("REPO_URL")
repo_token = os.getenv("REPO_TOKEN")
project_num = os.getenv("PROJECT_NUM")


class GitLabAPI:
    def __init__(self, url, token, project_num):
        self.url = url
        self.token = token
        self.project_num = project_num

        gitlab_obj = gitlab.Gitlab(url=url, private_token=token)
        gitlab_obj.auth()
        self.project = gitlab_obj.projects.get(project_num)

    @functools.lru_cache(maxsize=500, typed=True)
    def get_issues(self, state):
        """
        It takes a state as an argument and returns all issues in that state.
        The function uses the project's list method to get all issues in the
        given state, but only gets the first page of results (get_all=False).
        This is because we don't want to make too many requests at once.
        """
        issues = self.project.issues.list(state=state, get_all=True)
        return issues

    def get_comments(self, issue_iid):
        """
        It takes an issue_iid as input and returns a list of comments
        associated with that issue.
        """
        issue = self.project.issues.get(issue_iid)
        issue_notes = issue.notes.list(get_all=True)
        return [n.asdict()["body"] for n in issue_notes]

    def get_issue_obj(self, issue_iid):
        return self.project.issues.get(issue_iid)

    def get_issues_meta(self, state):
        issues = self.get_issues(state)
        meta_data = []
        for issue in issues:
            issue_meta = issue.asdict()
            required_meta = {
                "name": issue_meta["title"],
                "id": issue_meta["id"],
                "iid": issue_meta["iid"],
                "author": issue_meta["author"]["username"],
                "web_url": issue_meta["web_url"]
            }
            meta_data.append(required_meta)
        return meta_data

    def get_simple_template(self):
        simple_path = ".gitlab/issue_templates/pipeline_request_simple.md"
        simple_template = self.project.files.get(simple_path, ref='main')
        simple_template = simple_template.decode().decode()
        return simple_template

    def get_advanced_template(self):
        advanced_path = ".gitlab/issue_templates/pipeline_request_advanced.md"
        advanced_template = self.project.files.get(advanced_path, ref='main')
        advanced_template = advanced_template.decode().decode()
        return advanced_template

    def run_pipeline(self, pipeline_request):
        new_pipeline = self.project.issues.create(pipeline_request)
        return new_pipeline.notes.create({"body": "GO"})


def get_gitlab_obj():
    """Creates and returns a GitLabAPI object"""
    return GitLabAPI(repo_url, repo_token, project_num)
