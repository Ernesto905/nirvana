import requests
import json

class JiraClient: 
    def __init__(self, cloud_id, access_token):
        self.cloud_id = cloud_id  
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

        self.project_api_path = "rest/api/3/project"
        self.search_api_path = "rest/api/3/search"
        self.create_issue_path = "rest/api/3/issue"


    def projects(self):
        """
        Returns all jira projects
        """
        url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/{self.project_api_path}"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        data = response.json()
        return data

    
    def get_all_issues(self):
        url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/{self.search_api_path}"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        data = response.json()
        return json.dumps(data)
    
    def search_with_jql(self, jql):
        """
        Perform search with JQL-- Jira's inbuild query language. 
        This function returns a string.
        """

        url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/{self.search_api_path}"

        params = {
            "jql" : jql
        }

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        data = response.json()
        return json.dumps(data)

    def get_userid_by_name(self, name):
        """
        Takes in a user's name and performs a JQL search on it.
        This function returns a string.
        """
        payload = self.search_with_jql(f"assignee = \"{name}\"")
        json_data = json.loads(payload)
        user_id = json_data['issues'][0]['fields']['assignee']['accountId']
        return user_id

    """
    project -> Key for our project. Only current project is "KAN" 
    summary -> A string of text recapping the issue 
    description -> A more in depth paragraph of the issue 
    assignee -> An ID associated with the assignee for this issue 
        to obtain, call get_userid_by_name("ernesto enriquez")
    priority -> An ID associated with the priority for this project 
        Currently allows for "Low", "Medium", "High", "Highest"

    TODO:
    - update_issue(issue_key, summary, description, assignee, priority)
    - create_task(issue_key, summary, description, assignee, priority)
    - update_task(task_key, summary, description, assignee, priority)
    """

    def create_issue(self, project, summary, description, assignee, priority, issue_type):
        """
        Creates a jira issue of a given type and assign it to a given user.  
        """
        url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/{self.create_issue_path}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        data = json.dumps({
            "fields": {
                "project": {
                    "key": project 
                },
                "assignee": {
                    "id": assignee
                },
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description
                                }
                            ]
                        }
                    ]
                },
                "priority": {
                  "name": "Low"
                },
                "issuetype": {
                    "name": issue_type
                }
            }
        })

        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()

        data = response.json()
        return json.dumps(data)

    def update_issue(issue_key, summary, description, assignee, priority):
        pass

    def create_task(issue_key, summary, description, assignee, priority):
        pass

    def update_task(task_key, summary, description, assignee, priority):
        pass


    








