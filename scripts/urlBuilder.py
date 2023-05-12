def build_url(api_url, owner, repo, action_path) -> str:
    return f"{api_url}/repos/{owner}/{repo}/{action_path}"
