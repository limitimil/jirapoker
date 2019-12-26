import os
# Logger
_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LOG_CONFIG = os.path.join(_PATH, 'logging.ini')

# Jira auth
JIRA_URL = 'https://cybersoft4u.atlassian.net'
JIRA_USER = os.environ['JIRA_USER']
JIRA_TOKEN = os.environ['JIRA_TOKEN']

# Mongo db connection
MONGO_HOST_NAME = os.environ['MONGO_HOST_NAME']
MONGO_URI = 'mongodb://{hostname}:27017'.format(hostname=MONGO_HOST_NAME)
DATABASE_NAME = os.environ['MONGO_DB_NAME']