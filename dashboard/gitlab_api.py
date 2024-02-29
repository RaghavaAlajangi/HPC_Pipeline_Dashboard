from datetime import datetime, timedelta
import math
import re
import yaml
from collections import defaultdict

import gitlab
from gitlab.exceptions import GitlabAuthenticationError


class AuthenticationError(Exception):
    pass


class GitLabAPI:
    def __init__(self, url, token, project_num):
        self.url = url
        self.token = token
        self.project_num = project_num

        try:
            gitlab_obj = gitlab.Gitlab(url=url, private_token=token)
            gitlab_obj.auth()
            self.project = gitlab_obj.projects.get(project_num)
            self.issues_per_page = 20
        except GitlabAuthenticationError:
            raise AuthenticationError(
                "Authentication error. Your access token may be expired or "
                "incorrect. Please update your access token in your GitLab "
                "settings."
            )

    def get_issues_per_page(self, state, page):
        """Fetch issues list per page in a state"""
        return self.project.issues.list(state=state, page=page, get_all=False,
                                        per_page=self.issues_per_page)

    @staticmethod
    def get_issue_type(issue_text):
        if "advanced" in issue_text.lower():
            return "Advanced", "danger"
        else:
            return "Simple", "success"

    @staticmethod
    def human_readable_date(date):
        # Define the GMT+0200 timezone offset
        gmt_offset = timedelta(hours=2)
        time_stamp = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
        # Add the GMT offset to the timestamp
        new_time_stamp = time_stamp + gmt_offset
        return new_time_stamp.strftime("%I:%M%p, %d-%b-%Y")

    def get_num_pages(self, state):
        """Compute the total number of issue pages in a state"""
        num_issues = len(self.project.issues.list(state=state, get_all=True))
        return math.ceil(num_issues / self.issues_per_page)

    def get_comments(self, issue_iid):
        """Fetch comments with dates of an issue"""
        issue = self.project.issues.get(issue_iid)

        # Fetch comments of the issue
        issue_notes = issue.notes.list(all=True)

        # Compile regex pattern
        pattern = re.compile(r"```python.*?```", flags=re.DOTALL)

        comments = []
        dates = []

        for note in issue_notes:
            time_stamp = self.human_readable_date(note.created_at)

            # Filter python error messages from comments
            if "```python" in note.body:
                note_wo_code = pattern.sub(
                    f"Got some error! See the comment: "
                    f"{issue.web_url}#note_{note.id}",
                    note.body
                )
                comments.append(note_wo_code)
            else:
                comments.append(note.body)

            dates.append(time_stamp)

        return {"comments": comments, "dates": dates}

    def get_issue_obj(self, issue_iid):
        """Fetch the issue object based on issue iid"""
        return self.project.issues.get(issue_iid)

    def get_issues_meta(self, state, page):
        """Fetch the metadata of issues in a page"""
        issues = self.get_issues_per_page(state, page)
        return [
            {
                "title": issue.title,
                "id": issue.id,
                "iid": issue.iid,
                "author": issue.author["name"],
                "user": self.find_user(issue.description) or issue.author[
                    "name"],
                "web_url": issue.web_url,
                "date": self.human_readable_date(issue.created_at),
                "type": self.get_issue_type(issue.description)
            }
            for issue in issues
        ]

    def get_project_members(self):
        """Fetch the members list of a repository"""
        return self.project.members_all.list(get_all=True)

    def find_user(self, issue_text, pattern="username"):
        """Look for `username` section in the issue description"""
        members = self.get_project_members()
        username = None
        name = None
        for line in reversed(issue_text.split('\n')):
            if f"[x] {pattern}" in line:
                username = line.split("=")[1].strip()
                break

        if username:
            for member in members:
                if username == member.username:
                    name = member.name
                    break
        return name

    def read_file(self, path):
        """Fetch the file content of a specified repository path"""
        file = self.project.files.get(path, ref="main")
        file_content = file.decode().decode()
        return file_content

    def get_dvc_files(self, path):
        """Fetch DVC file list from a specified repository path without .dvc
        extension"""
        folder_contents = self.project.repository_tree(path=path)
        return [item["name"].split(".dvc")[0] for item in folder_contents if
                ".dvc" in item["name"]]

    def fetch_model_meta(self):
        repo_folder_path = "model_registry/segmentation"
        folder_content = self.project.repository_tree(repo_folder_path)
        model_meta = defaultdict(dict)

        for file in folder_content:
            if ".dvc" in file["name"]:
                str_data = self.read_file(file["path"])
                # Convert file content string into dictionary
                dict_data = yaml.safe_load(str_data)
                if not dict_data["meta"]["archive"]:
                    device = dict_data["meta"]["device"]
                    ftype = dict_data["meta"]["type"]
                    path = dict_data["outs"][0]["path"]
                    model_meta[device][ftype] = path

        # Extract device and type lists from model_meta
        device_list = list(model_meta.keys())
        type_list = list(
            {ty for types in model_meta.values() for ty in types.keys()})

        result = (device_list, type_list, model_meta)

        return result

    def run_pipeline(self, pipeline_request):
        """Trigger a pipeline by creating `Go` comment in an issue"""
        new_pipeline = self.project.issues.create(pipeline_request)
        return new_pipeline.notes.create({"body": "Go"})

    def cancel_pipeline(self, issue_iid):
        """Stop a pipeline by creating `Close` comment in an issue"""
        issue_obj = self.get_issue_obj(issue_iid)
        issue_obj.notes.create({"body": "Cancel"})
        issue_obj.save()
