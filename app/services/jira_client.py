from lib.jira import JIRA
import config

jira_client = JIRA(config.JIRA_URL,
                   basic_auth=(config.JIRA_USER, config.JIRA_TOKEN),
                   options={'server': "URLHERE",
                            'agile_rest_path': 'agile'})

