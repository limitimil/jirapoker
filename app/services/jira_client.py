from lib.jira import JIRA
from config import JIRA_URL
from config import JIRA_USER
from config import JIRA_TOKEN

jira_client = JIRA(JIRA_URL, basic_auth=(JIRA_USER, JIRA_TOKEN), options={'server': "URLHERE",
                                                                          'agile_rest_path': 'agile'})

