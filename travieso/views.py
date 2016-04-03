import requests
from flask import Blueprint

from .core import authorize_travis, notify_github, get_job_github_state, get_job_task, get_job_url


blueprint = Blueprint('travis', __name__)


@blueprint.route('/notifications', methods=['POST'])
@authorize_travis
def handle_notification(payload):
    for job in payload['matrix']:
        state = get_job_github_state(job['status'], job['state'])
        commit = job['commit']
        job_id = job['id']
        job_task = get_job_task(job)

        if job_task:
            repo = payload['repository']
            job_url = get_job_url(repo['owner_name'], repo['name'], job_id, payload['build_url'])
            notify_github(payload['repository'], commit, state, job_task, job_url)

    return 'ok', requests.codes.ok
