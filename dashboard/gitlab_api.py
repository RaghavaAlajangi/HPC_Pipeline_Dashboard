import math

import gitlab


class GitLabAPI:
    def __init__(self, url, token, project_num):
        self.url = url
        self.token = token
        self.project_num = project_num

        gitlab_obj = gitlab.Gitlab(url=url, private_token=token)
        gitlab_obj.auth()
        self.project = gitlab_obj.projects.get(project_num)
        self.issues_per_page = 20

    def get_issues_per_page(self, state, page):
        """Fetch issues list per page in a state"""
        return self.project.issues.list(state=state, page=page, get_all=False,
                                        per_page=self.issues_per_page)

    def get_num_pages(self, state):
        """Compute the total number of issue pages in a state"""
        num_issues = len(self.project.issues.list(state=state, get_all=True))
        return math.ceil(num_issues / self.issues_per_page)

    def get_comments(self, issue_iid):
        """Fetch comments of an issues"""
        issue = self.project.issues.get(issue_iid)
        issue_notes = issue.notes.list(get_all=True)
        return [n.asdict()["body"] for n in issue_notes]

    def get_issue_obj(self, issue_iid):
        return self.project.issues.get(issue_iid)

    def get_issues_meta(self, state, page):
        issues = self.get_issues_per_page(state, page)
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
        simple_template = self.project.files.get(simple_path, ref="main")
        simple_template = simple_template.decode().decode()
        return simple_template

    def get_advanced_template(self):
        advanced_path = ".gitlab/issue_templates/pipeline_request_advanced.md"
        advanced_template = self.project.files.get(advanced_path, ref="main")
        advanced_template = advanced_template.decode().decode()
        return advanced_template

    def run_pipeline(self, pipeline_request):
        new_pipeline = self.project.issues.create(pipeline_request)
        return new_pipeline.notes.create({"body": "Go"})
