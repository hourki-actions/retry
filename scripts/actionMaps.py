class ActionMaps:
    EXTRACT_WORKFLOW_DATA = "actions/runs/{id}/jobs"
    RERUN_WORKFLOW = "actions/jobs/{id}/rerun"
    @classmethod
    def get_action_path(cls, type, id):
        path = getattr(cls, type, None)
        if path:
            return path.format(id=id)
        else:
            return None
