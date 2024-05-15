from flask import Blueprint, request, jsonify
from backend.v1.data.service import ingest_data

bp = Blueprint('data', __name__, url_prefix='/data')

@bp.route('/', methods=['POST'])
def ingest():
    data = request.get_json()
    email = data.get('email')

    # Process the chat message
    response_code = ingest_data(email)

    if response_code == 200:
        return jsonify({'message': 'Data ingested successfully'}), 200
    else:
        return jsonify({'message': 'Data ingestion failed'}), 500
