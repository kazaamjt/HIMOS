from flask import Flask
from Server.Config import flask_settings
from datetime import datetime
from flask_bootstrap import Bootstrap
from redis import StrictRedis as Redis
from Server.app.utils import from_string_to_datetime, get_collapsed

from Server.app.lib.momentjs import momentjs

bootstrap = Bootstrap()
redis = None


def create_app(config_name):
    """
    creates the Flask app.
    """
    global redis  # hack. maybe use https://github.com/underyx/flask-redis

    config_obj = flask_settings[config_name]
    app = _base_app(config=config_obj)

    # init redis
    # https://redis-py.readthedocs.io/en/latest/
    redis = Redis(host=config_obj.REDIS_HOST, port=config_obj.REDIS_PORT, decode_responses=True,db=config_obj.REDIS_DB)

    from .dashboard import main as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    from .admin_dashboard import admin as admin_dashboard_blueprint
    app.register_blueprint(admin_dashboard_blueprint, url_prefix='/admin')

    from .admin_api import admin_api as admin_api_blueprint
    app.register_blueprint(admin_api_blueprint, url_prefix='/admin_api')

    return app


def _base_app(config):
    """
    init a barebone flask app.
    if it is needed to create multiple flask apps,
    use this function to create a base app which can be further modified later
    """
    app = Flask(__name__)

    app.config.from_object(config)
    config.init_app(app)

    bootstrap.init_app(app)

    app.jinja_env.globals['datetime'] = datetime
    app.jinja_env.globals['str_to_datetime'] = lambda x: from_string_to_datetime(x)
    app.jinja_env.globals['format_float'] = lambda x: "%.2f" % x if x else None
    app.jinja_env.globals['momentjs'] = momentjs
    app.jinja_env.globals['get_collapsed_ids'] = get_collapsed

    return app
