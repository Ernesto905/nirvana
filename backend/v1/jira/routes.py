from flask import Blueprint, request, jsonify
from backend.v1.jira.service import get_all_projects, get_all_issues
import requests 

bp = Blueprint('jira', __name__, url_prefix='/jira')

/jira/get-projects <- Get 


@bp.route('get-projects', method=['GET'])
def get_all_issues():
    access_token = resquest.headers.get('Authorization')
    cloud_id = request.headers.get('X-Cloud-ID')

    if not access_token or cloud_id:
        return jsonify({'error': 'Missing authentication token or cloud ID'}), 401

    return get_all_projects(access_token, cloud_id)

@bp.route('get-issues', method=['GET'])
def get_all_issues():
    access_token = resquest.headers.get('Authorization')
    cloud_id = request.headers.get('X-Cloud-ID')

    if not access_token or cloud_id:
        return jsonify({'error': 'Missing authentication token or cloud ID'}), 401

    return get_all_issues(access_token, cloud_id)
