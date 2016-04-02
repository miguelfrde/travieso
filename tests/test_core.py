import json
import random
from unittest.mock import patch
from uuid import uuid4

import requests
import responses

from travieso.core import notify_github, get_description_from_task, get_job_github_state, get_job_task
from tests.conftest import TEST_TRAVIS_TOKEN


@patch('travieso.core.TRAVIS_TOKEN', TEST_TRAVIS_TOKEN)
def test_authorize_travis_ok(travis_app, successful_payload, travis_token):
    resp = travis_app.post('/', data={'payload': successful_payload}, headers={'Authorization': travis_token})
    assert resp.status_code == requests.codes.ok


def test_authorize_travis_no_payload(travis_app):
    resp = travis_app.post('/')
    assert resp.status_code == requests.codes.bad


def test_authorize_travis_no_token(travis_app, successful_payload):
    resp = travis_app.post('/', data={'payload': successful_payload})
    assert resp.status_code == requests.codes.forbidden


def test_authorize_travis_invalid_token(travis_app, successful_payload):
    token = uuid4().hex
    resp = travis_app.post('/', data={'payload': successful_payload},
                           headers={'Authorization': token})
    assert resp.status_code == requests.codes.unauthorized


def test_get_job_github_state():
    assert get_job_github_state(0, 'success') == 'success'
    for state in ('received', 'created', 'queued', 'started'):
        assert get_job_github_state(1, state) == 'pending'
    for state in ('canceled', 'failed'):
        assert get_job_github_state(1, state) == 'failure'
    assert get_job_github_state(1, 'errored') == 'error'


def test_get_job_task():
    with open('tests/data/travis_success_payload.json', 'r') as f:
        payload = json.loads(f.read())
    tasks = ['py27', 'py35', 'flake8']
    for i, job in enumerate(payload['matrix']):
        assert get_job_task(job) == tasks[i]


def test_get_description_from_task(faker):
    assert get_description_from_task(faker.domain_word()) == 'Build job on TravisCI'


@responses.activate
def test_notify_gihub(faker):
    repo = {'owner_name': faker.domain_word(), 'name': faker.domain_word()}
    commit = uuid4().hex
    state = random.choice(['success', 'failure', 'error', 'pending']),
    job_task = faker.domain_word()
    job_id = random.randint(1, 10000)

    request_json = {
        'state': state,
        'target_url': 'https://travis-ci/{0}/{1}/jobs/{2}'.format(repo['owner_name'], repo['name'], job_id),
        'description': get_description_from_task(job_task),
        'context': job_task
    }

    responses.add(
        responses.POST,
        'https://api.github.com/repos/{0}/{1}/statuses/{2}'.format(repo['owner_name'], repo['name'], commit),
        json=request_json)

    notify_github(repo, commit, state, job_task, job_id)

    assert len(responses.calls) == 1
