"""
Flask backend integrating JIRA, SQL, and Arctic all together
to serve as a RESTful API for the frontend to consume.

Endpoints:
/get-actions - Given an email and user ID, returns list of potential JIRA actions based on the user's
    current JIRA context.
/ingest - Given an email and user ID, extract any useful information from the user's email
    and store it in the SQL database for future analysis and use.
"""

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY='dev')

    from . import v1
    app.register_blueprint(v1.bp)

    return app