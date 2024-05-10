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
        print("\n\n\ndata is: ", data)
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
        print("\n\n\ndata is: ", data)
        return json.dumps(data)



    








