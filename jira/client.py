import requests
import json

class JiraClient: 
    def __init__(self, cloud_id, access_token):
        self.cloud_id = cloud_id  
        self.access_token = access_token

        self.project_api_path = "/rest/api/2/project"
        self.search_api_path = "/rest/api/2/search"


    def projects(self):
        url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/{self.project_api_path}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        return data
    
    def get_all_issues(self):
        url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/{self.search_api_path}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        return json.dumps(data)
    
    def search_with_jql(self, jql):
        url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/{self.search_api_path}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

        params = {
            "jql" : jql
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        return json.dumps(data)

    """
    We have access to the following functions to interact with the JIRA API:
    - create_issue(project, summary, description, assignee, priority)
    - update_issue(issue_key, summary, description, assignee, priority)
    - create_task(issue_key, summary, description, assignee, priority)
    - update_task(task_key, summary, description, assignee, priority)
    """

    def create_issue(self, project, summary, description, assignee, priority):
        """
        Creates an issue based on the following parameters 
            project -> An ID associated with a project 
            summary -> A string of text recapping the issue 
            description -> A more in depth paragraph of the issue 
            assignee -> An ID associated with the assignee for this issue 
            priority -> An ID associated with the priority for this project 
        """

        url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/{self.create_issue_path}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

        payload = json.dumps(
            {
                "fields": {
                    "assignee": {"id": assignee},
                    "components": [{"id": "10000"}],
                    "customfield_10000": "09/Jun/19",
                    "customfield_20000": "06/Jul/19 3:25 PM",
                    "customfield_30000": ["10000", "10002"],
                    "customfield_40000": {
                        "content": [
                            {
                                "content": [
                                    {"text": "Occurs on all orders", "type": "text"}
                                ],
                                "type": "paragraph",
                            }
                        ],
                        "type": "doc",
                        "version": 1,
                    },
                    "customfield_50000": {
                        "content": [
                            {
                                "content": [
                                    {
                                        "text": "Could impact day-to-day work.",
                                        "type": "text",
                                    }
                                ],
                                "type": "paragraph",
                            }
                        ],
                        "type": "doc",
                        "version": 1,
                    },
                    "customfield_60000": "jira-software-users",
                    "customfield_70000": ["jira-administrators", "jira-software-users"],
                    "customfield_80000": {"value": "red"},
                    "description": {
                        "content": [
                            {
                                "content": [
                                    {
                                        "text": description,
                                        "type": "text",
                                    }
                                ],
                                "type": "paragraph",
                            }
                        ],
                        "type": "doc",
                        "version": 1,
                    },
                    "duedate": "2019-05-11",
                    "environment": {
                        "content": [
                            {
                                "content": [{"text": "UAT", "type": "text"}],
                                "type": "paragraph",
                            }
                        ],
                        "type": "doc",
                        "version": 1,
                    },
                    "fixVersions": [{"id": "10001"}],
                    "issuetype": {"id": "10000"},
                    "labels": ["bugfix", "blitz_test"],
                    "parent": {"key": "PROJ-123"},
                    "priority": {"id": priority},
                    "project": {"id": str(project)},
                    "reporter": {"id": "5b10a2844c20165700ede21g"},
                    "security": {"id": "10000"},
                    "summary": summary,
                    "timetracking": {
                        "originalEstimate": "10",
                        "remainingEstimate": "5",
                    },
                    "versions": [{"id": "10000"}],
                },
                "update": {},
            }
        )

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        return json.dumps(data)

    def update_issue(issue_key, summary, description, assignee, priority):
        pass

    def create_task(issue_key, summary, description, assignee, priority):
        pass

    def update_task(task_key, summary, description, assignee, priority):
        pass


    








