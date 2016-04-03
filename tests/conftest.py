import pytest
from faker import Factory
from flask import Flask
from hashlib import sha256

from travieso import create_app
from travieso.config import TestConfig
from travieso.core import authorize_travis

TEST_TRAVIS_TOKEN = '123456789abcdefg'


@pytest.yield_fixture
def app(request):
    app = create_app('test', TestConfig)
    ctx = app.app_context()
    ctx.push()
    yield app.test_client()
    ctx.pop()


@pytest.fixture(scope='session')
def faker():
    return Factory.create()


@pytest.yield_fixture
def travis_app():
    app = Flask('test_travis')
    app.config.from_object(TestConfig)

    @app.route('/', methods=['POST'])
    @authorize_travis
    def test_route(payload):
        return 'ok'

    ctx = app.app_context()
    ctx.push()
    yield app.test_client()
    ctx.pop()


@pytest.fixture(scope='session')
def successful_payload():
    with open('tests/data/travis_success_payload.json') as f:
        return f.read()


@pytest.fixture(scope='session')
def travis_token():
    return sha256(('wizeline/awesome' + TEST_TRAVIS_TOKEN).encode('utf-8')).hexdigest()
