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
    response = build_request(token=token, url=url, method="GET")
    if response.status == 200:
        data = json.loads(response.data)
        status = data["status"]
        conclusion = data["conclusion"]
        job_name = data["name"]
        return status, conclusion, job_name
    else:
        logger.error("Error fetching job status: {}".format(response.status))


def retry_from_dispatched_event(run_id, token, failed_jobs_ids, api_url, inputs):
    if ":" in failed_jobs_ids:
        joined_ids = failed_jobs_ids.split(":")
        for job_id in joined_ids:
            retry_count = 0
            while retry_count < 3:
                time.sleep(5)
                status, conclusion, job_name = check_job_status(job_id, inputs, token, api_url)
                if status == "completed" and conclusion == "failure":
                    action_path = types.get_action_path('RERUN_SINGLE_FAILED_JOB', job_id)
                    url = build_url(api_url=api_url, owner=inputs.owner, repo=inputs.repo, action_path=action_path)
                    response = build_request(token=token, url=url, method="POST")
                    if response.status == 204:
                        logger.info("retry count {} for job {}".format(retry_count, job_name))
                        logger.info("Job {} re-run made with success".format(job_name))
                        retry_count += 1
                    elif response.status == 403:
                        logger.info("Job {} re-run has an issue with status {}".format(job_name, response.status))
                        logger.info("log data {}".format(response.data))
                        retry_count += 1
                elif status == "completed" and conclusion == "success":
                    logger.info("Job {} has been completed with {}".format(job_name, conclusion))
                    break
                elif status == "in_progress":
                    logger.error("Job {} is in progress".format(job_name))
                    retry_count += 1
                else:
                    logger.info("retry {} for job {}".format(retry_count, job_name))
                    retry_count += 1
            else:
                logger.info("Maximum retries '{}' has been reached for job {}".format(retry_count, job_name))
    else:
        logger.info("TBD")


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
