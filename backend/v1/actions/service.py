from backend.v1.llm import generate_actions as ga
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
        return data

    def get_userid_by_name(self, name):
        """
        Takes in a user's name and performs a JQL search on it.
        This function returns a string.
        """
        payload = self.search_with_jql(f"assignee = \"{name}\"")
        print("1")
        # json_data = json.loads(payload)
        json_data = payload
        print("2")
        user_id = json_data['issues'][0]['fields']['assignee']['accountId']
        print("3")
        user_id = user_id
        print("4")
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

    def create_issue(self, project, summary, description=None, assignee=None, priority=None, issue_type=None, due_date=None, labels=None):
        """
        Creates a jira issue of a given type and assign it to a given user.
        """
        url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/{self.create_issue_path}"

        print("\n\n\nIM HERE!!!!!!!!\n\n")
        print("Project is ", project)
        project = self.get_project_key_by_name(project)

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        data = {
            "fields": {
                "project": {
                    "key": project
                },
                "summary": summary
            }
        }

        if description:
            data["fields"]["description"] = {
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
            }

        if assignee:
            data["fields"]["assignee"] = {
                "id": assignee
            }

        if priority:
            data["fields"]["priority"] = {
                "name": priority
            }

        if due_date:
            data["fields"]["duedate"] = due_date

        if issue_type:
            data["fields"]["issuetype"] = {
                "name": issue_type
            }

        if labels:
            data["fields"]["labels"] = labels

        response = requests.post(url, headers=headers, json=data)
        print(f"\n\n{response.text}")
        response.raise_for_status()

        return response.json()


    def update_issue(self, issue, due_date=None, assignee=None, status=None, priority=None):
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

        data = {
            "fields": {}
        }

        if assignee:
            data["fields"]["assignee"] = {
                "id": assignee
            }

        if priority:
            data["fields"]["priority"] = {
                "name": priority
            }

        if due_date:
            data["fields"]["duedate"] = due_date

        response = requests.put(url, headers=headers, json=data)
        print(response.text)
        if response.status_code != 204:
            response.raise_for_status()

        # Transition an issue to a new status
        if status:
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
        Extract and structure important issue data for all projects as a single JSON structure.

        Returns:
            str: JSON string containing structured data on projects and associated issues.
        """
        projects = self.projects()  
        output = {}

        for project in projects:
            project_name = project['name']
            project_data = {
                "issues": [],
                "members": set(),
                "labels": set(),
                "priorities": set()
            }

            # Extract issues for each project using JQL or an appropriate method
            project_issues = self.search_with_jql(f'project = "{project_name}"')
            for issue in project_issues['issues']:
                assignee_data = issue['fields'].get('assignee')
                simplified_issue = {
                    "id": issue.get('id'),
                    "key": issue.get('key'),
                    "summary": issue['fields'].get('summary', 'No summary provided'),
                    "status": issue['fields'].get('status', {}).get('name', 'Unknown status'),
                    "duedate": issue['fields'].get('duedate', 'No due date'),
                    "assignee": {
                        "name": assignee_data.get('displayName', 'Unassigned') if assignee_data else 'Unassigned',
                        "email": assignee_data.get('emailAddress', 'No email available') if assignee_data else 'No email available'
                    }
                }
                project_data['issues'].append(simplified_issue)

                if assignee_data:
                    project_data['members'].add(assignee_data['displayName'])

                project_data['labels'].update(issue['fields'].get('labels', []))
                if issue['fields'].get('priority'):
                    project_data['priorities'].add(issue['fields']['priority']['name'])

            project_data['members'] = list(project_data['members'])
            project_data['labels'] = list(project_data['labels'])
            project_data['priorities'] = list(project_data['priorities'])

            output[project_name] = project_data

        return json.dumps(output)

    def get_project_key_by_name(self, project_name):
        projects = self.projects()

        for project in projects:
            if project['name'] == project_name:
                return project['key']

        return None

def generate_actions(email: str, client: JiraClient):
    context = client.get_allowed_params()
    context = json.loads(context)

    funcs = """
        ["name: create_issue
        required params: project, summary, priority
        optional params: description, assignee, due_date",
        "name: update_issue
        required params: issue
        optional params: due_date, assignee, status, priority"]
        """

    actions = ga(email, context, funcs)

    return actions

def execute_action(action, client: JiraClient):

    try:
        print("\n\nTrying eval", f"client.{action}")
        eval("client." + action)
        print("Did eval!")
    except Exception as e:
        print(e)
        raise Exception(f"Error executing action during eval step: {e}")

    return