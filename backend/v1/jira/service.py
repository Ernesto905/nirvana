from backend.v1.llm import dict_to_str
from backend.v1.llm import generate_actions as ga
import json
from jira import JiraClient

def generate_actions(email: str, client: JiraClient):
    context = client.get_allowed_params()
    context = json.loads(context)

    funcs = """
        ["name: create_issue
        required params: project, summary, priority
        optional params: description, assignee, duedate",
        "name: update_issue
        required params: issue
        optional params: due_date, assignee, status, priority"]
        """

    actions = ga(email, context, funcs)

    return actions

def execute_action(action, client: JiraClient):

    try:
        eval("client." + action)
    except Exception as e:
        raise Exception(f"Error executing action during eval step: {e}")

    return
