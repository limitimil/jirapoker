from flask import Flask
from flask_cors import CORS
import config
import logging.config
from controllers.auth_controller import auth
from controllers.issue_controller import issue
from controllers.user_controller import user
from controllers.game_controller import game


def create_app():
    app = Flask(__name__)
    app.register_blueprint(auth)
    app.register_blueprint(issue)
    app.register_blueprint(user)
    app.register_blueprint(game)
    app.config['SECRET_KEY'] = 'secret!'
    CORS(app)
    return app


def create_logger():

    logging.config.fileConfig(config.DEFAULT_LOG_CONFIG)
    logger = logging.getLogger('flask')
    return logger

