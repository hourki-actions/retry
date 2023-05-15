import json
import os
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


def retry_from_dispatched_event(token, run_id, failed_jobs_ids, max_retries):
    logger.info("received workflow id {}".format(run_id))
    logger.info("received failed jobs ids id {}".format(failed_jobs_ids))



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
            for job in failed_jobs_list and failed_jobs_list >= 1:
                extract_steps_count_from_job(data, job.jobApiIndex, job.jobName)
                failed_jobs_ids.append(job.jobId)
                send_repo_dispatch_event(token, run_id, api_url, inputs, failed_jobs_ids)
    except urllib3.exceptions.NewConnectionError:
        logger.error("Connection failed.")
    except (KeyError, ValueError, AttributeError, TypeError) as e:
        logger.error("An error occurred: {}".format(str(e)))
    except Exception as e:
        logger.error("Unknown Error: {}".format(str(e)))
