import os
# Logger
_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LOG_CONFIG = os.path.join(_PATH, 'logging.ini')

# Jira auth
JIRA_URL = 'https://cybersoft4u.atlassian.net'
JIRA_USER = 'xxx'
JIRA_TOKEN = 'xxx'

# Mongo db connection
MONGO_URI = 'mongodb://localhost:27017'
DATABASE_NAME = 'jirapoker'