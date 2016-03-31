import functools
import json
import logging
import os
import re
from hashlib import sha256

import requests
from flask import abort, request


TRAVIS_TOKEN = os.getenv('TRAVIS_TOKEN', '')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
TRAVIS_JOB_URL = 'https://travis-ci.com/{account}/{repo}/jobs/{job_id}'
GITHUB_API_BASE_URL = 'https://api.github.com'


def authorize_travis(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if 'payload' not in request.form:
            abort(requests.codes.bad, 'Expected a payload field with the json payload')
        payload = json.loads(request.form.get('payload'))
        token = request.headers.get('Authorization', None)
        repository = payload['repository']

        logging.info('Handling notification for repo: {0}/{1} commit {2}'.format(
            repository['owner_name'], repository['name'], payload['commit']))

        if not token:
            abort(requests.codes.forbidden, 'A token is required')

        repository = '{0}/{1}'.format(payload['repository']['owner_name'], payload['repository']['name'])
        expected_token = sha256((repository + TRAVIS_TOKEN).encode('utf-8')).hexdigest()

        if token != expected_token:
            abort(requests.codes.unauthorized, 'Invalid token')
        return f(payload, *args, **kwargs)
    return wrapper


def get_job_github_state(travis_status, travis_state):
    state = travis_state.lower()
    if travis_status == 0:  # cannot do `if not travis_status` since None represents pending
        return 'success'
    if state in ('received', 'created', 'queued', 'started'):
        return 'pending'
    if state in ('canceled', 'failed'):
        return 'failure'
    return 'error'


def get_job_task(job):
    for env in job['config']['env']:
        match = re.search(r'TASK=(.+)', env)
        if match:
            return match.group(1)


def get_description_from_task(job_task):
    # TODO: allow to configure custom messages for each expected task
    return 'Build job on TravisCI'


def notify_github(repository, commit, state, job_task, job_id):
    url = '{0}/repos/{1}/{2}/statuses/{3}'.format(
        GITHUB_API_BASE_URL, repository['owner_name'], repository['name'], commit)
    payload = {
        'state': state,
        'target_url': TRAVIS_JOB_URL.format(
            account=repository['owner_name'], repo=repository['name'], job_id=job_id),
        'description': get_description_from_task(job_task),
        'context': job_task
    }
    headers = {
        'Authorization': 'token {0}'.format(GITHUB_TOKEN),
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if not response.ok:
        logging.info('Failed to post to github, status={}, response={}'.format(response.status_code, response.content))
