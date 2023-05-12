import os
import urllib3
import threading
import json
from typing import List
from dataclasses import dataclass

from url_builder import build_url
from actionMaps import ActionMaps
from logger import Logger


@dataclass
class RepoInfo:
    owner: str
    repo: str


@dataclass
class jobItem:
    jobName: str
    jobId: str
    jobStatus: str
    jobCompletion: str
    jobApiIndex: int


logger = Logger('Retry.checker')


def get_workflow_info() -> RepoInfo:
    json_data = json.load(open(os.environ['GITHUB_EVENT_PATH']))
    owner = json_data['repository']['owner']['login']
    repo = json_data['repository']['name']
    return RepoInfo(owner=owner, repo=repo)


def rerun_failed_job_by_id(id, job_name, api_url, inputs, token, lock):
    action_path = ActionMaps.get_action_path('RERUN_WORKFLOW', id)
    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = build_url(api_url=api_url, owner=inputs.owner, repo=inputs.repo, action_path=action_path)
    logger.info('Posting Rerun Workflow URL: {}'.format(url))
    lock.acquire()
    try:
        response = urllib3.request("POST", url, headers=headers)
        if response.status != 201:
            logger.error('Failed to rerun job {} with status code {}'.format(job_name, response.status))
            return
        else:
            logger.info('Rerun Job {}'.format(job_name))
    except urllib3.exceptions.NewConnectionError:
        logger.error("Connection failed.")
    finally:
        lock.release()


def rerun_all_failed_jobs(run_id, api_url, inputs, token):
    action_path = ActionMaps.get_action_path('RERUN_ALL_FAILED_WORKFLOW_JOBS', run_id)
    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = build_url(api_url=api_url, owner=inputs.owner, repo=inputs.repo, action_path=action_path)
    logger.info('Posting Rerun All failed Workflow URL: {}'.format(url))
    try:
        response = urllib3.request("POST", url, headers=headers)
        if response.status != 201:
            logger.error('Failed to rerun all jobs with status {}'.format(response.status))
            return
        else:
            logger.info('Rerun All Jobs with status {}'.format(response.status))
    except urllib3.exceptions.NewConnectionError:
        logger.error("Connection failed.")


def extract_failed_jobs(data) -> List[jobItem]:
    jobs_items = []
    jobs = data["jobs"]
    while True:
        for job in jobs:
            job_name = job["name"]
            job_index = jobs.index(job)
            if job_name != "retry-action" and job_name not in jobs_items and job["conclusion"] == "failure":
                job_item = jobItem(jobName=job_name, jobId=job["id"], jobStatus=job["status"], jobCompletion=job["conclusion"], jobApiIndex=job_index)
                jobs_items.append(job_item)
        if all(job["status"] in ["completed", "failed", "cancelled"] for job in jobs if job["name"] != "retry-action"):
            break
    return jobs_items


def extract_steps_count_from_job(data, job_index):
    failure_count = 0
    skip_count = 0
    for step in data["jobs"][job_index]["steps"]:
        if not step["name"].startswith("Set up") and not step["name"].startswith("Post") and not step["name"] == "Complete job":
            step_conclusion = step["conclusion"]
            if step_conclusion == "failure":
                failure_count += 1
            elif step_conclusion == "skipped":
                skip_count += 1
    return failure_count, skip_count


def check_workflow_api(token, inputs, api_url, run_id):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    action_path = ActionMaps.get_action_path('EXTRACT_WORKFLOW_DATA', run_id)
    url = build_url(api_url=api_url, owner=inputs.owner, repo=inputs.repo, action_path=action_path)
    logger.info('Posting Workflow URL: {}'.format(url))
    try:
        response = urllib3.request("GET", url, headers=headers)
        if response.status != 200:
            logger.error('Failed to get API logs with status code {}'.format(response.status))
            return
        else:
            logger.info('get API logs for workflow with ID {}'.format(run_id))
            data = json.loads(response.data)
            jobs = extract_failed_jobs(data)
            failed_jobs = len(jobs)
            logger.info('{} failed job(s) was captured'.format(failed_jobs))
            rerun_all_failed_jobs(run_id, api_url, inputs, token)
            # threads = []
            # for job in jobs:
            #     lock = threading.Lock()
            #     failed_steps_per_job, skipped_steps_per_job = extract_steps_count_from_job(data, job.jobApiIndex)
            #     logger.info('{} failed step(s) and {} skipped step(s) for job {}'.format(failed_steps_per_job,
            #                                                                              skipped_steps_per_job,
            #                                                                              job.jobName))
            #     t = threading.Thread(target=rerun_failed_job_by_id,
            #                          args=(job.jobId, job.jobName, api_url, inputs, token, lock))
            #     threads.append(t)
            #     t.start()
            #     t.join()
            #     # rerun_failed_job_by_id(job.jobId, job.jobName, api_url, inputs, token)
            # for t in threads:
            #     t.join()
    except urllib3.exceptions.NewConnectionError:
        logger.error("Connection failed.")
