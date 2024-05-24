from flask import Blueprint, jsonify
from . import chat, data, gmail, actions

bp = Blueprint('v1', __name__, url_prefix='/v1')

bp.register_blueprint(gmail.bp)
bp.register_blueprint(actions.bp)
bp.register_blueprint(data.bp)
bp.register_blueprint(chat.bp)

@bp.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "UP", "message": "Flask is running!"}), 200