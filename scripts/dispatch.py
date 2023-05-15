import urllib3


from logger import Logger
from builder import *

logger = Logger('Retry.dispatch')


def send_repo_dispatch_event(run_id, api_url, inputs, token, failed_jobs_ids):
    try:
        url = build_url(api_url=api_url, owner=inputs.owner, repo=inputs.repo, action_path="dispatches")
        payload = {
            "event_type": "retry-event",
            "client_payload": {
                "workflow_id": f"{run_id}",
                "failed_job_ids": failed_jobs_ids,
                "max_retries": 3
            }
        }
        response = build_request(token=token, url=url, method="POST", payload=payload)
        if response.status == 204:
            logger.info('Workflow Dispatch was triggered with {}'.format(response.status))
        else:
            logger.error('Cannot trigger dispatch workflow failed job(s) with status {}'.format(response.status))
    except urllib3.exceptions.NewConnectionError:
        logger.error("Connection failed.")
