import streamlit as st
from streamlit_navigation_bar import st_navbar
from jira.authentication import *
from jira.client import JiraClient
import json 

page = st_navbar(["Email", "Assistant", "Display Database", "Jira"], selected="Jira")

if page == "Assistant":
    st.switch_page("pages/assistant.py")
elif page == "Display Database":
    st.switch_page("pages/display_db.py")
elif page == "Email":
    st.switch_page("Email.py")

# Authenticated with code 
redirecting = False 
auth = False

# Check if the user has already authenticated
if 'access_token' not in st.session_state:

    if 'auth_state' not in st.session_state or 'code' in st.query_params or auth == False:
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





            # st.markdown(f'<a href="{authorization_url}" target="_self">Click here to authenticate with Jira</a>', unsafe_allow_html=True)
# css styling for the button
# CSS styling for the button
            button_style = """
                <style>
                .custom-button {
                    display: inline-block;
                    padding: 0.75rem 1.5rem;
                    background-color: #8B6969;
                    color: #FFF8F3;
                    text-decoration: none;
                    border-radius: 0.25rem;
                    font-weight: bold;
                    transition: background-color 0.3s;
                    font-family: serif;
                    border: none;
                    cursor: pointer;
                    font-size: 1.1rem;
                }
                .custom-button:hover {
                    background-color: #A08080;
                }
                .custom-button:active {
                    background-color: #6B4F4F;
                }
                </style>
            """

# Display the button with custom styling
            button_html = f'<a href="{authorization_url}" target="_self"><button class="custom-button">Authenticate with Jira</button></a>'
            st.markdown(button_style + button_html, unsafe_allow_html=True)




            redirecting = True

    elif redirecting == True: 
        st.warning("Redirecting now...")

else:
    st.success("Successfully Authenticated")
    access_token = st.session_state['access_token']
    cloud_id = get_cloudid(access_token)

    st.session_state.JiraClient = JiraClient(cloud_id, access_token)
    client = st.session_state.JiraClient


# Drop-down feature for displaying issues
    if st.checkbox("Show All Issues"):
        issues_json = client.get_all_issues()
        issues = json.loads(issues_json)
        
        for issue in issues['issues']:
            issue_key = issue['key']
            issue_summary = issue['fields']['summary']
            issue_description = issue['fields']['description'] or 'No description available'
            issue_status = issue['fields']['status']['name']
            issue_priority = issue['fields']['priority']['name']
            issue_assignee = issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned'
            issue_created = issue['fields']['created']
            
            with st.expander(f"{issue_key}: {issue_summary}"):
                st.write(f"**Description:** {issue_description}")
                st.write(f"**Status:** {issue_status}")
                st.write(f"**Priority:** {issue_priority}")
                st.write(f"**Assignee:** {issue_assignee}")
                st.write(f"**Created:** {issue_created}")

# Search bar and button for JQL search
    st.subheader("Search Issues with JQL")
    jql_query = st.text_input("Enter JQL Query")

    if st.button("Search"):
        if jql_query:
            search_results_json = client.search_with_jql(jql_query)
            search_results = json.loads(search_results_json)
            
            if search_results['issues']:
                for issue in search_results['issues']:
                    issue_key = issue['key']
                    issue_summary = issue['fields']['summary']
                    issue_description = issue['fields']['description'] or 'No description available'
                    issue_status = issue['fields']['status']['name']
                    issue_priority = issue['fields']['priority']['name']
                    issue_assignee = issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned'
                    issue_created = issue['fields']['created']
                    
                    with st.expander(f"{issue_key}: {issue_summary}"):
                        st.write(f"**Description:** {issue_description}")
                        st.write(f"**Status:** {issue_status}")
                        st.write(f"**Priority:** {issue_priority}")
                        st.write(f"**Assignee:** {issue_assignee}")
                        st.write(f"**Created:** {issue_created}")
            else:
                st.warning("No issues found matching the JQL query.")
        else:
            st.warning("Please enter a JQL query.")








