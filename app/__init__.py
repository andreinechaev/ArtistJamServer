__author__ = 'faradey'

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from app.config import config

db = SQLAlchemy()


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.no_user'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)

    from app.main import main as bp_main
    app.register_blueprint(bp_main)

    login_manager.init_app(app)

    from app.authentication import auth as bp_auth

    app.register_blueprint(bp_auth)

    return app
