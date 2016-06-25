import requests
from flask import Blueprint

from .core import authorize_travis, notify_github, get_job_github_state, get_job_task, get_job_url


blueprint = Blueprint('travis', __name__)


@blueprint.route('/notifications', methods=['POST'])
@authorize_travis
def handle_notification(payload):
    head_commit = payload['head_commit']
    for job in payload['matrix']:
        state = get_job_github_state(job['status'], job['state'])
        # For pull requests, the commit_sha we get back is that of the merge_commit_sha.
        # We don't want this!
        commit = head_commit if payload['type'] == 'pull_request' else job['commit']
        commit = job['commit']
        job_id = job['id']
        job_task = get_job_task(job)

        if job_task:
            repo = payload['repository']
            job_url = get_job_url(repo['owner_name'], repo['name'], job_id, payload['build_url'])
            notify_github(payload['repository'], commit, state, job_task, job_url)

    return 'ok', requests.codes.ok
