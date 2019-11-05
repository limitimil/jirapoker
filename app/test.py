from services.jira_client import jira_client
import re
from services.mapping import customfield


"""
project = jira_client.project('CTIS')
print(project.__dict__)
all_boards = jira_client.boards()
sprints = jira_client.sprints(248)
print(all_boards)
print(sprints)
for sprint in sprints:
    print(sprint.__dict__)

"""
project_issues = jira_client.search_issues('project=CTIS AND (SPRINT not in closedSprints() OR SPRINT in openSprints()) AND issuetype not in (Sub-task, 估點, Memo)', startAt=0, maxResults=False)
for issue in project_issues:
    if issue.raw['key'] == 'CTIS-1098' or issue.raw['key'] == 'CTIS-1299':
        # print(issue.fields.__dict__)
        print(issue.raw)
        sprint_name = re.findall(r"name=[^,]*", str(issue.raw['fields'][customfield['sprint']][0]))[0]
        sprint_name = sprint_name.replace('name=', '')
        print(sprint_name)
        print(issue.key)
