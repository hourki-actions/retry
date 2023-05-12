import urllib3

from actionTypes import types
from logger import Logger
from builder import *


logger = Logger('Retry.run')


def rerun_all_failed_jobs(run_id, api_url, inputs, token, job_name):
    try:
        action_path = types.get_action_path('RERUN_ALL_FAILED_WORKFLOW_JOBS', run_id)
        url = build_url(api_url=api_url, owner=inputs.owner, repo=inputs.repo, action_path=action_path)
        response = build_request(token=token, url=url, method="POST")
        if response.status != 201:
            logger.error('Failed to rerun job "{}" with status {}'.format(job_name, response.status))
            return
        else:
            logger.info('Rerun All Jobs with status {}'.format(response.status))
    except urllib3.exceptions.NewConnectionError:
        logger.error("Connection failed.")
