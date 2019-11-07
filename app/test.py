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
    if issue.raw['key'] != None:
        # print(issue.fields.__dict__)
        active_sprint = re.findall(r"state=ACTIVE,name=[^,]*", str(issue.raw['fields'][customfield['sprint']]))
        future_sprint = re.findall(r"state=FUTURE,name=[^,]*", str(issue.raw['fields'][customfield['sprint']]))

        if active_sprint:
            issue_sprint = active_sprint[0].replace('state=ACTIVE,name=', '')
        elif future_sprint:
            issue_sprint = future_sprint[0].replace('state=FUTURE,name=', '')
        print(issue.raw)
        print(issue_sprint)
        print(issue.key)
