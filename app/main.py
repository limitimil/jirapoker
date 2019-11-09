# -*- coding: utf-8 -*-
from flask import jsonify
from flask import Flask
from flask import request
from werkzeug.exceptions import HTTPException

from flask_cors import CORS

import json
import os
import re
import logging.config

from config import JIRA_URL
from services.jira_client import jira_client
from services.mapping import customfield
from models.issue import Issue
from models.user import User
from lib.jira import JIRA


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


@app.route('/api/<project>/GetIssuesInSprints', methods=['GET'])
def get_project_issues_in_sprints(project):
    project_issues = jira_client.search_issues('project={} AND (SPRINT not in closedSprints() OR SPRINT in openSprints()) AND issuetype not in (Sub-task, 估點, Memo)'.format(project), startAt=0, maxResults=False)

    issues = []
    for issue in project_issues:
        active_sprint = re.findall(r"state=ACTIVE,name=[^,]*", str(issue.raw['fields'][customfield['sprint']]))
        future_sprint = re.findall(r"state=FUTURE,name=[^,]*", str(issue.raw['fields'][customfield['sprint']]))

        if active_sprint:
            issue_sprint_name = active_sprint[0].replace('state=ACTIVE,name=', '')
        elif future_sprint:
            issue_sprint_name = future_sprint[0].replace('state=FUTURE,name=', '')

        issue_story_point = 0.0
        if customfield['story_point'] in issue.raw['fields'].keys():
            issue_story_point = issue.raw['fields'][customfield['story_point']]

        _issue = Issue()
        _issue.issueKey = issue.key
        _issue.url = JIRA_URL + '/browse/{}'.format(issue.key)
        _issue.summary = issue.fields.summary
        _issue.description = issue.fields.description
        _issue.storyPoint = issue_story_point
        _issue.sprintName = issue_sprint_name
        issues.append(_issue.__dict__)

    return jsonify(issues)


@app.route('/api/<issue_key>/UpdateStoryPoint', methods=['PUT'])
def update_story_point(issue_key):
    json_data = request.json

    issue = jira_client.issue(issue_key)
    issue.update(fields={customfield['story_point']: json_data['storyPoint']})

    return 'Update story point successfully', 200


@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    logger.error('%s', str(e))
    return jsonify(error=str(e)), code


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
