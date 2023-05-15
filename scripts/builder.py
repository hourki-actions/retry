import urllib3


def build_url(api_url, owner, repo, action_path) -> str:
    return f"{api_url}/repos/{owner}/{repo}/{action_path}"


def build_request(token, url, method, payload=None):
    headers = {
        'Authorization': 'Bearer {}'.format(token)
    }
    if payload is None:
        return urllib3.request(method, url, headers=headers)
    else:
        return urllib3.request(method, url, headers=headers, body=payload)
