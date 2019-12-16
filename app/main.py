# -*- coding: utf-8 -*-
from flask import jsonify
from flask import Flask, render_template
from pymongo import MongoClient
from flask import request
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from bson.objectid import ObjectId
import datetime
import json
import os
import logging.config
from flask_socketio import SocketIO

from config import JIRA_URL
from services.jira_client import jira_client
from services.mapping import customfield
from models.issue import Issue
from models.sprint import Sprint
from models.user import User
from lib.jira import JIRA
from jira.exceptions import JIRAError
from config import MONGO_URI
from config import DATABASE_NAME


class JSONEncoder(json.JSONEncoder):
    ''' extend json-encoder class'''
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


_PATH = os.path.dirname(os.path.abspath(__file__))
_PATH = os.path.join(_PATH, 'logging.ini')
DEFAULT_LOG_CONFIG = os.path.abspath(_PATH)

logging.config.fileConfig(DEFAULT_LOG_CONFIG)
logger = logging.getLogger('flask')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.json_encoder = JSONEncoder
CORS(app)

socketio = SocketIO(app, logger=True, engineio_logger=True, log_output=True, cors_allowed_origins="*", async_mode='threading')

mongo_client = MongoClient(MONGO_URI)
jirapoker_db = mongo_client[DATABASE_NAME]


@app.route('/api/auth/sign-in', methods=['POST'])
def sign_in():
    json_data = request.json

    jira_user = json_data['jiraUser']
    jira_token = json_data['jiraToken']
    jira_client_of_user = JIRA(JIRA_URL, basic_auth=(jira_user, jira_token))
    user_profile = jira_client_of_user.get_myself_user_profile()

    user = User()
    user.accountId = user_profile['accountId']
    user.userName = user_profile['key']
    user.avatarUrl = user_profile['avatarUrls']['48x48']

    queried_user = jirapoker_db.user.find_one({'userName': user.userName})
    if queried_user:
        jirapoker_db.user.update_one({'_id': queried_user['_id']},
                                     {'$set': user.__dict__})
    else:
        jirapoker_db.user.insert_one(user.__dict__)
    return jsonify(user.__dict__)


@app.route('/api/issue/<board_name>/active-and-future-sprints', methods=['GET'])
def get_issues_in_active_and_future_sprints_in_board(board_name):
    sprint_names = jira_client.get_active_and_future_sprint_names_in_board(board_name)

    issues_in_active_and_future_sprints = []  # [{'sprint_A': ['issue_A', ...]}, {'sprintB': ['issue_C'...]}...]
    for sprint_name in sprint_names:
        _issues = jira_client.search_issues('sprint="{}" AND issuetype not in (Sub-task, 估點, Memo)'.format(sprint_name),
                                            startAt=0,
                                            maxResults=False)
        issues = []
        for _issue in _issues:
            issue_story_point = 0.0
            if customfield['story_point'] in _issue.raw['fields'].keys():
                issue_story_point = _issue.raw['fields'][customfield['story_point']]

            issue = Issue()
            issue.issueKey = _issue.key
            issue.url = JIRA_URL + '/browse/{}'.format(_issue.key)
            issue.summary = _issue.fields.summary
            issue.description = _issue.fields.description
            issue.storyPoint = issue_story_point
            issue.sprintName = sprint_name
            issues.append(issue.__dict__)

        sprint = Sprint()
        sprint.sprintName = sprint_name
        sprint.issues = issues

        issues_in_active_and_future_sprints.append(sprint.__dict__)
    return jsonify(issues_in_active_and_future_sprints)


@app.route('/api/issue/story-point', methods=['PUT'])
def update_story_point_in_jira():
    request_body = request.json

    issue = jira_client.issue(request_body['issueKey'])
    issue.update(fields={customfield['story_point']: request_body['storyPoint']})

    return 'Update story point successfully', 200


