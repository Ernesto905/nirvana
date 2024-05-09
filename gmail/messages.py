import base64

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_messages(session, maxResults=10, page_number=1, query=""):
    try:
        service = build("gmail", "v1", credentials=session.creds)

        # Get Email IDs
        results = (service.users().messages().list(
            userId="me", maxResults=maxResults, q=query).execute())

        # print(results)
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
