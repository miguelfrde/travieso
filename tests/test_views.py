from unittest.mock import patch, call
from uuid import uuid4
import requests

from travieso.core import TRAVIS_PRIVATE_JOB_URL
from tests.conftest import TEST_TRAVIS_TOKEN


def test_fails_if_no_token(app, successful_payload):
    resp = app.post('/notifications', data={'payload': successful_payload})
    assert resp.status_code == requests.codes.forbidden


def test_valid_token_is_valid(app, successful_payload):
    token = uuid4().hex
    resp = app.post('/notifications', data={'payload': successful_payload},
                    headers={'Authorization': token})
    assert resp.status_code == requests.codes.unauthorized


def test_travis_payload_required(app):
    resp = app.post('/notifications')
    assert resp.status_code == requests.codes.bad


def test_no_job_tasks(app):
    pass


@patch('travieso.core.TRAVIS_TOKEN', TEST_TRAVIS_TOKEN)
def test_success_build(app, successful_payload, travis_token):
    repo = {'owner_name': 'wizeline', 'name': 'awesome'}
    commit = 'c5d7750d087adab05451efc555614c1c55b23d3b'
    job_id = 36596938
    with patch('travieso.views.notify_github') as notify_github_mock:
        resp = app.post('/notifications', data={'payload': successful_payload}, headers={'Authorization': travis_token})

        assert resp.status_code == requests.codes.ok

        calls = [call(repo, commit, 'success', task, TRAVIS_PRIVATE_JOB_URL.format(
                        account='wizeline', repo='awesome', job_id=job_id + i))
                 for i, task in enumerate(['py27', 'py35', 'flake8'])]

        notify_github_mock.assert_has_calls(calls)
