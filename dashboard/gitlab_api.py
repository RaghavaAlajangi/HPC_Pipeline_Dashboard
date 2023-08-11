import os

import gitlab


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

    def get_issues(self, state):
        """
        It takes a state as an argument and returns all issues in that state.
        The function uses the project's list method to get all issues in the
        given state, but only gets the first page of results (get_all=False).
        This is because we don't want to make too many requests at once.
        """
        issues = self.project.issues.list(state=state, get_all=False)
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
        return [
            {
                "name": issue.title,
                "id": issue.id,
                "iid": issue.iid,
                "author": issue.author["username"],
                "web_url": issue.web_url,
            }
            for issue in issues
        ]

    def get_project_members(self):
        members = self.project.members.list(all=True, include_inherited=True)
        return [member.name for member in members]

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
