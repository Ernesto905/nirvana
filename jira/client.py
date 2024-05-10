import requests
import json

class JiraClient: 
    def __init__(self, cloud_id, access_token):
        self.cloud_id = cloud_id  
        self.access_token = access_token
        self.api_path = "/rest/api/2/project"


    def projects(self):
        url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/{self.api_path}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        return data








