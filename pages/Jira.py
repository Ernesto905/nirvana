import streamlit as st
import json 
from jira.authentication import *
from jira.client import JiraClient

# Check if the user has already authenticated
if 'access_token' not in st.session_state:
    st.info("Please authenticate with Jira to continue.")
else:
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

    # Title for the Streamlit app.
    st.subheader("Jira Issue Creator")

    # UI elements for user inputs.
    project = st.selectbox("Select Project", options=["KAN"])
    summary = st.text_input("Issue Summary")
    description = st.text_area("Issue Description")
    username = st.text_input("Your Username")
    priority = st.selectbox("Select Priority", options=["Low", "Medium", "High", "Highest"])
    issue_type = st.selectbox("Select Issue Type", options=["Bug", "Task", "Epic"])

    if st.button("Create Issue"):
        # Attempt to create an issue using the provided inputs.
        try:
            # Convert the username to a user ID.
            user_id = client.get_userid_by_name(username)
            result = client.create_issue(project, summary, description, user_id, priority, issue_type)
            st.success("Issue created successfully! Issue ID: " + str(result))
        except Exception as e:
            if str(e) == "list index out of range":
                st.error("Failed to create issue: please enter a valid user")
            else: 
                st.error("Failed to create issue: " + str(e))







