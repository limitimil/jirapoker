from models.user import User
from models.Issue import Issue

import enum

class GameStatus(enum.Enum):
    Start = 1
    Over = 0

class Game:
    def __init__(self, host, participants=[], issues=[]):
        self.host = host
        self.participants = participants
        self.issues = issues
        self.status = GameStatus.Start
