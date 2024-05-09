import streamlit as st
from jira.authentication import get_authorization_url, get_access_token

# Check if the user has already authenticated
if 'access_token' not in st.session_state:
    authorization_url, state = get_authorization_url()

    auth_button = st.link_button("Authenticate Jira", authorization_url)

    if auth_button:
        st.session_state['auth_state'] = state

else:
    st.success("Successfully Authenticated")
    access_token = st.session_state['access_token']

if 'code' in st.query_params:
    authorization_code = st.query_params['code']
    access_token = get_access_token(authorization_code)

    st.session_state['access_token'] = access_token
    st.query_params.clear()

    st.rerun()


