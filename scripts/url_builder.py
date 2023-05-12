def build_url(api_url, owner, repo, run_id) -> str:
    return f"{api_url}/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
