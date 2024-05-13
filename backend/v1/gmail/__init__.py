import os
import json
import base64
import requests
import functools
from dotenv import load_dotenv

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from flask import Blueprint, request, session, url_for, abort

bp = Blueprint('gmail', __name__, url_prefix='/gmail')

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
load_dotenv()

with open("credentials.json") as f:
    credentials_json = json.load(f)
    credentials_json["web"]["client_secret"] = os.environ["GMAIL_CLIENT_SECRET"]


def gmail_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'gmail_credentials' not in session:
            abort(401)
        if 'gmail_address' not in session:
            session['gmail_address'] = address_from_creds(session['gmail_credentials'])
        return view(**kwargs)
    return wrapped_view


@bp.route('/authorize', methods=('GET',))
def authorize():
    flow = Flow.from_client_config(credentials_json, SCOPES)
    flow.redirect_uri = url_for('.oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    session['gmail_state'] = state
    return authorization_url, 200


@bp.route('/oauth2callback', methods=('GET',))
def oauth2callback():
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Remove this later when we get https
    state = session['gmail_state']

    flow = Flow.from_client_config(credentials_json, SCOPES, state=state)
    flow.redirect_uri = url_for('.oauth2callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    session["gmail_credentials"] = credentials_to_dict(flow.credentials)
    return "You have successfully logged in. You can close this window.", 200


@bp.route('/revoke', methods=('GET',))
@gmail_login_required
def revoke():
    credentials = Credentials(**session['gmail_credentials'])

    revoke = requests.post(
        'https://oauth2.googleapis.com/revoke',
        params={'token': credentials.token},
        header={'content-type': 'application/x-www-form-urlencoded'}
    )
    status_code = getattr(revoke, 'status_code')
    if status_code != 200:
        return 'An error occured', status_code
    return 'Credentials successfully revoked', 200


@bp.route('/clear', methods=('GET', 'POST'))
def clear():
    if 'gmail_credentials' in session:
        del session['gmail_credentials']
    if 'gmail_state' in session:
        del session['gmail_state']
    if 'gmail_address' in session:
        del session['gmail_address']
    return "", 200


@bp.route('/messages', methods=('GET',))
@gmail_login_required
def messages():
    max_results = request.args.get('max_results', 10)
    page_number = request.args.get('page_number', 1)
    query = request.args.get('query', "")
    try:
        creds = Credentials(**session['gmail_credentials'])
        service = build("gmail", "v1", credentials=creds)

        # Get Email IDs
        results = (service.users().messages().list(
            userId="me", maxResults=max_results, q=query).execute())

        message_ids = results.get("messages", [])

        if not message_ids:
            print("No Emails found.")
            return []

        emails = []
        for message_id in message_ids:
            message_data = service.users().messages().get(
                userId="me", id=message_id["id"], format="full").execute()
            email_data = {}

            email_data["snippet"] = message_data.get("snippet", "")

            payload = message_data.get("payload", None)
            if not payload:
                continue

            for header in payload.get("headers", []):
                if header["name"] == "To":
                    email_data["to"] = remove_latex(header["value"])
                if header["name"] == "From":
                    email_data["from"] = remove_latex(header["value"])
                if header["name"] == "Subject":
                    email_data["subject"] = remove_latex(header["value"])

            email_data["body"] = get_body_text(payload)

            emails.append(email_data)
        return emails

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


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


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def get_body_text(payload: dict) -> str:
    if payload.get("mimeType", "") == "text/plain":
        if payload.get("body", {}).get("size") != 0:
            return remove_latex(decode_string(payload["body"]["data"]))
        else:
            return ""
    for part in payload.get("parts", []):
        data = get_body_text(part)
        if data:
            return data
    return ""


def decode_string(data: str, charset: str = "UTF8") -> str:
    data_binary = data.encode(charset) + b"=="
    decoded_binary = base64.urlsafe_b64decode(data_binary)
    return decoded_binary.decode(charset)


def remove_latex(data: str) -> str:
    return data.replace("$", "\\$")
