from typing import List
from dataclasses import dataclass
import networkx as nx
import matplotlib.pyplot as plt

from logger import Logger


@dataclass
class jobItem:
    jobName: str
    jobId: str
    jobStatus: str
    jobCompletion: str
    jobApiIndex: int


logger = Logger('Retry.extract')


def create_failed_steps_graph(data, job_index):
    failed_steps = extract_failed_steps(data, job_index)
    G = nx.DiGraph()
    for step in failed_steps:
        G.add_node(step)
    for i, step in enumerate(failed_steps):
        if i+1 < len(failed_steps):
            G.add_edge(step, failed_steps[i+1])
    return G


def extract_steps_count_from_job(data, job_index, job_name):
    failure_count = 0
    skip_count = 0
    G = nx.DiGraph()
    for step in data["jobs"][job_index]["steps"]:
        excluded_steps = ["Set up", "Post", "Complete job"]
        if not any(step["name"].startswith(name) for name in excluded_steps):
            G.add_node(step)
            for i, step in enumerate(data["jobs"][job_index]["steps"]):
               if i+1 < len(data["jobs"][job_index]["steps"]):
                 G.add_edge(step, data["jobs"][job_index]["steps"][i+1])
            step_conclusion = step["conclusion"]
            if step_conclusion == "failure":
                failure_count += 1
            elif step_conclusion == "skipped":
                skip_count += 1
    logger.info('{} failed / {} skipped step(s) for job "{}"'.format(failure_count, skip_count, job_name))
    nx.draw(G, with_labels=True)
    plt.show()
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
