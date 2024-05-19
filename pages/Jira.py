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
        issues = issues_json

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
            search_results = search_results_json

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
    labels = st.text_input("Enter labels separated by spaces:")
    username = st.text_input("Your Username")
    priority = st.selectbox("Select Priority", options=["Low", "Medium", "High", "Highest"])
    issue_type = st.selectbox("Select Issue Type", options=["Bug", "Task", "Epic"])
    due_date = st.date_input("Select a due date:")


    # Format the date as YYYY-MM-DD
    if due_date is not None:
        formatted_date = due_date.strftime('%Y-%m-%d')
        due_date = formatted_date

    # Convert the input string to an array of unique labels
    if labels:
        labels_array = labels_input.split()  
        labels = list(set(labels_array)) 

    if st.button("Create Issue"):
        # Attempt to create an issue using the provided inputs.
        try:
            # Convert the username to a user ID.
            user_id = client.get_userid_by_name(username)

            print(f"due date is {due_date}")
            result = client.create_issue(project, summary, description, user_id, priority, issue_type, due_date, labels)
            st.success("Issue created successfully! Issue ID: " + str(result))
        except Exception as e:
            if str(e) == "list index out of range":
                st.error("Failed to create issue: please enter a valid user")
            else: 
                st.error("Failed to create issue: " + str(e))



    st.subheader("Jira Issue updater")
    """issue, due_date, assignee, status, priority"""
    # UI elements for user inputs.
    issue = st.text_input("Issue title")
    username = st.text_input("Assignee")
    priority = st.selectbox("Select Priority", options=["Low", "Medium", "High", "Highest", "null"])
    status = st.selectbox("Select a status for this issue", options=["To Do", "In Progress", "Done"])
    # due_date = st.date_input("Select a due date:")
    due_date = "2024-10-10"

    if st.button("Update Issue"):
        # Attempt to create an issue using the provided inputs.
        try:
            # Convert the username to a user ID.
            user_id = client.get_userid_by_name(username)
            result = client.update_issue(issue, due_date, user_id, status, priority)
            st.success("Issue updated successfully! Issue: " + str(result))
        except Exception as e:
            if str(e) == "list index out of range":
                st.error("Failed to create issue: please enter a valid user")
            else: 
                st.error("Failed to create issue: " + str(e))

    # Testing
    if st.button("get transitions"):
        try:
            transitions = client.get_transitions()
            st.success(f"Transitions obtained: {transitions}")
        except Exception as e:
            st.error(f"Failed to get transitions: {e}")

    if st.button("get proje"):
        try:
            projs = client.projects()
            st.success(f"issues obtained: {projs}")
        except Exception as e:
            st.error(f"Failed to get projects: {e}")


    if st.button("get issues"):
        try:
            issues = client.get_all_issues()
            st.success(f"issues obtained: {type(issues)}")
        except Exception as e:
            st.error(f"Failed to get projects: {e}")

    if st.button("Get params"):
        try:
            all = client.get_allowed_params()
            st.success(f"params: {all}")
        except Exception as e:
            st.error(f"Failed: {e}")
