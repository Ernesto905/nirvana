import os
import uuid
import json
import redis
import requests

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

load_dotenv()

HOST = os.getenv('HOST')

credentials_json = {
    "web": {
        "client_id": os.getenv('GMAIL_CLIENT_ID'),
        "client_secret": os.getenv('GMAIL_CLIENT_SECRET'),
        "project_id": "artic-hackathon-2024",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": [
            "http://localhost/",
            "http://127.0.0.1/"
        ]
    }
}

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

redis_client = redis.Redis(host='redis-app', port=6379, db=0)


def get_gmail_auth_url():
    flow = Flow.from_client_config(credentials_json, SCOPES)
    flow.redirect_uri = HOST
    authorization_url, state = flow.authorization_url()
    return authorization_url, state


def generate_gmail_access_token(state, response_params):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Remove this later when we get https

    # Add state back to client config
    flow = Flow.from_client_config(credentials_json, SCOPES)
    flow.redirect_uri = HOST

    authorization_response = f'{HOST}?state={response_params["state"]}&code={response_params["code"]}&state={response_params["scope"]}'
    try:
        flow.fetch_token(authorization_response=authorization_response)
    except Exception as e:
        print(e, flush=True)
        return None

    id = str(uuid.uuid4())
    redis_client.set(id, flow.credentials.to_json(), ex=3600)
    return id


def logout_gmail(id):
    redis_client.delete(id)


def get_gmail_credentials(id):
    data = redis_client.get(id)
    data = json.loads(data) if data else None
    return Credentials.from_authorized_user_info(data) if data else None


def gmail_credentials_exists(id):
    data = redis_client.get(id)
    return data is not None
