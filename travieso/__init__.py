import os
from .app_factory import create_app
from .config import Config, DevConfig

__version__ = '1.0.0'

app_config = DevConfig if os.getenv('FLASK_ENV') == 'development' else Config
app = create_app('travieso', app_config)
