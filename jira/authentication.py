import os
import secrets
import requests
from dotenv import load_dotenv

load_dotenv()

def authenticate_jira(session):
    get_authorization_url()


def get_authorization_url():
    scopes = ['read%3Ajira-work', 'manage%3Ajira-project', 'manage%3Ajira-configuration']
    state = secrets.token_urlsafe(16)

    authorization_url = f"""https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id={os.getenv('JIRA_CLIENT_ID')}&scope={scopes[0]}%20{scopes[1]}%20{scopes[2]}&redirect_uri={os.getenv('REDIRECT_URI')}&state={state}&response_type=code&prompt=consent"""

    return authorization_url, state

def get_access_token(code):
    token_url = 'https://auth.atlassian.com/oauth/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': os.getenv('JIRA_CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'code': code,
        'redirect_uri': "http://localhost:8501/Jira" 
    }

    headers = {
        'Content-Type': 'application/json'
    }

    print("data is: ", data)

    response = requests.post(token_url, json=data, headers=headers)
    print('---------')
    print("response is: ", response)
    print('---------')
    print("response text is: ", response.text)
    response.raise_for_status()
    access_token = response.json()['access_token']

    return access_token
