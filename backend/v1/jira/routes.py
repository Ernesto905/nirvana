import os
import uuid
import redis
import secrets
import requests
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, url_for, redirect
from backend.v1.jira.service import generate_actions, execute_action
from backend.v1.auth import jira_auth_required
from jira import JiraClient

bp = Blueprint('jira', __name__, url_prefix='/jira')

load_dotenv()

redis_client = redis.Redis(host='redis-app', port=6379, db=0)


@bp.route('/authorize', methods=['GET'])
def authorize():
    scopes = ['read%3Ajira-work', 'manage%3Ajira-project', 'manage%3Ajira-configuration', 'write%3Ajira-work']
    state = secrets.token_urlsafe(16)

    authorization_url = f"""https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id={os.getenv('JIRA_CLIENT_ID')}&scope={scopes[0]}%20{scopes[1]}%20{scopes[2]}%20{scopes[3]}&redirect_uri={url_for('.oauth2callback', _external=True)}&state={state}&response_type=code&prompt=consent"""
    authorization_url = authorization_url.replace('flask-app', 'localhost')

    return {'authorization_url': authorization_url, 'state': state}


@bp.route('/oauth2callback', methods=['GET'])
def oauth2callback():
    data = request.get_json()
    code = data.get('code')
    token_url = 'https://auth.atlassian.com/oauth/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': os.getenv('JIRA_CLIENT_ID'),
        'client_secret': os.getenv('JIRA_CLIENT_SECRET'),
        'code': code,
        'redirect_uri': "http://localhost:8501"
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(token_url, json=data, headers=headers)
    response.raise_for_status()
    access_token = response.json()['access_token']

    id = str(uuid.uuid4())
    redis_client.set(id, access_token, ex=3600)
    return redirect(f"http://localhost:8501/?jira_uuid={id}")


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
