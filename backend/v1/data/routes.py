from flask import Blueprint, request, jsonify
from backend.v1.data.service import ingest_data
from backend.v1.auth import google_auth_required
from utils.gmail import address_from_creds

bp = Blueprint('data', __name__, url_prefix='/data')

@bp.route('/', methods=['POST'])
@google_auth_required
def ingest():
    """
    Given an email, remember useful information about the user for future insights.

    Expected Payload:
    - email: str with the user's email we are ingesting data for
    - google-auth-token: dict with user's google auth token
    """
    data = request.get_json()
    email = data.get('email')

    token = data.get('google-auth-token')
    user_email = address_from_creds(token)

    # Process the chat message
    try: 
        ingest_data(email, user_email)
        return jsonify({'response': 'Data ingested successfully'}), 200
    except Exception as e:
        return jsonify({'response': f'Data ingestion failed due to the following exception: {e}'}), 500