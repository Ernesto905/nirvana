from flask import Blueprint, request, jsonify
from backend.v1.chat.service import process_chat

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message')

    # Process the chat message
    response_message = process_chat(user_message)

    return jsonify({"response": response_message})
