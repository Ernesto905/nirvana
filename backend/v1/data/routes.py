from flask import Blueprint, request, jsonify
from backend.v1.data.service import ingest_data

bp = Blueprint('data', __name__, url_prefix='/data')

@bp.route('/', methods=['POST'])
def ingest():
    data = request.get_json()
    email = data.get('email')

    # Process the chat message
    try: 
        ingest_data(email)
        return jsonify({'status': 200, 'response': 'Data ingested successfully'})
    except Exception as e:
        return jsonify({'status': 500, 'response': f'Data ingestion failed due to the following exception: {e}'})