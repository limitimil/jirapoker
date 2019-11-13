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
"""
project_issues = jira_client.search_issues('project=CTIS AND (SPRINT not in closedSprints() OR SPRINT in openSprints()) AND issuetype not in (Sub-task, 估點, Memo)', startAt=0, maxResults=False)
for issue in project_issues:
    print(issue.fields.sprint.name)
"""
a = {1: [2, 3, 4]}
for key in a.keys():
    for value in a[key]:
        value = 5

print(a)