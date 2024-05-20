import os
import json

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
load_dotenv()


def login(session):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            with open("credentials.json") as f:
                credentials_json = json.load(f)
                credentials_json["web"]["client_secret"] = os.environ["GMAIL_CLIENT_SECRET"]
            flow = InstalledAppFlow.from_client_config(credentials_json, SCOPES)
            creds = flow.run_local_server(port=8502, authorization_prompt_message="")

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # Update streamlit session
    session.logged_in = True
    session.creds = creds


def logout(session):
    session.creds = None
    if os.path.exists("token.json"):
        os.remove("token.json")
    session.logged_in = False
