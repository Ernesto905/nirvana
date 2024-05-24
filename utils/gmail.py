from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def address_from_creds(creds: dict) -> str:
    """Given a user's token, fetch their email."""
    # try:
    #     service = build("gmail", "v1", credentials=Credentials(**creds))

    #     # Get Email ID
    #     results = service.users().getProfile(userId="me").execute()
    #     return results.get("emailAddress", None)
    # except HttpError as error:
    #     print(f"An error occured: {error}")
    #     return None
    raise NotImplementedError