import os
from checker import *

if __name__ == "__main__":
    max_retries = os.environ["INPUT_MAX_RETRIES"]
    repo_token = os.environ["INPUT_TOKEN"]
    runId = os.environ["INPUT_WORKFLOW_RUN_ID"]
    api_url = os.environ["GITHUB_API_URL"]
    repoInfo = get_workflow_info()
    test_token = os.environ["TEST_TOKEN"]

    check_workflow_api(repo_token, repoInfo, api_url, runId)
    rerun_all_failed_jobs(runId, api_url, repoInfo, test_token)
