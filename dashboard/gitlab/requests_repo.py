from datetime import datetime, timedelta
import re

from .base import BaseAPI


class RequestRepoAPI(BaseAPI):
    """HPC Pipeline Request repository API inherited from BaseAPI"""

    @staticmethod
    def human_readable_date(date):
        # Define the GMT+0200 timezone offset
        gmt_offset = timedelta(hours=2)
        time_stamp = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
        # Add the GMT offset to the timestamp
        new_time_stamp = time_stamp + gmt_offset
        return new_time_stamp.strftime("%I:%M%p, %d-%b-%Y")

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
        results_path = "Result path is not found!"
        comments = []
        comment_authors = []
        dates = []
        pipe_state = "run"

        issue_object = self.get_issue_object(issue_iid)
        # Fetch comments of the issue
        issue_notes = issue_object.notes.list(all=True)

        for note in issue_notes:
            # Fetch human-readable date
            time_stamp = self.human_readable_date(note.created_at)
            dates.append(time_stamp)
            auth_name = note.author["name"]
            comment_authors.append("bot" if "*" in auth_name else auth_name)

            if "cancel" in note.body.lower():
                pipe_state = "stop"
            if "state: invalid" in note.body.lower():
                pipe_state = "pause"

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
            "comment_authors": comment_authors,
            "dates": dates,
            "pipe_state": pipe_state
        }

    def get_request_template(self, temp_type):
        """Return either simple or advanced request"""
        templates = {
            "simple": ".gitlab/issue_templates/pipeline_request_simple.md",
            "advanced": ".gitlab/issue_templates/pipeline_request_advanced.md"
        }
        return self.read_repo_file(templates[temp_type])

    def parse_description(self, issue_text):
        """Parse username and type of issue from description"""
        lower_text = issue_text.lower()
        data = {
            "type": "advanced" if "advanced" in lower_text else "simple",
            "username": None
        }

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

    def run_pipeline(self, pipeline_request):
        """Trigger pipeline by creating `Go` comment in an issue"""
        new_pipeline = self.project.issues.create(pipeline_request)
        return new_pipeline.notes.create({"body": "Go"})

    def change_pipeline_status(self, issue_iid, action):
        """Stops or pause the given pipeline by writing `cancel` and `invalid`
        comments"""
        issue_obj = self.get_issue_object(issue_iid)

        comments = issue_obj.notes.list(get_all=True)
        if action == "pause":
            if not any("state: invalid" in c.body.lower() for c in comments):
                issue_obj.notes.create({"body": "STATE: invalid"})
        elif action == "run":
            # Remove any existing "pause" comment
            for comment in comments:
                if "state: invalid" in comment.body.lower():
                    comment.delete()
        elif action == "stop":
            if not any("cancel" in c.body.lower() for c in comments):
                issue_obj.notes.create({"body": "Cancel"})
        else:
            print("unknown action!")
