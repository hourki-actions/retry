from typing import List
from dataclasses import dataclass

from logger import Logger


@dataclass
class jobItem:
    jobName: str
    jobId: str
    jobStatus: str
    jobCompletion: str
    jobApiIndex: int


logger = Logger('Retry.extract')


def extract_steps_count_from_job(data, job_index, job_name):
    failure_count = 0
    skip_count = 0
    for step in data["jobs"][job_index]["steps"]:
        if not step["name"].startswith("Set up") and not step["name"].startswith("Post") and not step["name"] == "Complete job":
            step_conclusion = step["conclusion"]
            if step_conclusion == "failure":
                failure_count += 1
            elif step_conclusion == "skipped":
                skip_count += 1
    logger.info('{} / {} failed/skipped step(s) for job "{}"'.format(failure_count, skip_count, job_name))
    return failure_count, skip_count


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
