# -*- coding: utf-8 -*-
import os
os.environ['PYTHONPATH'] = os.path.dirname(__file__)
print(os.environ['PYTHONPATH'])

from flask import jsonify
from flask_socketio import SocketIO
from werkzeug.exceptions import HTTPException
from jira.exceptions import JIRAError

from app import create_logger
from app import create_app


logger = create_logger()
app = create_app()

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


@app.errorhandler(Exception)
def handle_error(e):
    print(type(e))
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    elif isinstance(e, JIRAError):
        code = e.status_code
    logger.error('%s', str(e))
    return jsonify(error=str(e)), code


@socketio.on('connect')
def connected():
    print('Client connected')


@socketio.on('message')
def connected():
    print('receive message')


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    # app.run(host='0.0.0.0', port=80)
