import os
from flask import Flask, request, jsonify
from backend import create_app
# from llm.wrappers import (
#     get_jira_actions,
#     get_jira_api_call,
#     extract_features
# )
from SQL.manager import RdsManager
from jira.client import JiraClient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = create_app()

def user_from_token(creds: dict) -> str:
    """Given a user's token, fetch their email."""
    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().getProfile(userId="me").execute()
        return results.get("emailAddress", "")
    except HttpError as error:
        print(f"An error occurred: {error}")
        return ""

@app.route('/get-actions', methods=['GET'])
def get_actions() -> dict:
    tokens = request.args.get('tokens')
    email_text = request.args.get('email_text')

    jira_token = tokens['jira']
    google_token = tokens['google']
    user_email = user_from_token(google_token)

    client: JiraClient = ...
    context: dict = ...

    actions: dict = get_jira_actions(email_text, context)
    return jsonify(actions)

@app.route('/ingest', methods=['POST'])
def ingest() -> int:
    tokens = request.args.get('tokens')
    email_text = request.args.get('email_text')

    google_token = tokens['google']
    user_email = user_from_token(google_token)

    db = RdsManager(...)
    schema = ...
    data = extract_features(email_text, schema)

    for statement in data['extracted_information']:
        try:
            db.execute_sql(statement)
        except Exception as e:
            print(f"Error executing Arctic generated SQL.\nStatement: {statement}\nError: {str(e)}")
            return 500

    return 200

@app.route('/execute-jira', methods=['POST'])
def execute_jira() -> int:
    tokens = request.args.get('tokens')
    action = request.args.get('action')

    jira_token = tokens['jira']
    client: JiraClient = ...

    response = get_jira_api_call(client, action)
    api_call = response["api_call"]

    # execute the JIRA API call
    ...

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "UP", "message": "Flask is running!"}), 200

if __name__ == "__main__":
    app.run(port=5000)
