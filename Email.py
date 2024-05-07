import streamlit as st

# Set page title and favicon
st.set_page_config(page_title="Gmail Wrapper", page_icon=":email:")

# App title and description
st.title("Gmail Wrapper")
st.write("Access and manage your Gmail inbox with ease.")

# Authentication section
st.header("Authentication")
logged_in = st.session_state.get("logged_in", False)

if not logged_in:
    login_button = st.button("Login with Google")
    if login_button:
        # Perform login logic here
        st.session_state.logged_in = True
        st.rerun()
else:
    logout_button = st.button("Logout")
    if logout_button:
        st.session_state.logged_in = False
        st.rerun()

# Inbox section
if logged_in:
    st.success("Logged in successfully!")
    
    st.header("Inbox")
    search_query = st.text_input("Search emails", placeholder="Enter keywords")
    email_list = st.empty()

    # Placeholder for email list
    with email_list.container():
        selected_email_indices = []
        for i in range(10):  # Placeholder loop, replace with actual email data
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                if st.checkbox("Select", key=f"email_{i}"):
                    selected_email_indices.append(i)
            with col2:
                st.write(f"Email {i+1} Subject")
                st.write("Sender Name")
                st.write("Email Preview...")
            with col3:
                pdf_icon = ":page_facing_up:" if i % 2 == 0 else ""
                spreadsheet_icon = ":bar_chart:" if i % 3 == 0 else ""
                st.write(f"{pdf_icon} {spreadsheet_icon}")
            st.write("---")

    # Email details section
    st.header("Email Details")
    selected_email = st.empty()

    # Display selected email details
    with selected_email.container():
        if selected_email_indices:
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
                            st.write("From: Sender Name")
                            st.write("Subject: Email Subject")
                            show_full_email = st.checkbox(f"Show Full Email {email_index+1}", key=f"show_full_email_{email_index}")
                            if show_full_email:
                                st.write("Body: Email body content...")
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
