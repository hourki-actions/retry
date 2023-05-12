import os
import urllib3
import json
import time
from typing import List
from dataclasses import dataclass

from url_builder import build_url
from logger import Logger


@dataclass
class RepoInfo:
    owner: str
    repo: str

@dataclass
class jobItem:
    jobName: str
    jobStatus: str
    jobCompletion: str
    jobApiIndex: int


logger = Logger('Retry.checker')


def get_workflow_info() -> RepoInfo:
    json_data = json.load(open(os.environ['GITHUB_EVENT_PATH']))
    owner = json_data['repository']['owner']['login']
    repo = json_data['repository']['name']
    return RepoInfo(owner=owner, repo=repo)

def extract_failed_jobs(data) -> List[jobItem]:
    jobs_items = []
    jobs = data["jobs"]
    while True:
        for job in jobs:
            job_name = job["name"]
            job_index = jobs.index(job)
            logger.info('Post job {} with status {} and conclusion {}'.format(job_name, job["status"], job["conclusion"]))
            job_item = jobItem(jobName=job_name, jobStatus=job["status"], jobCompletion=job["conclusion"], jobApiIndex=job_index)
            if job_name != "retry-action" and job_name not in jobs_items:
                jobs_items.append(job_item)
        if all(job["status"] in ["completed", "failed", "cancelled"] for job in jobs if job["name"] != "retry-action"):
            break
    return jobs_items


def extract_failed_steps_from_job(data, job_index):
    failure_count = 0
    for step in data["jobs"][job_index]["steps"]:
        if not step["name"].startswith("Set up") and not step["name"].startswith("Post"):
            step_name = step["name"]
            step_status = step["status"]
            step_conclusion = step["conclusion"]
            logger.info(
                'Job with name {} status {} conclusion {}'.format(step_name, step_status, step_conclusion))
            if step_conclusion == "failure":
                failure_count += 1
    return failure_count


def check_workflow_api(token, inputs, api_url, run_id):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = build_url(api_url=api_url, owner=inputs.owner, repo=inputs.repo, run_id=run_id)
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
            logger.info('jobs {}'.format(jobs))
            for job in jobs:
                failed_steps_per_job = extract_failed_steps_from_job(data, job.jobApiIndex)
                logger.info('steps per job {} : {}'.format(job.jobName, failed_steps_per_job))
    except urllib3.exceptions.NewConnectionError:
        logger.error("Connection failed.")
