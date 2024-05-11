import base64
import re

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_messages(session, maxResults=10, page_number=1, query=""):
    try:
        service = build("gmail", "v1", credentials=session.creds)

        page_id = get_page_id(service, session, maxResults, page_number, query)

        # Get Email IDs
        results = (
            service
            .users()
            .messages()
            .list(
                userId="me",
                maxResults=maxResults,
                q=query,
                pageToken=page_id,
                includeSpamTrash=False
            ).execute()
        )

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

            emails.append(email_data)
        return emails

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


def get_page_id(service, session, maxResults, page_number, query):
    if page_number == 1:
        return ""

    email_pages = session.get("email_pages", {})
    page_id = email_pages.get((maxResults, page_number), "")
    if len(page_id):
        return page_id

    try:
        counter = 1
        prev_page_id = ""
        while counter != page_number:
            prev_page_id = page_id
            page_id = email_pages.get((maxResults, counter), None)
            if page_id:
                counter += 1
                continue

            results = (
                service
                .users()
                .messages()
                .list(
                    userId="me",
                    maxResults=maxResults,
                    q=query,
                    pageToken=prev_page_id,
                    includeSpamTrash=False
                ).execute()
            )

            page_id = results.get("nextPageToken")
            email_pages[(maxResults, counter)] = page_id
            counter += 1
        return page_id
    except HttpError as error:
        print(f"An error occurred: {error}")
        return ""


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


def parse_date(date: str) -> dict:
    expression = r"^(?P<day_of_week>\w{3}),\s+(?P<day>\d{1,2})\s+(?P<month>\w+)\s+(?P<year>\d+)\s+(?P<time>.*)$"
    search_result = re.search(expression, date)
    if not search_result:
        return {}
    result = search_result.groupdict()
    result["day"] = int(result["day"])
    result["year"] = int(result["year"])
    return result
