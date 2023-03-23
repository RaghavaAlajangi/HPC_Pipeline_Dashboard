import gitlab

token = "glpat-oNqAsQX7aHfPJTy3gcHM"
url = "https://gitlab.com/"
project_id = 44043982


class GitLabAPI:
    def __init__(self):
        pass


def get_issues(status="opened"):
    token = "glpat-oNqAsQX7aHfPJTy3gcHM"
    url = "https://gitlab.com/"
    project_id = 44043982

    gl = gitlab.Gitlab(url=url, private_token=token)
    gl.auth()
    project = gl.projects.get(project_id)
    issues = project.issues.list(state=status)
    return issues


def get_issues_metadata(issues):
    issues_meta_data = [i.asdict() for i in issues]
    meta_data = []
    for issue_meta in issues_meta_data:
        title = issue_meta["title"]
        author = issue_meta["author"]["username"]
        web_url = issue_meta["web_url"]
        card = {'name': title, 'author': author, 'web_url': web_url}
        meta_data.append(card)
    return meta_data


def create_gitlab_issue():
    issue_data = {"title": "raghava_test",
                  "description": "this is a test issue created by dash"}

    gl = gitlab.Gitlab(url=url, private_token=token)
    # gl.auth()
    project = gl.projects.get(project_id)
    return project.issues.create(issue_data)
