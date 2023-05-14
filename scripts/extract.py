from typing import List
from dataclasses import dataclass
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
from github import Github

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


def extract_steps_count_from_job(data, job_index, job_name, token):
    failure_count = 0
    skip_count = 0
    G = nx.DiGraph()
    for step in data["jobs"][job_index]["steps"]:
        excluded_steps = ["Set up", "Post", "Complete job"]
        if not any(step["name"].startswith(name) for name in excluded_steps):
            step_tuple = tuple(step.items())
            G.add_node(step_tuple)
            for i, step in enumerate(data["jobs"][job_index]["steps"]):
               if i+1 < len(data["jobs"][job_index]["steps"]):
                   next_step_tuple = tuple(data["jobs"][job_index]["steps"][i+1].items())
                   G.add_edge(step_tuple, next_step_tuple)
            step_conclusion = step["conclusion"]
            if step_conclusion == "failure":
                failure_count += 1
            elif step_conclusion == "skipped":
                skip_count += 1
    logger.info('{} failed / {} skipped step(s) for job "{}"'.format(failure_count, skip_count, job_name))
    nx.draw(G, with_labels=True)
    figfile = io.BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue()).decode('utf-8')
    image_data = bytes(figdata_png)
    plt.clf()
    plt.close()
    image_path = f"{job_name}.png"
    g = Github(token)
    repo = g.get_repo("soloyak/test-app")
    try:
        contents = repo.get_contents(image_path)
        repo.update_file(contents.path, "update image", image_data, contents.sha)
    except:
        repo.create_file(image_path, "new push", image_data)
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
