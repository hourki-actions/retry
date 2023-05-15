import os
from main import *

if __name__ == "__main__":
    # collect action inputs & environments
    max_retries = os.environ["INPUT_MAX_RETRIES"]
    repo_token = os.environ["INPUT_TOKEN"]
    runId = os.environ["INPUT_WORKFLOW_RUN_ID"]
    api_url = os.environ["GITHUB_API_URL"]
    repoInputs = fetch_workflow_inputs()
    if os.environ["INPUT_FROM_DISPATCH"] == "false":
        setup(repo_token, repoInputs, api_url, runId)
    else:
        failed_jobs_ids = os.environ["INPUT_FAILED_JOBS_IDS"]
        print(os.environ["INPUT_FAILED_JOBS_IDS"])
        retry_from_dispatched_event(repo_token, runId, failed_jobs_ids, max_retries)
