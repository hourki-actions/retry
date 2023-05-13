import urllib3
import orjson

from actionTypes import types
from logger import Logger
from builder import *


logger = Logger('Retry.run')


def get_default_workflow_permissions(token, api_url, inputs):
    url = build_url(api_url=api_url, owner=inputs.owner, repo=inputs.repo, action_path="actions/permissions/workflow")
    response = build_request(token=token, url=url, method="GET")
    logger.info('Get Workflow default permissions with status {}'.format(response.status))
    logger.info('permissions {}'.format(response.data))


def rerun_all_failed_jobs(run_id, api_url, inputs, token, job_name):
    logger.info('Job Run ID {}'.format(run_id))
    try:
        encoded_data = orjson.dumps({"enable_debug_logging": True})
        action_path = types.get_action_path('RERUN_ALL_FAILED_WORKFLOW_JOBS', run_id)
        url = build_url(api_url=api_url, owner=inputs.owner, repo=inputs.repo, action_path=action_path)
        response = build_request(token=token, url=url, method="POST", body=encoded_data)
        if response.status == 201:
            logger.info('Rerun All Jobs with status {}'.format(response.status))
            return
        else:
            logger.error('Failed to rerun job "{}" with status {}'.format(job_name, response.status))
    except urllib3.exceptions.NewConnectionError:
        logger.error("Connection failed.")
