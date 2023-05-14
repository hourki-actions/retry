import json
import os
import urllib3
from github import Github
import requests
from dataclasses import dataclass

from extract import *
from retry import *


@dataclass
class RepoInputs:
    owner: str
    repo: str


logger = Logger('Retry.check')


def fetch_workflow_inputs() -> RepoInputs:
    json_data = json.load(open(os.environ['GITHUB_EVENT_PATH']))
    owner = json_data['repository']['owner']['login']
    repo = json_data['repository']['name']
    print(os.environ['GITHUB_EVENT_PATH'])
    return RepoInputs(owner=owner, repo=repo)

def rerun_from_github(api_url, token, job_id):
    response = requests.post(
        f"{api_url}/repos/soloyak/test-app/actions/jobs/{job_id}/rerun",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        }
    )
    response.raise_for_status()


def setup(token, repoInputs, api_url, run_id):
    try:
        action_path = types.get_action_path('EXTRACT_WORKFLOW_DATA', run_id)
        url = build_url(api_url=api_url, owner=repoInputs.owner, repo=repoInputs.repo, action_path=action_path)
        logger.info('Posting Workflow URL: {}'.format(url))
        response = build_request(token=token, url=url, method="GET")
        if response.status != 200:
            logger.error('Failed to get API logs with status code {}'.format(response.status))
            return
        else:
            logger.info('Fetch workflow inputs with ID {}'.format(run_id))
            data = json.loads(response.data)
            jobs = extract_failed_jobs(data)
            # failed_jobs = len(jobs)
            # logger.info('{} failed job(s) was captured'.format(failed_jobs))
            for job in jobs:
                rerun_from_github(api_url, token, job.jobId)
            #     extract_steps_count_from_job(data, job.jobApiIndex, job.jobName)
            # if failed_jobs >= 1:
            #     rerun_all_failed_jobs(run_id, api_url, repoInputs, token)
    except urllib3.exceptions.NewConnectionError:
        logger.error("Connection failed.")
    # except (KeyError, ValueError, AttributeError, TypeError) as e:
    #     logger.error("An error occurred: {}".format(str(e)))
    # except Exception as e:
    #     logger.error("Unknown Error: {}".format(str(e)))