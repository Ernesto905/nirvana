import requests
import json

def get_all_projects(cloud_id, access_token):
    """
    Returns all jira projects associated with an account
    This function returns a JSON formatted string.
    """
    url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/project"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    return data

def get_all_issues(cloud_id, access_token):
    """
    Returns all jira issues associated with an account
    This function returns a JSON formatted string.
    """
    url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/search"

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    return json.dumps(data)


def search_with_jql(cloud_id, access_token, jql):
    """
    Perform search with JQL-- Jira's inbuild query language. 
    This function returns a JSON formatted string.
    """

    url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/{self.search_api_path}"

    params = {
        "jql" : jql
    }

    response = requests.get(url, headers=self.headers, params=params)
    response.raise_for_status()

    data = response.json()
    return json.dumps(data)
