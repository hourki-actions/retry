import os
from main import *

if __name__ == "__main__":
    # collect action inputs & environments
    max_retries = os.environ["INPUT_MAX_RETRIES"]
    repo_token = os.environ["INPUT_TOKEN"]
    runId = os.environ["INPUT_WORKFLOW_RUN_ID"]
    api_url = os.environ["GITHUB_API_URL"]
    repoInfo = fetch_workflow_inputs()
    # main setup script
    setup(repo_token, repoInfo, api_url, runId)
