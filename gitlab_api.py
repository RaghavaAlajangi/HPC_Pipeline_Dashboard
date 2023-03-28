import gitlab
import pathlib

secrets_path = pathlib.Path(__file__).parent / "SECRETS.txt"

# with open(secrets_path) as f:
#     lines = f.readlines()
#     url = str(lines[4].strip().split("=")[1])
#     token = str(lines[5].strip().split("=")[1])
#     project_num = str(lines[6].strip().split("=")[1])


with open(secrets_path) as f:
    lines = f.readlines()
    url = str(lines[0].strip().split("=")[1])
    token = str(lines[1].strip().split("=")[1])
    project_num = str(lines[2].strip().split("=")[1])


class GitLabAPI:
    def __init__(self, url, token, project_num):
        self.url = url
        self.token = token
        self.project_num = project_num

        gitlab_obj = gitlab.Gitlab(url=url, private_token=token)
        gitlab_obj.auth()
        self.project = gitlab_obj.projects.get(project_num)

    def get_issues(self, state):
        issues = self.project.issues.list(state=state, get_all=False)
        return issues

    def get_comments(self, issue_iid):
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

    def run_pipeline(self, pipeline_request):
        new_pipeline = self.project.issues.create(pipeline_request)
        return new_pipeline.notes.create({'body': "GO"})


gitlab_api = GitLabAPI(url, token, project_num)
