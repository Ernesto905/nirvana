from flask import Blueprint, request, jsonify
from backend.v1.jira.service import generate_actions, execute_action
from backend.v1.auth import jira_auth_required
from jira import JiraClient

bp = Blueprint('jira', __name__, url_prefix='/jira')

@bp.route('/actions', methods=['POST'])
@jira_auth_required
def actions():
    """
    Expected Payload:
    - email: str with the email in question
    - jira-cloud-id: str with the jira cloud id
    - jira-auth-token: dict with the jira auth token
    """
    data = request.get_json()
    email = data.get('email')
    jira_cloud_id = data.get('jira-cloud-id')
    jira_auth_token = data.get('jira-auth-token')
    try:
        jc = JiraClient(jira_cloud_id, jira_auth_token)
    except Exception as e:
        return jsonify({"status": 401, "error": f"Jira authentic error: {e}"})

    try:
        actions = generate_actions(email, jc)
    except Exception as e:
        return jsonify({"status": 500, "error": f"Error generating actions: {e}"})

    return jsonify({"status": 200, "actions": actions})

@bp.route('/execute', methods=['POST'])
@jira_auth_required
def execute():
    """
    Expected Payload:
    - action: dict with the action to be executed
    - jira-cloud-id: str with the jira cloud id
    - jira-auth-token: dict with the jira auth token
    """
    data = request.get_json()
    action = data.get('action')
    jira_cloud_id = data.get('jira-cloud-id')
    jira_auth_token = data.get('jira-auth-token')

    try:
        jc = JiraClient(jira_cloud_id, jira_auth_token)
    except Exception as e:
        return jsonify({"status": 401, "error": f"Jira authentic error: {e}"})

    try:
        execute_action(action, jc)
    except Exception as e:
        return jsonify({"status": 500, "error": f"Error executing action: {e}"})

    return jsonify({"status": 200, "message": "Action executed successfully"})
