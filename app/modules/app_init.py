from flask import Flask
from flask_cors import CORS
import os
import logging.config
from controllers.auth_controller import auth
from controllers.issue_controller import issue
from controllers.user_controller import user


def create_app():
    app = Flask(__name__)
    app.register_blueprint(auth)
    app.register_blueprint(issue)
    app.register_blueprint(user)
    app.config['SECRET_KEY'] = 'secret!'
    CORS(app)
    return app


def create_logger():
    _PATH = os.path.dirname(os.path.abspath(__file__))
    _PATH = os.path.join(_PATH, 'logging.ini')
    _DEFAULT_LOG_CONFIG = os.path.abspath(_PATH)
    logging.config.fileConfig(_DEFAULT_LOG_CONFIG)
    logger = logging.getLogger('flask')
    return logger

