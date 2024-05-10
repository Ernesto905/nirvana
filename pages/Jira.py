import streamlit as st
from jira.authentication import *
from jira.client import JiraClient

# Check if the user has already authenticated
if 'access_token' not in st.session_state:
    if 'auth_state' not in st.session_state or 'code' in st.query_params:
        if 'code' in st.query_params:
            authorization_code = st.query_params['code']
            st.query_params.clear()
            access_token = get_access_token(authorization_code)

            st.session_state['access_token'] = access_token

            st.rerun()
        else:
            authorization_url, state = get_authorization_url()
            st.session_state['auth_state'] = state
            st.markdown(f'<a href="{authorization_url}" target="_self">Click here to authenticate with Jira</a>', unsafe_allow_html=True)
    else:
        st.warning("Redirecting now...")

else:
    st.success("Successfully Authenticated")
    access_token = st.session_state['access_token']
    cloud_id = get_cloudid(access_token)

    st.session_state.JiraClient = JiraClient(cloud_id, access_token)





