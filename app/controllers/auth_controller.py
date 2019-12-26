from flask import Blueprint
from flask import request
from flask import jsonify
from lib.jira import JIRA
from config import JIRA_URL
from models.user import User
from database.jirapoker_db import jirapoker_db

auth = Blueprint('auth', __name__)


@auth.route("/api/auth/sign-in", methods=['POST'])
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
        # insert_one will return _id which can not be serialized
        user.__dict__.pop('_id')
    return jsonify(user.__dict__)