from flask import Blueprint
from flask import jsonify
from database.jirapoker_db import jirapoker_db

user = Blueprint('user', __name__)


@user.route('/api/user/<account_id>/estimated-issue-keys', methods=['GET'])
def get_user_estimated_issues(account_id):
    user = jirapoker_db.user.find_one({'accountId': account_id})
    user_estimated_issues = list(jirapoker_db.estimation_result.find({'userId': user['_id']}, {'_id': False}))
    user_estimated_issue_keys = {}
    for user_estimated_issue in user_estimated_issues:
        user_estimated_issue_keys[user_estimated_issue['issueKey']] = True
    return jsonify(user_estimated_issue_keys)


@user.route('/api/user/<user_name>/avatar-url', methods=['GET'])
def get_user_avatar_url(user_name):
    queried_user = jirapoker_db.user.find_one({'userName': user_name})
    if not queried_user:
        return '', 200
    else:
        return queried_user['avatarUrl'], 200
