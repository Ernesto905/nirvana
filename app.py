"""
Flask backend integrating JIRA, SQL, and Arctic all together
to serve as a RESTful API for the frontend to consume.

Endpoints:
/get-actions - Given an email and user ID, returns list of potential JIRA actions based on the user's
    current JIRA context.
/ingest - Given an email and user ID, extract any useful information from the user's email
    and store it in the SQL database for future analysis and use.
"""

from flask import Flask, request, jsonify

from llm.agents import (
    get_jira_actions,
    get_jira_api_call,
    extract_features
)

from SQL.manager import RdsManager

from jira.client import JiraClient

app = Flask(__name__)

def user_from_token(token: str) -> str:
    """Given a user's token, fetch their email."""
    ...

@app.route('/get-actions', methods=['GET'])
def get_actions() -> dict:
    """Given an email and user credentials, return a list of potential actions to take in JIRA."""
    tokens     = request.args.get('tokens')
    email_text = request.args.get('email_text')

    jira_token = tokens['jira']

    google_token = tokens['google']
    user_email = user_from_token(google_token)

    # get the user's current JIRA context (projects, issues, etc.)
    client: JiraClient  = ...
    context: dict       = ...

    actions: dict = get_jira_actions(email_text, context)

    return jsonify(actions)

@app.route('/ingest', methods=['POST'])
def ingest() -> int:
    """Given an email and user credentials, extract any useful information from the email and store it in the SQL database for future analysis."""
    tokens     = request.args.get('tokens')
    email_text = request.args.get('email_text')

    google_token = tokens['google']
    user_email   = user_from_token(google_token)

    db = RdsManager(...)
    # get the current database schema (every table and its columns, excluding metadata table and other non-data tables)
    schema = ...
    data   = extract_features(email_text, schema)

    for statement in data['extracted_information']:
        # execute the SQL statement
        try: 
            db.execute_sql(statement)
        except Exception as e:
            print(f"Error executing Arctic generated SQL.\nStatement: {statement}\nError: {str(e)}")
            return 500

    return 200

@app.route('/execute-jira', methods=['POST'])
def execute_jira() -> int:
    """Given a JIRA action (like from get_actions), execute it."""
    tokens = request.args.get('tokens')
    action = request.args.get('action')

    jira_token = tokens['jira']
    client: JiraClient = ...

    response = get_jira_api_call(client, action)
    api_call = response["api_call"]

    # execute the JIRA API call
    ...


if __name__ == '__main__':
    app.run(port=5000)