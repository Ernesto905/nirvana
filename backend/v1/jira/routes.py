from flask import Blueprint, request, jsonify
from backend.v1.jira.service import generate_actions, execute_action

jira_bp = Blueprint('jira', __name__, url_prefix='/jira')

@jira_bp.route('/actions', methods=['POST'])
def actions():
    ...

@jira_bp.route('/execute', methods=['POST'])
def execute():
    ...
