import urllib3
import orjson

from actionTypes import types
from logger import Logger
from builder import *


logger = Logger('Retry.run')


def get_default_workflow_permissions(token, api_url, inputs):
    url = build_url(api_url=api_url, owner=inputs.owner, repo=inputs.repo, action_path="actions/permissions/workflow")
    response = build_request(token=token, url=url, method="GET")
    logger.info('Get Workflow default permissions {}'.format(response.status))
    logger.info('Before set {}'.format(response.data))


def set_defaukt_workflow_permissions(token, api_url, inputs):
    encoded_data = orjson.dumps({"default_workflow_permissions": "write"})
    url = build_url(api_url=api_url, owner=inputs.owner, repo=inputs.repo, action_path="actions/permissions/workflow")
    response = build_request(token=token, url=url, method="PUT", body=encoded_data)
    logger.info('Set Workflow default permissions {}'.format(response.status))
    logger.info('After set {}'.format(response.data))

def rerun_all_failed_jobs(run_id, api_url, inputs, token, job_name):
    get_default_workflow_permissions(token, api_url, inputs)
    set_defaukt_workflow_permissions(token, api_url, inputs)
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
