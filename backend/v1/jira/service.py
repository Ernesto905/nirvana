from backend.v1.llm import (
    get_jira_actions,
    get_jira_api_call
)

from jira import JiraClient

def generate_actions(email, client: JiraClient):
    ...

def execute_action(email, action, client: JiraClient):
    ...