from flask import Blueprint
from flask import jsonify
from flask import request
from config import JIRA_URL
from services.jira_client import jira_client
from services.twist_fate import twistfate
from models.issue import Issue
from models.sprint import Sprint
from database.jirapoker_db import jirapoker_db

issue = Blueprint('issue', __name__)

# fields mapping is mainly used for custom field which can make the code more readable
fields_mapping = jira_client.get_fields_mapping()

# get issues
@issue.route('/api/issue/<board_name>/active-and-future-sprints', methods=['GET'])
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
            if fields_mapping['Story Points'] in _issue.raw['fields'].keys():
                issue_story_point = _issue.raw['fields'][fields_mapping['Story Points']]

            issue = Issue()
            issue.issueKey = _issue.key
            issue.url = JIRA_URL + '/browse/{}'.format(_issue.key)
            issue.iconUrl = _issue.fields.issuetype.iconUrl
            issue.issueType = _issue.fields.issuetype.name
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

# issue estimation
@issue.route('/api/issue/estimation-result', methods=['POST'])
def insert_issue_estimation_result():
    request_body = request.json

    user = jirapoker_db.user.find_one({'accountId': request_body['accountId']})
    estimation_record_of_issue_by_user = jirapoker_db.estimation_result.find_one({'issueKey': request_body['issueKey'],
                                                                                  'userId': user['_id']})
    if not estimation_record_of_issue_by_user:
        jirapoker_db.estimation_result.insert_one({'issueKey': request_body['issueKey'],
                                                   'userId': user['_id'],
                                                   'estimatedStoryPoint': request_body['estimatedStoryPoint']})
    else:
        estimation_record_of_issue_by_user.update({'estimatedStoryPoint': request_body['estimatedStoryPoint']})
        jirapoker_db.estimation_result.update_one({'_id': estimation_record_of_issue_by_user['_id']},
                                                  {'$set': estimation_record_of_issue_by_user})

    return "OK", 200


@issue.route('/api/issue/<issue_key>/estimation-results', methods=['GET'])
def get_issue_estimation_results(issue_key):
    issue_estimation_results = list(jirapoker_db.estimation_result.find({'issueKey': issue_key}, {'_id': False}))
    returned_issue_estimation_results = []
    for issue_estimation_result in issue_estimation_results:
        user = jirapoker_db.user.find_one({'_id': issue_estimation_result['userId']},
                                          {'_id': False})
        issue_estimation_result.pop('userId')
        issue_estimation_result['user'] = user
        returned_issue_estimation_results.append(issue_estimation_result)
    if True:
        returned_issue_estimation_results.append({'issueKey': issue_key,
                                                   'userId': twistfate.name,
                                                   'estimatedStoryPoint': twistfate.evaluate_story_point(issue_key)}
)


@issue.route('/api/issue/<issue_key>/estimation-results', methods=['DELETE'])
def delete_issue_estimation_results(issue_key):
    jirapoker_db.estimation_result.delete_many({'issueKey': issue_key})

    return "OK", 200

# issue story point
@issue.route('/api/issue/estimated-story-point/<issue_key>/<account_id>', methods=['GET'])
def get_issue_estimated_story_point(issue_key, account_id):
    user = jirapoker_db.user.find_one({'accountId': account_id})
    estimation_record_of_issue_by_user = jirapoker_db.estimation_result.find_one({'issueKey': issue_key,
                                                                                  'userId': user['_id']},
                                                                                 {'_id': False})
    if not estimation_record_of_issue_by_user:
        return ''
    estimated_story_point_by_user = estimation_record_of_issue_by_user['estimatedStoryPoint']
    return estimated_story_point_by_user, 200


@issue.route('/api/issue/story-point', methods=['PUT'])
def update_story_point_in_jira():
    request_body = request.json

    issue = jira_client.issue(request_body['issueKey'])
    issue.update(fields={fields_mapping['Story Points']: request_body['storyPoint']})

    return 'Update story point successfully', 200

# issue status
@issue.route('/api/issue/status', methods=['POST'])
def insert_issue_status():
    request_body = request.json
    issue_status_record = jirapoker_db.issue_status.find_one({'issueKey': request_body['issueKey']})
    if not issue_status_record:
        jirapoker_db.issue_status.insert_one(request_body)
    else:
        issue_status_record.update({'isRevealed': request_body['isRevealed']})
        jirapoker_db.estimation_result.update_one({'_id': issue_status_record['_id']},
                                                  {'$set': issue_status_record})

    return 'OK', 200


@issue.route('/api/issue/<issue_key>/status/<status_name>', methods=['GET'])
def get_issue_status(issue_key, status_name):
    issue_status_record = jirapoker_db.issue_status.find_one({'issueKey': issue_key})
    if not issue_status_record or issue_status_record[status_name] is False:
        return jsonify(False), 200
    return jsonify(True), 200

# maybe can be modified like above api
@issue.route('/api/issue/<issue_key>/status', methods=['DELETE'])
def delete_issue_status(issue_key):
    jirapoker_db.issue_status.remove({'issueKey': issue_key})

    return 'OK', 200

