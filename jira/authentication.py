import os
import uuid
import redis
import secrets
import requests
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis(host='redis-app', port=6379, db=0)


def get_jira_authorization_url():
    scopes = ['read%3Ajira-work', 'manage%3Ajira-project', 'manage%3Ajira-configuration', 'write%3Ajira-work']
    state = secrets.token_urlsafe(16)

    authorization_url = f"""https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id={os.getenv('JIRA_CLIENT_ID')}&scope={scopes[0]}%20{scopes[1]}%20{scopes[2]}%20{scopes[3]}&redirect_uri={os.getenv('JIRA_REDIRECT_URI')}&state={state}&response_type=code&prompt=consent"""

    return authorization_url, state


def generate_jira_access_token(code):
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
    return id


def get_jira_access_token_and_cloudid(id):
    access_token = redis_client.get(id)
    if not access_token:
        return None, None
    access_token = access_token.decode('utf-8')
    resource_url = "https://api.atlassian.com/oauth/token/accessible-resources"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(resource_url, headers=headers)
    response.raise_for_status()

    # Bit of a misnomer. response_json type is actually a list
    response_json = response.json()

    return access_token, response_json[0]["id"]


def jira_access_token_exists(id):
    access_token = redis_client.get(id)
    return access_token is not None


def logout_jira(id):
    redis_client.delete(id)
