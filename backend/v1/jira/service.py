from backend.v1.llm import (
    generate_actions,
    dict_to_str
)

from jira import JiraClient

def generate_actions(email: str, client: JiraClient):
    context = client.get_allowed_params()
    context = dict_to_str(context)

    actions = generate_actions(email, context)

    return actions

def execute_action(action, client: JiraClient):
    context = client.get_allowed_params()
    context = dict_to_str(context)

    try:
        eval("client." + action)
    except Exception as e:
        raise Exception(f"Error executing action during eval step: {e}")

    return
