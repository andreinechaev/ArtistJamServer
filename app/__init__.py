__author__ = 'faradey'

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from app.config import config
from flask.ext.cache import Cache
from flask.ext.bootstrap import Bootstrap

db = SQLAlchemy()
bootstrap = Bootstrap()
cache = Cache(config={'CACHE_TYPE': 'simple'})

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.no_user'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    cache.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)

    from app.main import main as bp_main
    app.register_blueprint(bp_main)

    from app.authentication import auth as bp_auth
    app.register_blueprint(bp_auth)

    from app.stage import stage as bp_stage
    app.register_blueprint(bp_stage)

    return app
