from datetime import datetime, timedelta
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
        """Fetch comments with dates of an issue"""
        issue = self.project.issues.get(issue_iid)
        issue_notes = issue.notes.list(get_all=True)
        # Define the GMT+0200 timezone offset
        gmt_offset = timedelta(hours=2)

        comments, dates = [], []
        for note in issue_notes:
            time_stamp = datetime.strptime(note.created_at,
                                           "%Y-%m-%dT%H:%M:%S.%fZ")
            # Add the GMT offset to the timestamp
            new_time_stamp = time_stamp + gmt_offset
            formatted_time = new_time_stamp.strftime("%I:%M%p, %d-%b-%Y")
            comments.append(note.body)
            dates.append(formatted_time)
        return {"comments": comments, "dates": dates}

    def get_issue_obj(self, issue_iid):
        """Fetch the issue object based on issue iid"""
        return self.project.issues.get(issue_iid)

    def get_issues_meta(self, state, page):
        """Fetch the metadata of issues in a page"""
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
        """Fetch the members list of a repository"""
        members = self.project.members.list(all=True, include_inherited=True)
        return [member.name for member in members]

    def read_file(self, path):
        """Fetch the file content of a specified repository path"""
        file = self.project.files.get(path, ref="main")
        file_content = file.decode().decode()
        return file_content

    def get_dvc_filelist_from_dir(self, path):
        """Fetch DVC file list from a specified repository path without .dvc
        extension"""
        folder_contents = self.project.repository_tree(path=path)
        return [item["name"].split(".dvc")[0] for item in folder_contents if
                ".dvc" in item["name"]]

    def run_pipeline(self, pipeline_request):
        """Trigger a pipeline by creating `Go` comment in an issue"""
        new_pipeline = self.project.issues.create(pipeline_request)
        return new_pipeline.notes.create({"body": "Go"})

    def cancel_pipeline(self, issue_iid):
        """Stop a pipeline by creating `Close` comment in an issue"""
        issue_obj = self.get_issue_obj(issue_iid)
        issue_obj.notes.create({"body": "Cancel"})
        issue_obj.state_event = "close"
        issue_obj.save()
