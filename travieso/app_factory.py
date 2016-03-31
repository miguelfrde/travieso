from flask import Flask

from .config import Config
from .views import blueprint


def create_app(name, config=Config):
    app = Flask(name)
    app.config.from_object(config)
    app.register_blueprint(blueprint)
    return app
