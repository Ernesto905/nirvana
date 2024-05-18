import sys
import time
import streamlit as st
from gmail import logout_gmail, get_gmail_auth_url, generate_gmail_access_token, gmail_credentials_exists
from jira import logout_jira, get_jira_authorization_url, get_jira_access_token_and_cloudid, jira_access_token_exists, generate_jira_access_token
from streamlit_cookies_controller import CookieController

# Set page title and favicon
st.set_page_config(page_title="Nirvana", page_icon=":peace_symbol:")

cookie_controller = CookieController()

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

gmail_uuid = None
jira_uuid = None
try:
    gmail_uuid = cookie_controller.get('gmail_uuid')
    jira_uuid = cookie_controller.get('jira_uuid')
except TypeError:
    pass


col1, col2 = st.columns(2, gap="large")  # Adjust the column widths here

scope = st.query_params.get('scope')
gmail_clicked = False
if scope and 'google' in scope:
    gmail_clicked = True
code = st.query_params.get('code')
jira_clicked = False
if code and not scope:
    print("here3", file=sys.stderr, flush=True)
    jira_clicked = True

with col1:
    if not gmail_uuid or not gmail_credentials_exists(gmail_uuid):
        if gmail_clicked:
            state = cookie_controller.get('gmail_state')
            response_params = {
                "state": st.query_params.get('state'),
                "code": st.query_params.get('code'),
                "scope": st.query_params.get('scope')
            }
            id = generate_gmail_access_token(response_params['state'], response_params)
            if id:
                cookie_controller.set('gmail_uuid', id)
                time.sleep(0.1)
            st.query_params.clear()
            st.rerun()
        else:
            gmail_auth_url, gmail_state = get_gmail_auth_url()
            button_html = f'<a href="{gmail_auth_url}" target="_self"><button class="custom-button">Authenticate Google :key:</button></a>'
            st.markdown(button_html, unsafe_allow_html=True)
            if gmail_state:
                cookie_controller.set('gmail_state', gmail_state)
                time.sleep(0.1)
    else:
        logout_button = st.button("Logout from Google")
        if logout_button:
            logout_gmail(gmail_uuid)
            cookie_controller.remove('gmail_uuid')
            time.sleep(0.1)
            st.rerun()

with col2:
    if not jira_uuid or not jira_access_token_exists(jira_uuid):
        print("here4", file=sys.stderr, flush=True)
        if jira_clicked:
            print("here5", file=sys.stderr, flush=True)
            authorization_code = st.query_params['code']
            st.query_params.clear()
            id = generate_jira_access_token(authorization_code)
            print(f"here6 [{id}]", file=sys.stderr, flush=True)
            if id:
                cookie_controller.set('jira_uuid', id)
                time.sleep(1)
            # st.query_params.clear()
            # st.rerun()
        else:
            authorization_url, state = get_jira_authorization_url()

            # Display the button with custom styling
            button_html = f'<a href="{authorization_url}" target="_self"><button class="custom-button" id="jira_button">Authenticate Jira :key:</button></a>'
            st.markdown(button_html, unsafe_allow_html=True)
            cookie_controller.set('jira_state', state)
            time.sleep(0.1)
    else:
        jira_inauth = st.button("Logout from Jira")
        if jira_inauth:
            logout_jira(jira_uuid)
            cookie_controller.remove('jira_uuid')
            time.sleep(0.1)
            st.rerun()

if gmail_uuid and gmail_credentials_exists(gmail_uuid):
    st.success("Successfully authenticated with Google")

if jira_uuid and jira_access_token_exists(jira_uuid):
    st.success("Successfully authenticated with Jira")
