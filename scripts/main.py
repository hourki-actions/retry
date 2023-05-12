import json
import os
import urllib3
from dataclasses import dataclass

from extract import *
from retry import *


@dataclass
class RepoInfo:
    owner: str
    repo: str


logger = Logger('Retry.check')


def fetch_workflow_inputs() -> RepoInfo:
    json_data = json.load(open(os.environ['GITHUB_EVENT_PATH']))
    owner = json_data['repository']['owner']['login']
    repo = json_data['repository']['name']
    return RepoInfo(owner=owner, repo=repo)


def setup(token, inputs, api_url, run_id):
    try:
        action_path = types.get_action_path('EXTRACT_WORKFLOW_DATA', run_id)
        url = build_url(api_url=api_url, owner=inputs.owner, repo=inputs.repo, action_path=action_path)
        logger.info('Posting Workflow URL: {}'.format(url))
        response = build_request(token=token, url=url, method="GET")
        if response.status != 200:
            logger.error('Failed to get API logs with status code {}'.format(response.status))
            return
        else:
            logger.info('get API logs for workflow with ID {}'.format(run_id))
            data = json.loads(response.data)
            jobs = extract_failed_jobs(data)
            failed_jobs = len(jobs)
            logger.info('{} failed job(s) was captured'.format(failed_jobs))
            for job in jobs:
                extract_steps_count_from_job(data, job.jobApiIndex, job.jobName)
            if failed_jobs >= 1:
                rerun_all_failed_jobs(run_id, api_url, inputs, token)

    except urllib3.exceptions.NewConnectionError:
        logger.error("Connection failed.")
