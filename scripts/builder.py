import urllib3


def build_url(api_url, owner, repo, action_path) -> str:
    return f"{api_url}/repos/{owner}/{repo}/{action_path}"


def build_request(token, url, method):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    return urllib3.request(method, url, headers=headers)
