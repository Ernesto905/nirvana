from flask import Blueprint, request, jsonify
from backend.v1.jira.service import generate_actions, execute_action
from backend.v1.auth import google_auth_required, jira_auth_required

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
    ...

@bp.route('/execute', methods=['POST'])
@jira_auth_required
def execute():
    """
    Expected Payload:
    - email: str with the email in question
    - action: dict with the action to be executed
    - jira-cloud-id: str with the jira cloud id
    - jira-auth-token: dict with the jira auth token
    """
    ...
