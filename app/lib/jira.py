from jira import JIRA


class JIRA(JIRA):
    """See class JIRA in jira"""

    def get_myself_user_profile(self):
        route_api = 'myself'
        user_profile_json = self._get_json(route_api)
        return user_profile_json