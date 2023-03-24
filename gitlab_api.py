import gitlab


class GitLabAPI:
    def __init__(self, url="https://gitlab.gwdg.de",
                 project_num=28692, token=None):
        self.url = url
        self.project_num = project_num
        self.token = token

        gitlab_obj = gitlab.Gitlab(url=url, private_token=token)
        gitlab_obj.auth()
        self.project = gitlab_obj.projects.get(project_num)

    def get_issues(self, state):
        issues = self.project.issues.list(state=state, get_all=False)
        return issues

    def get_issues_meta(self, state):
        issues = self.get_issues(state)
        meta_data = []
        for issue in issues:
            # issue_notes = issue.notes.list(get_all=True)
            # comments = [n.asdict()["body"] for n in issue_notes]
            issue_meta = issue.asdict()
            title = issue_meta["title"]
            author = issue_meta["author"]["username"]
            web_url = issue_meta["web_url"]
            meta_req = {"name": title, "author": author,
                        "web_url": web_url,
                        # "comments": comments
                        }
            meta_data.append(meta_req)
        return meta_data

    def create_issue(self, issue_dict):
        # issue_data = {"title": "raghava_test",
        #               "description": "this is a test issue created by dash"}
        return self.project.issues.create(issue_dict)
