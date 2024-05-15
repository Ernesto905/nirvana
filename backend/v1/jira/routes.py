from flask import Blueprint, request, jsonify
from backend.v1.jira.service import generate_actions, execute_action

bp = Blueprint('jira', __name__, url_prefix='/jira')

@bp.route('/actions', methods=['POST'])
def actions():
    ...

@bp.route('/execute', methods=['POST'])
def execute():
    ...
