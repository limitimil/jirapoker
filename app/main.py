# -*- coding: utf-8 -*-
import os
import eventlet
# To make std library non-blocking(here will blocked by requests)
eventlet.monkey_patch()
os.environ['PYTHONPATH'] = os.path.dirname(__file__)
print(os.environ['PYTHONPATH'])

from flask import jsonify
from flask_socketio import SocketIO
from werkzeug.exceptions import HTTPException
from jira.exceptions import JIRAError

from database.jirapoker_db import jirapoker_db
from modules.app_init import create_logger
from modules.app_init import create_app

logger = create_logger()
app = create_app()

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')


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


@socketio.on('insertIssueEstimationResult')
def return_estimation_results(issue_key):
    issue_estimation_results = list(jirapoker_db.estimation_result.find({'issueKey': issue_key}, {'_id': False}))
    returned_issue_estimation_results = []
    if issue_estimation_results:
        for issue_estimation_result in issue_estimation_results:
            user = jirapoker_db.user.find_one({'_id': issue_estimation_result['userId']},
                                              {'_id': False})
            issue_estimation_result.pop('userId')
            issue_estimation_result['user'] = user
            returned_issue_estimation_results.append(issue_estimation_result)
        socketio.emit('updateCurrentIssueEstimationResults', returned_issue_estimation_results)
        socketio.emit('updateUserEstimatedIssueKey', {'userAccountId': user.accountId, 'issueKey': issue_key})


@socketio.on('deleteIssueEstimationResults')
def delete_issue_estiamtion_results(issue_key):
    socketio.emit('resetCurrentIssue', issue_key)
    socketio.emit('resetUserEstimatedIssueKey', issue_key)


@socketio.on('insertIssueStatus')
def insert_issue_status(status):
    socketio.emit('updateCurrentIssueStatus', status)


@socketio.on('deleteIssueStatus')
def delete_issue_status(issue_key):
    socketio.emit('resetCurrentIssueStatus', issue_key)


@socketio.on('connect')
def connected():
    print('Client connected')


@socketio.on('message')
def connected():
    print('receive message')


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', debug=True)
    # app.run(host='0.0.0.0', port=80)
