import sys
print("PATH IS: ", sys.path)

import streamlit as st 
from gmail.authentication import login, logout
from jira.authentication import *
from jira.client import JiraClient

# Set page title and favicon
st.set_page_config(page_title="Nirvana", page_icon=":peace_symbol:")

# Custom CSS styles
st.markdown("""
    <style>
    body {
        background-color: #FFF0F5;
        font-family: serif;
    }
    .custom-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.4rem 0.8rem;
        background-color: white;
        color: #483434;
        text-decoration: none;
        border-radius: 0.65rem;
        font-weight: 400;
        transition: all 0.2s ease-in-out;
        font-family: serif;
        border: 1px solid #EDE0D4;
        cursor: pointer;
        font-size: 1rem;
        line-height: 1.5;
        text-transform: none;
        margin-right: 1rem;
    }
    .custom-button:hover {
        background-color: white;
        border-color: #483434;
    }
    .custom-button:active {
        background-color: white;
        border-color: #483434;
    }
    .custom-button:focus {
        outline: none;
        box-shadow: 0 0 0 0.2rem rgba(72, 52, 52, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# Authentication section
st.header("Nirvana")
st.write("Unifying Projects and Breaking Silos")
st.write("Seamlessly integrate emails, Jira, and SQL databases for streamlined project management.")

st.subheader("Authentication")
logged_in = st.session_state.get("logged_in", False)

col1, col2 = st.columns(2, gap="large")  # Adjust the column widths here

with col1:
    if not logged_in:
        login_button = st.button("Authenticate Google :key:")
        if login_button:
            # Perform login logic here
            login(st.session_state)
            st.rerun()
    else:
        logout_button = st.button("Logout from Google")
        if logout_button:
            logout(st.session_state)
            st.rerun()

with col2:
    if "access_token" not in st.session_state:
        if 'code' in st.query_params:
            authorization_code = st.query_params['code']
            st.query_params.clear()
            access_token = get_access_token(authorization_code)

            st.session_state['access_token'] = access_token
            auth = True
            st.rerun()
        else:
            authorization_url, state = get_authorization_url()
            st.session_state['auth_state'] = state

            # Display the button with custom styling
            button_html = f'<a href="{authorization_url}" target="_self"><button class="custom-button">Authenticate Jira :key:</button></a>'
            st.markdown(button_html, unsafe_allow_html=True)
    else:
        jira_inauth = st.button("Logout from Jira")
        if jira_inauth:
            del st.session_state["access_token"]
            del st.session_state["auth_state"]
            del st.session_state["JiraClient"]
            st.rerun()

if logged_in:
    st.success("Successfully authenticated with Google")

if "access_token" in st.session_state:
    st.success("Successfully authenticated with Jira")
