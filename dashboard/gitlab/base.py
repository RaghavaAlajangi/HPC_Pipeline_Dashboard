from datetime import datetime, timedelta
import re

import gitlab
from gitlab.exceptions import GitlabAuthenticationError


class AuthenticationError(Exception):
    """Authentication Exception"""


class BaseAPI:
    """Gitlab API"""

    def __init__(self, gitlab_url, access_token, project_num):
        self.gitlab_url = gitlab_url
        self.access_token = access_token
        self.project_num = project_num

        try:
            gitlab_obj = gitlab.Gitlab(url=gitlab_url,
                                       private_token=access_token)
            gitlab_obj.auth()
            self.project = gitlab_obj.projects.get(project_num)
        except GitlabAuthenticationError as exc:
            raise AuthenticationError(
                "Authentication error. Your access token may be expired or "
                "incorrect. Please update your access token in your GitLab "
                "settings."
            ) from exc

    @staticmethod
    def human_readable_date(date):
        """Convert gitlab date into human-readable format"""
        # Define the GMT+0200 timezone offset
        gmt_offset = timedelta(hours=2)
        time_stamp = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
        # Add the GMT offset to the timestamp
        new_time_stamp = time_stamp + gmt_offset
        return new_time_stamp.strftime("%I:%M%p, %d-%b-%Y")

    def get_issue_object(self, issue_iid):
        """Return issue object based on issue iid number"""
        return self.project.issues.get(issue_iid)

    def get_project_members(self):
        """Return project members list"""
        all_members = self.project.users.list(all=True)

        # Exclude access tokens from the members list
        filtered_members = [m for m in all_members if m.name != "****"]

        return filtered_members

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

    def repo_listdir(self, repo_dir_path):
        """Return listdir of a given repo directory path"""
        return self.project.repository_tree(repo_dir_path)

    def read_repo_file(self, path):
        """Return file content of a given repo file path"""
        file = self.project.files.get(path, ref="main")
        file_content = file.decode().decode()
        return file_content