@app.route('/api/issue/estimation-result', methods=['POST'])
def insert_issue_estimation_result():
    request_body = request.json

    estimation_record_of_issue_by_user = jirapoker_db.estimation_result.find_one({'issueKey': request_body['issueKey'],
                                                                                  'userName': request_body['userName']})
    if not estimation_record_of_issue_by_user:
        jirapoker_db.estimation_result.insert_one(request_body)
    else:
        estimation_record_of_issue_by_user.update({'estimatedStoryPoint': request_body['estimatedStoryPoint']})
        jirapoker_db.estimation_result.update_one({'_id': estimation_record_of_issue_by_user['_id']},
                                                  {'$set': estimation_record_of_issue_by_user})

    issue_estimation_results = list(jirapoker_db.estimation_result.find({'issueKey': request_body['issueKey']},
                                                                        {'_id': False}))
    socketio.emit('issueEstimationResults', issue_estimation_results)
    return "OK", 200


@app.route('/api/issue/<issue_key>/estimation-results', methods=['DELETE'])
def delete_issue_estimation_results(issue_key):
    jirapoker_db.estimation_result.delete_many({'issueKey': issue_key})
    socketio.emit('deleteIssueEstimationResults', issue_key)
    return "OK", 200


@app.route('/api/issue/estimated-story-point/<issue_key>/<user_name>', methods=['GET'])
def get_issue_estimated_story_point(issue_key, user_name):
    estimation_record_of_issue_by_user = jirapoker_db.estimation_result.find_one({'issueKey': issue_key,
                                                                                  'userName': user_name},
                                                                                 {'_id': False})
    if not estimation_record_of_issue_by_user:
        return ''
    estimated_story_point_by_user = estimation_record_of_issue_by_user['estimatedStoryPoint']
    return estimated_story_point_by_user, 200


@app.route('/api/issue/status', methods=['POST'])
def insert_issue_status():
    request_body = request.json
    issue_status_record = jirapoker_db.issue_status.find_one({'issueKey': request_body['issueKey']})
    if not issue_status_record:
        jirapoker_db.issue_status.insert_one(request_body)
    else:
        issue_status_record.update({'isRevealed': request_body['isRevealed']})
        jirapoker_db.estimation_result.update_one({'_id': issue_status_record['_id']},
                                                  {'$set': issue_status_record})

    socketio.emit('InsertIssueStatus', {'issueKey': request_body['issueKey'],
                                  'isRevealed': request_body['isRevealed']})
    return 'OK', 200


@app.route('/api/issue/<issue_key>/status', methods=['DELETE'])
def delete_issue_status(issue_key):
    jirapoker_db.issue_status.remove({'issueKey': issue_key})
    socketio.emit('deleteIssueStatus', issue_key)
    return 'OK', 200


@app.route('/api/issue/<issue_key>/status/<status_name>', methods=['GET'])
def get_issue_status(issue_key, status_name):
    issue_status_record = jirapoker_db.issue_status.find_one({'issueKey': issue_key})
    if not issue_status_record or issue_status_record[status_name] is False:
        return jsonify(False), 200
    return jsonify(True), 200


@app.route('/api/user/<user_name>/estimated-issue-keys', methods=['GET'])
def get_user_estimated_issues(user_name):
    user_estimated_issues = list(jirapoker_db.estimation_result.find({'userName': user_name}, {'_id': False}))
    user_estimated_issue_keys = {}
    for user_estimated_issue in user_estimated_issues:
        user_estimated_issue_keys[user_estimated_issue['issueKey']] = True
    return jsonify(user_estimated_issue_keys)


@app.route('/api/issue/<issue_key>/estimation-results', methods=['GET'])
def get_issue_estimation_results(issue_key):
    issue_estimation_results = list(jirapoker_db.estimation_result.find({'issueKey': issue_key}, {'_id': False}))
    return jsonify(issue_estimation_results)


@app.route('/api/user/<user_name>/avatar-url', methods=['GET'])
def get_user_avatar_url(user_name):
    queried_user = jirapoker_db.user.find_one({'userName': user_name})
    if not queried_user:
        return '', 200
    else:
        return queried_user['avatarUrl'], 200


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
