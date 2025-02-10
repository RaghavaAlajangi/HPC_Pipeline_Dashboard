import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import yaml

from .base import BaseAPI


class RequestRepoAPI(BaseAPI):
    """HPC Pipeline Request repository API inherited from BaseAPI"""

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
            filter_params.update({"search": search_term, "page": page})
        else:
            filter_params.update({"page": page, "per_page": per_page})

        issues = self.project.issues.list(**filter_params)

        issues_meta = []
        with ThreadPoolExecutor() as executor:
            future_to_issue = {
                executor.submit(self.process_issue, ii): ii for ii in issues
            }
            for future in as_completed(future_to_issue):
                try:
                    result = future.result()
                    issues_meta.append(result)
                except Exception as exc:
                    issue = future_to_issue[future]
                    print(f"Issue {issue.iid} generated an exception: {exc}")

        issues_meta = sorted(issues_meta, key=lambda x: x["id"], reverse=True)
        return issues_meta

    def process_issue(self, issue):
        parsed_description = self.parse_description(issue.iid)
        if issue.state == "opened":
            comments = self.get_processed_issue_notes(issue.iid)
            pipe_state = comments["pipe_state"]
        else:
            # Define state for all closed pipelines
            pipe_state = "finish"
        return {
            "title": issue.title,
            "id": issue.id,
            "iid": issue.iid,
            "author": issue.author["name"],
            "user": parsed_description["username"] or issue.author["name"],
            "web_url": issue.web_url,
            "date": self.human_readable_date(issue.created_at),
            "type": parsed_description["type"],
            "pipe_state": pipe_state,
            "s3_results_flag": parsed_description["s3_results_flag"],
            "s3_raw_data_flag": parsed_description["s3_raw_data_flag"],
        }

    def get_processed_issue_notes(self, issue_iid):
        """Fetch comments with dates of an issue and parse issue comments
        for specific information"""

        job_comments = [
            re.compile(r"^Completed job"),
            re.compile(r"^We have (\d+) pipeline"),
            re.compile(r"about this particular job at:\s*(https?://\S+)"),
        ]

        issue_object = self.get_issue_object(issue_iid)
        issue_notes = issue_object.notes.list(all=True)

        data = {
            "total_jobs": 0,
            "finished_jobs": 0,
            "results_path": "Result path is not found!",
            "comments": [],
            "comment_authors": [],
            "dates": [],
            "pipe_state": "run",
        }

        for note in issue_notes:
            note_body_lower = note.body.lower()
            time_stamp = self.human_readable_date(note.created_at)
            auth_name = note.author["name"]

            data["dates"].append(time_stamp)
            data["comment_authors"].append(
                "bot" if "*" in auth_name else auth_name
            )
            # Check for pipeline state
            if "cancel" in note_body_lower:
                data["pipe_state"] = "cancel"
            # "cancel" is prioritized over "error"
            elif (
                "state: error" in note_body_lower
                and data["pipe_state"] != "cancel"
            ):
                data["pipe_state"] = "error"
            # "cancel" and "error" are prioritized over "invalid"
            elif "state: invalid" in note_body_lower and data[
                "pipe_state"
            ] not in [
                "cancel",
                "error",
            ]:
                data["pipe_state"] = "pause"
            # "cancel" "error", and "invalid" are prioritized over "done"
            elif "state: done" in note_body_lower and data[
                "pipe_state"
            ] not in [
                "cancel",
                "error",
                "pause",
            ]:
                data["pipe_state"] = "finish"

            # Filter python error messages from comments
            if "```python" in note_body_lower:
                note_without_code = re.sub(
                    r"```python.*?```",
                    f"Got some error! See the comment: "
                    f"{issue_object.web_url}#note_{note.id}",
                    note.body,
                    flags=re.DOTALL,
                )
                data["comments"].append(note_without_code)
            elif "changed the description" in note_body_lower:
                continue
            elif "marked the checklist" in note_body_lower:
                continue
            else:
                data["comments"].append(note.body)

            # Check for completed job
            if job_comments[0].match(note.body):
                data["finished_jobs"] += 1

            # Parse comments for specific information
            # Check for total number of pipelines
            total_match = job_comments[1].match(note.body)
            if total_match:
                data["total_jobs"] = int(total_match.group(1))
            # Check for results path
            results_match = job_comments[2].search(note.body)
            if results_match:
                data["results_path"] = (
                    f"P:/{results_match.group(1).split('main/')[1]}"
                )

        return data

    def get_request_template(self, temp_type):
        """Return either simple or advanced request"""
        templates = {
            "simple": ".gitlab/issue_templates/pipeline_request_simple.md",
            "advanced": ".gitlab/issue_templates/pipeline_request_advanced.md",
        }
        # Note: 1 is added to the latest issue iid and added to the issue
        # description. As a result, users will be able to search for the
        # specific issue on the dashboard via the search bar.
        issue_titles = {
            "simple": "# Pipeline Request",
            "advanced": "# Pipeline Request ADVANCED",
        }
        latest_issue_iid = self.get_latest_issue_iid()
        issue_template = self.read_repo_file(templates[temp_type])
        title_idx = issue_template.find(issue_titles[temp_type])

        # Split the string at the position of the specific word
        first_part = issue_template[: title_idx + len(issue_titles[temp_type])]
        second_part = issue_template[
            title_idx + len(issue_titles[temp_type]):
        ]
        # Add new iid to the issue description
        return first_part + f"\n#{latest_issue_iid + 1}" + second_part

    def parse_description(self, issue_iid):
        """Parse username, type of issue, and whether to remove from the issue
        description"""
        issue_object = self.get_issue_object(issue_iid)
        lower_text = issue_object.description.lower()
        data = {
            "type": "advanced" if "advanced" in lower_text else "simple",
            "username": None,
            "s3_results_flag": False,
            "s3_raw_data_flag": False,
            "has_hsm_data": False,
        }

        if "[x] keep_results" in lower_text:
            data["s3_results_flag"] = "keep results"

        if "[x] keep_raw_data" in lower_text:
            data["s3_raw_data_flag"] = "keep raw data"

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
                    break
        elif action == "cancel":
            if not any("cancel" in c.body.lower() for c in comments):
                issue_obj.notes.create({"body": "Cancel"})
        else:
            print("unknown action!")

    def get_latest_issue_iid(self):
        """Get the latest issue iid"""
        latest_issue = self.project.issues.list(per_page=1, get_all=False)[0]
        return latest_issue.iid

    def total_issues(self, state, filter_params=None):
        """Return total issues in a state or based on filter_params"""
        # NOTE: Retrieve all the issues via the API is an expensive operation,
        # so we only retrieve the total number of issues from the latest issue
        # and subtract the number of issues in the opened state to get the
        # total number of issues in the closed state.
        open_len = len(self.project.issues.list(state="opened", get_all=True))
        if state == "opened" and not filter_params:
            return open_len
        elif state == "closed" and not filter_params:
            total_issues = self.get_latest_issue_iid()
            return total_issues - open_len
        else:
            filter_params.update({"state": state})
            # Retrieve total number of issues based on filter_params
            return len(self.project.issues.list(**filter_params))

    def change_s3_flag(self, issue_iid, flag_name):
        """Change the s3 flag (results or raw data) in an issue"""
        issue_obj = self.get_issue_object(issue_iid)
        desc = issue_obj.description
        flag_checked = f"[x] {flag_name}"
        flag_unchecked = f"[ ] {flag_name}"

        if flag_checked in desc:
            desc = desc.replace(flag_checked, flag_unchecked)
        elif flag_unchecked in desc:
            desc = desc.replace(flag_unchecked, flag_checked)
        else:
            desc += f"\n- __S3_{flag_name}_flag__\n   - {flag_checked}"

        issue_obj.description = desc
        issue_obj.save()

    def get_defaults(self):
        defaults_path = "dashboard_dcevent_defaults.yaml"
        default_str = self.read_repo_file(defaults_path)
        return yaml.safe_load(default_str)
