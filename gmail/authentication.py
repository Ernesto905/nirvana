import json
import redis

from google.oauth2.credentials import Credentials

redis_client = redis.Redis(host='redis-app', port=6379, db=0)


def get_gmail_credentials(id):
    data = redis_client.get(id)
    data = json.loads(data) if data else None
    return Credentials.from_authorized_user_info(data) if data else None


def gmail_credentials_exists(id):
    data = redis_client.get(id)
    return data is not None
