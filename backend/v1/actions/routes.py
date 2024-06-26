from flask import Blueprint, request, jsonify
from backend.v1.actions.service import generate_actions, execute_action, JiraClient
from backend.v1.auth import jira_auth_required

bp = Blueprint('actions', __name__, url_prefix='/actions')

@bp.route('/get', methods=['POST'])
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
        return jsonify({"error": f"Jira authentic error: {e}"}), 401

    try:
        actions = generate_actions(email, jc)
    except Exception as e:
        return jsonify({"error": f"Error generating actions: {e}"}), 500

    return jsonify({"actions": actions}), 200

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
        return jsonify({"error": f"Jira authentic error: {e}"}), 401

    try:
        execute_action(action, jc)
    except Exception as e:
        return jsonify({"error": f"Error executing action: {e}"}), 500

    return jsonify({"message": "Action executed successfully"}), 200
