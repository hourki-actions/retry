import urllib3
import json


from logger import Logger
from builder import *

logger = Logger('Retry.dispatch')


def send_repo_dispatch_event(run_id, api_url, inputs, token, failed_jobs_ids):
    try:
        jobs_ids = ""
        if isinstance(failed_jobs_ids, list):
            jobs_ids = ":".join(failed_jobs_ids)
        elif isinstance(failed_jobs_ids, str):
            jobs_ids = failed_jobs_ids
        else:
            logger.error("error of parsed type for jobs ids")
        logger.info("final output for jobs ids".format(jobs_ids))
        url = build_url(api_url=api_url, owner=inputs.owner, repo=inputs.repo, action_path="dispatches")
        logger.info('Posting Workflow URL: {}'.format(url))
        logger.info('Failed ids {}'.format(failed_jobs_ids))
        payload = {
            "event_type": "retry-event",
            "client_payload": {
                "workflow_id": f"{run_id}",
                "failed_job_ids": f"{jobs_ids}",
                "max_retries": "3",
                "from_dispatch": "true"
            }
        }
        response = build_request(token=token, url=url, method="POST", payload=json.dumps(payload))
        if response.status == 204:
            logger.info('Workflow Dispatch was triggered')
        else:
            logger.error('Cannot trigger dispatch workflow with status {}'.format(response.status))
            logger.error(response.data)
    except urllib3.exceptions.NewConnectionError:
        logger.error("Connection failed.")
