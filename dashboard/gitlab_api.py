from datetime import datetime, timedelta
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

    @staticmethod
    def human_readable_date(date):
        # Define the GMT+0200 timezone offset
        gmt_offset = timedelta(hours=2)
        time_stamp = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
        # Add the GMT offset to the timestamp
        new_time_stamp = time_stamp + gmt_offset
        return new_time_stamp.strftime("%I:%M%p, %d-%b-%Y")

    def get_issue_obj(self, issue_iid):
        """Fetch the issue object based on issue iid"""
        return self.project.issues.get(issue_iid)

    def total_issues(self, state):
        return len(self.project.issues.list(state=state, get_all=True))

    def get_processed_issue_notes(self, issue_iid):
        """Fetch comments with dates of an issue and parse issue comments
        for specific information"""

        job_comments = [
            re.compile(r"^Completed job"),
            re.compile(r"^We have (\d+) pipeline"),
            re.compile(r"Access all your experiments at:\s*(https?://\S+)")
        ]

        # Initialize variables
        total_jobs = 0
        finished_jobs = 0
        results_path = "No result path"
        comments = []
        dates = []
        is_canceled = False

        issue_object = self.get_issue_obj(issue_iid)
        # Fetch comments of the issue
        issue_notes = issue_object.notes.list(all=True)

        for note in issue_notes:
            # Fetch human-readable date
            time_stamp = self.human_readable_date(note.created_at)
            dates.append(time_stamp)

            # Filter python error messages from comments
            if "```python" in note.body:
                note_without_code = re.sub(
                    r"```python.*?```",
                    f"Got some error! See the comment: "
                    f"{issue_object.web_url}#note_{note.id}",
                    note.body,
                    flags=re.DOTALL
                )
                comments.append(note_without_code)
            elif note.body.lower() == "cancel":
                is_canceled = True

            else:
                comments.append(note.body)

            # Parse comments for specific information
            # Check for total number of pipelines
            total_match = job_comments[1].match(note.body)
            if total_match:
                total_jobs = int(total_match.group(1))

            # Check for completed job
            if job_comments[0].match(note.body):
                finished_jobs += 1

            # Check for results path
            results_match = job_comments[2].search(note.body)
            if results_match:
                results_path = f"P:/{results_match.group(1).split('main/')[1]}"

        if total_jobs == 0:
            pass

        return {
            "total_jobs": total_jobs,
            "finished_jobs": finished_jobs,
            "results_path": results_path,
            "comments": comments,
            "dates": dates,
            "is_canceled": is_canceled
        }

    def parse_description(self, issue_text):
        lower_text = issue_text.lower()
        data = {"type": "simple" if "simple" in lower_text else "advanced"}

        # Search for the username in reverse order
        for line in reversed(lower_text.split("\n")):
            if "[x] username" in line:
                name = line.split("=")[1].strip()
                break
        else:
            # Username not found, return immediately
            return data

        members = self.get_project_members()

        # Search for the matching username in project members
        for member in members:
            if name == member.username:
                data["username"] = member.name
                break

        return data

    def get_issues_meta(self, state, page, per_page=10, search_term=None):
        """Filter issues based on the state and search term if it exists and
        returns a list of dictionaries containing information about each issue.

        Parameters
        ----------
            state: str
                Filter issues by state
            page: int
                Get the page number of issues to be displayed
            per_page: int
                Set the number of issues to be displayed per page
            search_term: str
                Search for issues that match the term

        Returns
        -------
            A list of dictionaries
        """
        filter_params = {"state": state, "per_page": per_page}

        if search_term:
            filter_params.update({"search": search_term, "get_all": True})
        else:
            filter_params.update({"page": page, "per_page": per_page})

        issues = self.project.issues.list(**filter_params)

        issues_meta = []
        for issue in issues:
            parsed_description = self.parse_description(issue.description)
            issue_meta = {
                "title": issue.title,
                "id": issue.id,
                "iid": issue.iid,
                "author": issue.author["name"],
                "user": parsed_description["username"] or issue.author["name"],
                "web_url": issue.web_url,
                "date": self.human_readable_date(issue.created_at),
                "type": parsed_description["type"]
            }
            issues_meta.append(issue_meta)
        return issues_meta

    def get_project_members(self):
        """Fetch the members list of a repository"""
        return self.project.members_all.list(get_all=True)

    def read_file(self, path):
        """Fetch the file content of a specified repository path"""
        file = self.project.files.get(path, ref="main")
        file_content = file.decode().decode()
        return file_content

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
