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


_PATH = os.path.dirname(os.path.abspath(__file__))
_PATH = os.path.join(_PATH, 'logging.ini')
DEFAULT_LOG_CONFIG = os.path.abspath(_PATH)

logging.config.fileConfig(DEFAULT_LOG_CONFIG)
logger = logging.getLogger('flask')

app = Flask(__name__)
CORS(app)


@app.route('/api/<project>/GetIssuesInSprints', methods=['GET'])
def get_project_issues_in_sprints(project):
    project_issues = jira_client.search_issues('project={} AND (SPRINT not in closedSprints() OR SPRINT in openSprints())'.format(project), startAt=0, maxResults=False)

    issues = []
    for issue in project_issues:
        issue_sprint = re.findall(r"name=[^,]*", str(issue.raw['fields'][customfield['sprint']][0]))[0]
        issue_sprint = issue_sprint.replace('name=', '')

        issue_story_point = 0.0
        if customfield['story_point'] in issue.raw['fields'].keys():
            issue_story_point = issue.raw['fields'][customfield['story_point']]

        _issue = Issue()
        _issue.IssueKey = issue.key
        _issue.Url = JIRA_URL + '/browse/{}'.format(issue.key)
        _issue.Summary = issue.fields.summary
        _issue.Description = issue.fields.description
        _issue.StoryPoint = issue_story_point
        _issue.Sprint = issue_sprint
        issues.append(_issue.__dict__)

    return jsonify(issues)


@app.route('/api/<issue_key>/UpdateStoryPoint', methods=['PUT'])
def update_story_point(issue_key):
    json_data = request.json

    issue = jira_client.issue(issue_key)
    issue.update(fields={customfield['story_point']: json_data['story_point']})

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
