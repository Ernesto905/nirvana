import streamlit as st
import requests
import redis

def check_flask_health():
    try:
        response = requests.get("http://flask-app:5000/v1/health")
        print(response.text)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, None
    except requests.exceptions.RequestException as e:
        return False, str(e)

def check_redis_health():
    try:
        redis_client = redis.StrictRedis(host='redis-app', port=6379, db=0)  # Adjust host and port if necessary
        redis_client.ping()
        return True, "Redis server is alive!"
    except Exception as e:
        return False, str(e)

st.title('Service Connection Test')

if st.button('Test Flask Connection'):
    success, result = check_flask_health()
    if success:
        st.success(f"Success! Response: {result}")
    else:
        st.error(f"Failed to connect to Flask. Error: {result}")

if st.button('Test Redis Connection'):
    success, result = check_redis_health()
    if success:
        st.success(f"Success! {result}")
    else:
        st.error(f"Failed to connect to Redis. Error: {result}")
