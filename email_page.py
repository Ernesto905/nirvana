import streamlit as st
from streamlit_navigation_bar import st_navbar
from gmail.authentication import login, logout
from gmail.messages import get_messages

# Set page title and favicon
st.set_page_config(page_title="Gmail Wrapper", page_icon=":email:", layout="wide")

page = st_navbar(["Email", "Assistant", "Display Database", "Jira"])

if page == "Assistant":
    st.switch_page("pages/assistant.py")
elif page == "Display Database":
    st.switch_page("pages/display_db.py")
elif page == "Jira":
    st.switch_page("pages/jira.py")

# App title and description
st.title("Gmail Wrapper")
st.write("Access and manage your Gmail inbox with ease.")

# Authentication section
st.header("Authentication")
logged_in = st.session_state.get("logged_in", False)

if not logged_in:
    login_button = st.button("Login with Google :key:")
    if login_button:
        # Perform login logic here
        login(st.session_state)
        st.rerun()
else:
    logout_button = st.button("Logout")
    if logout_button:
        logout(st.session_state)
        st.rerun()

# Inbox section
if logged_in:
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

    email_list = st.empty()
    with email_list.container():

        # Prevent emails from being fetched multiple times
        if not st.session_state.get("emails", None) or st.session_state.get("update_emails", False):
            emails = get_messages(
                st.session_state,
                maxResults=emails_per_page,
                page_number=st.session_state.get("email_page_num", 1),
                query=search_query
            )
            st.session_state["emails"] = emails
            st.session_state["update_emails"] = False
        else:
            emails = st.session_state["emails"]

        selected_email_indices = []
        for i in range(len(emails)):
            col1, col2, col3 = st.columns([0.2, 5, 0.3])
            with col1:
                if st.checkbox(" ", key=f"email_{i}"):
                    selected_email_indices.append(i)
            with col2:
                st.write(f"**{emails[i]['from']}**")
                st.write(f"{emails[i]['date']['month']} {emails[i]['date']['day']}")
                st.write(emails[i]["subject"])
                st.write(emails[i].get("snippet", ""))
            with col3:
                pdf_icon = ":page_facing_up:" if len(emails[i]["pdf_ids"]) > 0 else ""
                spreadsheet_icon = ":bar_chart:" if i % 3 == 0 else ""
                st.write(f"{pdf_icon} {spreadsheet_icon}")
            st.write("---")

    # Email details section
    st.header("Email Details")
    selected_email = st.empty()

    # Display selected email details
    with selected_email.container():
        if selected_email_indices:
            emails = st.session_state["emails"]
            num_columns = 2
            num_rows = (len(selected_email_indices) + num_columns - 1) // num_columns
            for row in range(num_rows):
                columns = st.columns(num_columns)
                for col in range(num_columns):
                    index = row * num_columns + col
                    if index < len(selected_email_indices):
                        email_index = selected_email_indices[index]
                        with columns[col]:
                            st.write(f"Email {email_index+1} Details")
                            st.write(f"From: {emails[email_index]['from']}")
                            st.write(f"Subject: {emails[email_index]['subject']}")
                            show_full_email = st.checkbox(f"Show Full Email {email_index+1}", key=f"show_full_email_{email_index}")
                            if show_full_email:
                                st.write(emails[email_index].get("body", ""))
                                if email_index % 2 == 0:
                                    st.write(":page_facing_up: PDF Attachment")
                                if email_index % 3 == 0:
                                    st.write(":bar_chart: Spreadsheet Attachment")
                            st.write("---")
        else:
            st.write("Select emails to view their details.")

    # LLM section
    st.header("LLM Processing")
    selected_emails = st.empty()

    # Placeholder for selected emails
    with selected_emails.container():
        if selected_email_indices:
            st.write("Selected Emails for LLM Processing:")
            for index in selected_email_indices:
                st.write(f"Email {index+1}")
        else:
            st.write("No emails selected for LLM processing.")

    process_button = st.button("Process with LLM")
    if process_button:
        if selected_email_indices: 
            st.info("Processing emails with LLM...")
            # Add your LLM processing logic here
            st.success("LLM processing completed!")
        else:
            st.error("Please select atleast one email")

else:
    st.info("Please log in to access your Gmail inbox.")