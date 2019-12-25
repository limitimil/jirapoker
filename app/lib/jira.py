from jira import JIRA


class JIRA(JIRA):
    """See class JIRA in jira"""

    def get_myself_user_profile(self):
        route_api = 'myself'
        user_profile_json = self._get_json(route_api)
        return user_profile_json

    def get_user(self, account_id):
        route_api = 'user'
        query = {
           'accountId': account_id
        }
        user_json = self._get_json(route_api, params=query)
        return user_json

    def get_sprints_in_board(self, board_name):
        boards = self.boards(name=board_name)
        if not boards:
            raise RuntimeError('No board with name: {}'.format(board_name))
        board_id = boards[0].id
        sprints = self.sprints(board_id=board_id, maxResults=False)
        return sprints

    def get_active_and_future_sprint_names_in_board(self, board_name):
        sprints = self.get_sprints_in_board(board_name)
        sprint_names = []
        for sprint in sprints:
            if sprint.state in ['active', 'future']:
                sprint_names.append(sprint.name)
        return sprint_names
