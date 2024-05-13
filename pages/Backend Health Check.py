import streamlit as st
import requests

def check_flask_health():
    try:
        response = requests.get("http://flask-app:5000/health")
        print(response.text)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, None
    except requests.exceptions.RequestException as e:
        return False, str(e)

st.title('Flask Connection Test')

if st.button('Test Flask Connection'):
    success, result = check_flask_health()
    if success:
        st.success(f"Success! Response: {result}")
    else:
        st.error(f"Failed to connect to Flask. Error: {result}")
