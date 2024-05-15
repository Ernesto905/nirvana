from flask import Blueprint, request, jsonify
from backend.v1.chat.service import process_chat

bp = Blueprint('chat', __name__, url_prefix='/chat')

@bp.route('/', methods=['POST'])
def chat():
    data = request.get_json()
    print(data)
    user_message = data.get('message')

    try:
        user_message = user_message.strip()
        # Process the chat message
        response_message = process_chat(user_message)

        return jsonify({"status": 200, "response": response_message})
    except Exception as e:
        return jsonify({"status": 500, "response": str(e)})