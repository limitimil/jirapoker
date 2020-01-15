from flask import Blueprint
from flask import jsonify
from flask import request
from config import JIRA_URL
from services.jira_client import jira_client
from models.issue import Issue
from models.sprint import Sprint
from database.jirapoker_db import jirapoker_db
from bson.objectid import ObjectId

game = Blueprint('game', __name__)

@game.route('/api/game/create', methods=['POST'])
def create_game():
    request_body = request.json

    result = jirapoker_db.game.insert_one(request_body)
    return str(result.inserted_id), 200

@game.route('/api/game/get/<id>', methods=['GET'])
def get_game(id):
    result = jirapoker_db.game.find_one({'_id':ObjectId(id)})
    return str(result), 200
