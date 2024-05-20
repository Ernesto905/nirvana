import base64
import re

from gmail import get_gmail_credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_messages(gmail_uuid, session, maxResults=10, page_number=1, query=""):
    try:
        creds = get_gmail_credentials(gmail_uuid)
        service = build("gmail", "v1", credentials=creds)

        # Get Email IDs
        messages = service.users().messages()
        request = (
            messages.list(
                userId="me",
                maxResults=maxResults,
                q=query,
                includeSpamTrash=False
            )
        )

        count = 1
        results = None
        while request is not None and count < page_number:
            results = request.execute()
            request = messages.list_next(request, results)
            count += 1

        results = request.execute()
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
                if header["name"] == "Date":
                    email_data["date"] = parse_date(header["value"])

            email_data["body"] = get_body_text(payload)
            email_data["message_id"] = message_id

            pdf_ids = []
            get_pdf_attachment_ids(payload, pdf_ids)
            email_data["pdf_ids"] = pdf_ids

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


def get_gmail_address(session) -> str:
    """Given a user's token, fetch their email."""
    try:
        service = build("gmail", "v1", credentials=session.creds)

        # Get Email ID
        results = service.users().getProfile(userId="me").execute()
        return results.get("emailAddress", None)
    except HttpError as error:
        print(f"An error occured: {error}")
        return None


def get_pdf_attachment_ids(payload: dict, ids: list):
    if payload.get("mimeType", "") == "application/pdf":
        if payload.get("body", {}).get("size") != 0:
            ids.append(payload["body"]["attachmentId"])
    for part in payload.get("parts", []):
        get_pdf_attachment_ids(part, ids)


def get_pdf_attachment(service, message_id: str, payload: dict):
    pdf_ids = []
    get_pdf_attachment_ids(payload, pdf_ids)
    for pdf_id in pdf_ids:
        result = (
                service
                .users()
                .messages()
                .attachments()
                .get(
                    userId="me",
                    messageId=message_id,
                    id=pdf_id
                ).execute()
            )
        with open(f"temp/{pdf_id[:16]}.pdf", "wb") as f:
            f.write(base64.urlsafe_b64decode(result["data"]))
    return [id[:16] for id in pdf_ids]


def decode_string(data: str, charset: str = "UTF8") -> str:
    data_binary = data.encode(charset) + b"=="
    decoded_binary = base64.urlsafe_b64decode(data_binary)
    return decoded_binary.decode(charset)


def remove_latex(data: str) -> str:
    return data.replace("$", "\\$")


def parse_date(date: str) -> dict:
    expression = r"^(?P<day_of_week>\w{3}),\s+(?P<day>\d{1,2})\s+(?P<month>\w+)\s+(?P<year>\d+)\s+(?P<time>.*)$"
    search_result = re.search(expression, date)
    if not search_result:
        return {
            "day_of_week": "",
            "day": "",
            "month": "",
            "year": "",
            "time": ""
        }
    result = search_result.groupdict()
    result["day"] = int(result["day"])
    result["year"] = int(result["year"])
    return result
