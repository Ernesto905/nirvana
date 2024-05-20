import os
import json
import uuid
import redis
import requests
from dotenv import load_dotenv

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from flask import Blueprint, request, session, url_for, redirect

bp = Blueprint('gmail', __name__, url_prefix='/gmail')

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
load_dotenv()

redis_client = redis.Redis(host='redis-app', port=6379, db=0)

credentials_json = {
    "web": {
        "client_id": os.getenv('GMAIL_CLIENT_ID'),
        "client_secret": os.getenv('GMAIL_CLIENT_SECRET'),
        "project_id": "artic-hackathon-2024",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": [
            "http://localhost:8501/",
        ]
    }
}


@bp.route('/authorize', methods=('GET',))
def authorize():
    flow = Flow.from_client_config(credentials_json, SCOPES)
    flow.redirect_uri = url_for('.oauth2callback', _external=True).replace('flask-app', 'localhost')
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    session['gmail_state'] = state
    return authorization_url, 200


@bp.route('/oauth2callback', methods=('GET',))
def oauth2callback():
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Remove this later when we get https

    flow = Flow.from_client_config(credentials_json, SCOPES)
    flow.redirect_uri = url_for('.oauth2callback', _external=True).replace('flask-app', 'localhost')

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    creds = flow.credentials.to_json()
    if 'token' in creds:
        id = str(uuid.uuid4())
        redis_client.set(id, creds, ex=3600)
        return redirect(f"http://localhost:8501/?gmail_uuid={id}")
    return redirect("http://localhost:8501/?google_error=True")


@bp.route('/revoke/<uuid:gmail_uuid>', methods=('GET', 'POST'))
def revoke(gmail_uuid):
    credentials = get_gmail_credentials(gmail_uuid)

    revoke = requests.post(
        'https://oauth2.googleapis.com/revoke',
        params={'token': credentials.token},
        header={'content-type': 'application/x-www-form-urlencoded'}
    )
    status_code = getattr(revoke, 'status_code')
    if status_code != 200:
        return 'An error occured', status_code
    return 'Credentials successfully revoked', 200


@bp.route('/clear/<gmail_uuid>', methods=('GET', 'POST'))
def clear(gmail_uuid):
    if request.method == 'POST':
        redis_client.delete(gmail_uuid)
    return "", 200


def address_from_creds(creds: dict) -> str:
    """Given a user's token, fetch their email."""
    try:
        service = build("gmail", "v1", credentials=Credentials(**creds))

        # Get Email ID
        results = service.users().getProfile(userId="me").execute()
        return results.get("emailAddress", None)
    except HttpError as error:
        print(f"An error occured: {error}")
        return None


def get_gmail_credentials(id):
    data = redis_client.get(id)
    data = json.loads(data) if data else None
    return Credentials.from_authorized_user_info(data) if data else None
