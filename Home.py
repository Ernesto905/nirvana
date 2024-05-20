import sys

import time
import requests
import streamlit as st
from gmail import gmail_credentials_exists
from jira import logout_jira, get_jira_authorization_url, get_jira_access_token_and_cloudid, jira_access_token_exists, generate_jira_access_token
from streamlit_cookies_controller import CookieController

# Set page title and favicon
st.set_page_config(page_title="Nirvana", page_icon=":peace_symbol:")

cookie_controller = CookieController()

SLEEP_TIME = 0.2

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

with st.popover("Please read me!"):
    url = "https://accounts.google.com/AccountChooser?service=mail&continue=https://mail.google.com/mail/"
    formurl = "https://docs.google.com/forms/d/e/1FAIpQLSc5oZ2uzWDAqAKcyTZHbZpYcyvqEQzG42lFSzslSujQIMp4_w/viewform?usp=sf_link"
    st.markdown("Please click and log into the following email account.")
    st.markdown("check out this [link](%s)" % url)
    st.code("ai.nirvana.example@gmail.com", language="python")
    st.code("strongpassword100!!", language="python")
    st.markdown("It is imperative that you do this. Because our app is so young, it does not meet the restriction of allowing external users to link their GMAIL accounts with us. Thank you for your cooperation 🚀")
    st.markdown("When you auth with google make sure you use the nirvana example account. If you'd like us to add your email directly, please fill out the following form [link](%s)" % formurl)


st.subheader("Authentication")

gmail_uuid = st.query_params.get('gmail_uuid')
if gmail_uuid:
    cookie_controller.set('gmail_uuid', gmail_uuid)
    time.sleep(SLEEP_TIME)
    st.query_params.clear()
jira_uuid = st.query_params.get('jira_uuid')
if jira_uuid:
    cookie_controller.set('jira_uuid', jira_uuid)
    time.sleep(SLEEP_TIME)
    st.query_params.clear()

try:
    gmail_uuid = cookie_controller.get('gmail_uuid')
    jira_uuid = cookie_controller.get('jira_uuid')
except TypeError:
    pass


col1, col2 = st.columns(2, gap="large")  # Adjust the column widths here

with col1:
    if not gmail_uuid or not gmail_credentials_exists(gmail_uuid):
        response = requests.get("http://flask-app:5000/v1/gmail/authorize")
        gmail_auth_url = response.text
        button_html = f'<a href="{gmail_auth_url}" target="_self"><button class="custom-button">Authenticate Google :key:</button></a>'
        st.markdown(button_html, unsafe_allow_html=True)
    else:
        logout_button = st.button("Logout from Google")
        if logout_button:
            response = requests.post(f"http://flask-app:5000/v1/gmail/clear/{gmail_uuid}")
            cookie_controller.remove('gmail_uuid')
            time.sleep(SLEEP_TIME)
            st.rerun()

with col2:
    if not jira_uuid or not jira_access_token_exists(jira_uuid):
        response = requests.get("http://flask-app:5000/v1/jira/authorize").json()
        authorization_url = response.get('authorization_url')
        state = response.get('state')

        # Display the button with custom styling
        button_html = f'<a href="{authorization_url}" target="_self"><button class="custom-button" id="jira_button">Authenticate Jira :key:</button></a>'
        st.markdown(button_html, unsafe_allow_html=True)
    else:
        jira_inauth = st.button("Logout from Jira")
        if jira_inauth:
            logout_jira(jira_uuid)
            cookie_controller.remove('jira_uuid')
            time.sleep(SLEEP_TIME)
            st.rerun()

if gmail_uuid and gmail_credentials_exists(gmail_uuid):
    st.success("Successfully authenticated with Google")

if jira_uuid and jira_access_token_exists(jira_uuid):
    st.success("Successfully authenticated with Jira")
