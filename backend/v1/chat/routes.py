from flask import Blueprint, request, jsonify
from backend.v1.chat.service import process_chat
from backend.v1.auth import google_auth_required
from backend.v1.gmail import address_from_creds

bp = Blueprint('chat', __name__, url_prefix='/chat')

@bp.route('/', methods=['POST'])
@google_auth_required
def chat():
    """
    Expected Payload:
    - message: str with the user's message
    - google-auth-token: dict with user's google auth token
    """
    data = request.get_json()

    user_message = data.get('message')

    token = data.get('google-auth-token')
    try:
        user_email = address_from_creds(token)
    except Exception as e:
        return jsonify({"response": str(e)}), 500

    try:
        user_message = user_message.strip()
        # Process the chat message
        response_message = process_chat(user_message, user_email)

        # print(response_message) # DEBUG

        return jsonify({"response": response_message}), 200
    except Exception as e:
        return jsonify({"response": str(e)}), 500