# -*- coding: utf-8 -*-
from flask import jsonify
from flask import Flask
from flask import request
from werkzeug.exceptions import HTTPException

from flask_cors import CORS

import os
import logging.config

from config import JIRA_URL
from services.jira_client import jira_client
from services.mapping import customfield
from models.issue import Issue
from models.sprint import Sprint
from models.user import User
from lib.jira import JIRA
from jira.exceptions import JIRAError


_PATH = os.path.dirname(os.path.abspath(__file__))
_PATH = os.path.join(_PATH, 'logging.ini')
DEFAULT_LOG_CONFIG = os.path.abspath(_PATH)

logging.config.fileConfig(DEFAULT_LOG_CONFIG)
logger = logging.getLogger('flask')

app = Flask(__name__)
CORS(app)


@app.route('/api/auth/SignIn', methods=['POST'])
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

    return jsonify(user.__dict__)


@app.route('/api/IssuesInActiveAndFutureSprints/<board_name>', methods=['GET'])
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


@app.route('/api/<issue_key>/UpdateStoryPoint', methods=['PUT'])
def update_story_point(issue_key):
    json_data = request.json

    issue = jira_client.issue(issue_key)
    issue.update(fields={customfield['story_point']: json_data['storyPoint']})

    return 'Update story point successfully', 200


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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
