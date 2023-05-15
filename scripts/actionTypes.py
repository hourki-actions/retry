class types:
    EXTRACT_WORKFLOW_DATA = "actions/runs/{id}/jobs"
    RERUN_SINGLE_FAILED_JOB = "actions/jobs/{id}/rerun"
    DISPATCH_EVENT = "dispatches"
    RERUN_ALL_FAILED_WORKFLOW_JOBS = "actions/runs/{id}/rerun-failed-jobs"
    FETCH_JOB_STATUS = "actions/jobs/{id}"
    @classmethod
    def get_action_path(cls, type, id):
        path = getattr(cls, type, None)
        if path:
            return path.format(id=id)
        else:
            return None
