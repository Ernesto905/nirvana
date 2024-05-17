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
        Returns all jira projects as a python list 
        """
        url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/{self.project_api_path}"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        data = response.json()
        return data

    
    def get_all_issues(self):
        """
        Returns all issues in an account as a python dict 
        """
        url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/{self.search_api_path}"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        data = response.json()
        return data
    
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
    Below are the functions to create and update a jira issue. 

    Parameters: 
        project -> str : Key for our project. Only current project is "KAN" 
        summary -> str: Text recapping the issue 
        description -> str: A more in depth paragraph of the issue 
        assignee -> str: An ID associated with the assignee for this issue 
            to obtain by name, call get_userid_by_name("ernesto enriquez")
        priority -> str: An ID associated with the priority for this project 
            Currently allows for "Low", "Medium", "High", "Highest"
        due_date -> str: A date in the following form YYYY-MM-DD
        labels -> str[]: A list of strings, each indicating a lable
    """

    def create_issue(self, project, summary, description, assignee, priority, issue_type, due_date, labels):
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
                  "name": priority
                },
                "duedate": due_date,
                "issuetype": {
                    "name": issue_type
                }
            }
        })

        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()

        data = response.json()
        return json.dumps(data)

    def update_issue(self, issue, due_date, assignee, status, priority):
        """
        Updates a current jira issue with a due date, status, and priority.  
        issue parameter can be either an ID or the Name of the issue (also known as the "Key")
        """
        url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/{self.create_issue_path}/{issue}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        data = json.dumps({
            "fields": {
                "assignee": {
                    "id": assignee
                },
                "priority": {
                  "name": priority 
                },
                "duedate": due_date
            }
        })

        response = requests.put(url, headers=headers, data=data)
        if response.status_code != 204:
            response.raise_for_status()

        # Transition an issue to a new status
        self.transfer_issue(issue, status)

        return issue


    def transfer_issue(self, issue, status):
        """
        Transitions an issue to a new status. 
        Default statuses are TO DO, IN PROGRESS, and DONE.
        But more can be manually added. 
        """

        # Since status comes in a name form, we must convert it to an ID
        transitions_json = self.get_transitions()
        transition_as_id = self.get_transition_id_from_name(transitions_json, status)


        url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/{self.create_issue_path}/{issue}/transitions"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        data = json.dumps({
            "transition": {
                "id": transition_as_id
            } 
        })


        response = requests.post(url, headers=headers, data=data)
        print("Response is ", response)
        if response.status_code != 204:
            response.raise_for_status()


        return issue


    def get_transitions(self):
        """Get allowed transitions for an issue"""
        issue = "KAN-3"

        url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/{self.create_issue_path}/{issue}/transitions"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }



        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        return data

    def get_transition_id_from_name(self, transitions_json, status_name):
        """
        Retrieves the transition ID for a given status name.
        """
        for transition in transitions_json.get('transitions', []):
            if transition['name'] == status_name:
                return transition['id']
        return None
    


    
    """
    The following functions return the allowed parameters of a 
    jira ticket. For example, what priorities, statuses, users, etc.
    are allowed in the creation of a jira ticket.
    """

    def get_all_transition_names(self, transitions_json):
        """
        Extracts the names of all transitions from the JSON structure.
        """
        return [transition['name'] for transition in transitions_json.get('transitions', [])]


    def get_allowed_params(self): 
        """
        This function returns one big payload where, for each project, 
        it lists out 
            issues : []
            members : []
            labels : []
            priorities : []
            statuses : []

        return type: Python Dictionary
        """

        projects = [project['name'] for project in self.projects() if 'name' in project]
        # issues = 
        
    
        







