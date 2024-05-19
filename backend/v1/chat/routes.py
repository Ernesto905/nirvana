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
    user_email = address_from_creds(token)

    try:
        user_message = user_message.strip()
        # Process the chat message
        response_message = process_chat(user_message, user_email)

        # print(response_message) # DEBUG

        return jsonify({"status": 200, "response": response_message})
    except Exception as e:
        return jsonify({"status": 500, "response": str(e)})