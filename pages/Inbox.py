import streamlit as st
from jira.authentication import *
import re
import ast
from gmail import gmail_credentials_exists, get_messages
from streamlit_cookies_controller import CookieController

# Set page title and favicon
st.set_page_config(page_title="Gmail Wrapper", page_icon=":email:", layout="wide")

cookie_controller = CookieController()

# App title and description
st.title("Gmail Wrapper")
st.write("Access and manage your Gmail inbox with ease.")

gmail_uuid = None
try:
    gmail_uuid = cookie_controller.get('gmail_uuid')
except TypeError:
    pass
jira_uuid = None
try:
    jira_uuid = cookie_controller.get('jira_uuid')
except TypeError:
    pass

# Inbox section
if gmail_uuid and gmail_credentials_exists(gmail_uuid):
    st.success("Logged in successfully!")

    st.header("Inbox")

    def email_change_callback():
        st.session_state["update_emails"] = True

    search_query = st.text_input(
        "Search emails",
        placeholder="Enter keywords",
        on_change=email_change_callback
    )

    col1, col2 = st.columns([3, 0.5])
    with col1:
        emails_per_page = st.selectbox(
            "Emails per page:",
            [10, 25, 50, 100],
            on_change=email_change_callback
        )

    with col2:
        st.write("\n")
        button1, button2 = st.columns([1, 1])
        with button1:
            if st.button("<", help="Newer", use_container_width=True):
                current_value = st.session_state.get("email_page_num", 1)
                st.session_state["email_page_num"] = current_value - 1 if current_value > 1 else 1
                email_change_callback()
        with button2:
            if st.button("\\>", help="Older", use_container_width=True):
                current_value = st.session_state.get("email_page_num", 1)
                st.session_state["email_page_num"] = current_value + 1
                email_change_callback()

    from gmail import get_gmail_credentials
    # st.write(get_gmail_credentials(gmail_uuid))
    email_list = st.empty()
    with email_list.container():

        # Prevent emails from being fetched multiple times
        if not st.session_state.get("emails", None) or st.session_state.get("update_emails", False):
            emails = get_messages(
                gmail_uuid,
                st.session_state,
                maxResults=emails_per_page,
                page_number=st.session_state.get("email_page_num", 1),
                query=search_query
            )
            st.session_state["emails"] = emails
            st.session_state["update_emails"] = False
        else:
            emails = st.session_state["emails"]

        for i in range(len(emails)):
            expander_title = f"{emails[i]['subject']} - From: {emails[i]['from']}"
            with st.expander(expander_title, expanded=False):
                st.write(f"Date: {emails[i]['date']['month']} {emails[i]['date']['day']}")
                st.write(emails[i].get("body", ""))

                col1, col2 = st.columns([5, 0.3])


                if not jira_uuid and not jira_access_token_exists(jira_uuid):
                    st.info("Please authenticate with Jira to enable LLM functionality")
                else:
                    access_token, cloud_id = get_jira_access_token_and_cloudid(jira_uuid)

                    with col1:

                        if st.button("Get action", key=f"send_button_{i}"):
                            payload = {
                                "email": emails[i].get("body", ""),
                                "jira-cloud-id": cloud_id,
                                "jira-auth-token": access_token
                            }
                            response = requests.post("http://localhost:5000/v1/jira/actions", json=payload)
                            data = response.json()

                            actions = data["actions"]
                            actions = ast.literal_eval(actions)
                            st.session_state["actions"] = actions
                            # st.info(f"{actions[0]}")
                            for action in actions:
                                if "create_issue" in action:
                                    # get the project and summary
                                    # project is after "project=" or "project ="
                                    # summary is after "summary=" or "summary ="
                                    project = re.search(r'project\s*=\s*([^\s,]+)', action).group(1)
                                    summary = re.search(r'summary\s*=\s*([^\s,]+)', action).group(1)
                                    project = re.sub("(\"|')", "", project)
                                    summary = re.sub("(\"|')", "", summary)
                                    st.write(f"Create Issue: {project} - {summary}")
                                if "update_issue" in action:
                                    # get the issue name
                                    issue = re.search(r'issue\s*=\s*([^\s,]+)', action).group(1)
                                    issue = re.sub("(\"|')", "", issue)

                                    candidates = ["due_date", "assignee", "status", "priority"]
                                    ls = []
                                    for candidate in candidates:
                                        if candidate in action:
                                            value = re.search(f'{candidate}\s*=\s*([^\s,]+)', action).group(1)
                                            value = re.sub("(\"|')", "", value)
                                            ls.append(f"set {candidate} to {value}")

                                    st.write(f"Update Issue {issue} to {', '.join(ls).strip(", ")}")

                            # now we parse the action to show a list


                        st.write("---")
                        if st.button("Process", key=f"process_button_{i}"):
                            payload = {
                                "action": st.session_state["actions"][0],
                                "jira-cloud-id": cloud_id,
                                "jira-auth-token": access_token
                            }
                            response = requests.post("http://localhost:5000/v1/jira/execute", json=payload)
                            st.success(f"Response: {response.text}")


                            st.success("LLM processing completed!")

                    with col2:
                        pdf_icon = ":page_facing_up:" if len(emails[i]["pdf_ids"]) > 0 else ""
                        spreadsheet_icon = ":bar_chart:" if i % 3 == 0 else ""
                        st.write(f"{pdf_icon} {spreadsheet_icon}")

else:
    st.info("Please log in to access your Gmail inbox.")
