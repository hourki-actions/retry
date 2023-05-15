import json
import os
import time
import urllib3
from dataclasses import dataclass

from extract import *
from dispatch import *
from actionTypes import types


@dataclass
class RepoInputs:
    owner: str
    repo: str


logger = Logger('Retry.check')


def check_job_status(job_id, inputs, token, api_url):
    action_path = types.get_action_path('FETCH_JOB_STATUS', job_id)
    url = build_url(api_url=api_url, owner=inputs.owner, repo=inputs.repo, action_path=action_path)
    while True:
        response = build_request(token=token, url=url, method="GET")
        if response.status == 200:
            data = json.loads(response.data)
            status = data["status"]
            conclusion = data["conclusion"]
            if status == "completed" and conclusion == "failure":
                logger.info("Job {} completed".format(job_id))
                return
            else:
                logger.info("Job {} status: {}. Waiting...".format(job_id, status))
        else:
            logger.error("Error fetching job status: {}".format(response.status))
        time.sleep(10)


def retry_from_dispatched_event(token, failed_jobs_ids, api_url, inputs):
    if ":" in failed_jobs_ids:
        joined_ids = failed_jobs_ids.split(":")
        for id in joined_ids:
            check_job_status(id, inputs, token, api_url)
            action_path = types.get_action_path('RERUN_SINGLE_FAILED_JOB', id)
            url = build_url(api_url=api_url, owner=inputs.owner, repo=inputs.repo, action_path=action_path)
            response = build_request(token=token, url=url, method="POST")
            logger.info(response.status)
    else:
        logger.info("extracted one single job with id {}".format(failed_jobs_ids))


def fetch_workflow_inputs() -> RepoInputs:
    json_data = json.load(open(os.environ['GITHUB_EVENT_PATH']))
    owner = json_data['repository']['owner']['login']
    repo = json_data['repository']['name']
    return RepoInputs(owner=owner, repo=repo)


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
            logger.info('Fetch workflow inputs with ID {}'.format(run_id))
            data = json.loads(response.data)
            failed_jobs_list = extract_failed_jobs(data)
            failed_jobs_count = len(failed_jobs_list)
            logger.info('{} failed job(s) was captured'.format(failed_jobs_count))
            failed_jobs_ids = []
            if failed_jobs_count >= 1:
                for job in failed_jobs_list:
                    extract_steps_count_from_job(data, job.jobApiIndex, job.jobName)
                    failed_jobs_ids.append(str(job.jobId))
                if len(failed_jobs_ids) > 1:
                    joined_ids = ":".join(failed_jobs_ids)
                    send_repo_dispatch_event(run_id, api_url, inputs, token, joined_ids)
                else:
                    send_repo_dispatch_event(run_id, api_url, inputs, token, failed_jobs_ids[0])

    except urllib3.exceptions.NewConnectionError:
        logger.error("Connection failed.")
    # except (KeyError, ValueError, AttributeError, TypeError) as e:
    #     logger.error("An error occurred: {}".format(str(e)))
    # except Exception as e:
    #     logger.error("Unknown Error: {}".format(str(e)))
