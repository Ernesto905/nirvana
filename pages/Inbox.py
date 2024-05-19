import streamlit as st
from gmail.messages import get_messages

# Set page title and favicon
st.set_page_config(page_title="Gmail Wrapper", page_icon=":email:", layout="wide")

# App title and description
st.title("Gmail Wrapper")
st.write("Access and manage your Gmail inbox with ease.")

logged_in = st.session_state.get("logged_in", False)

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

        for i in range(len(emails)):
            expander_title = f"{emails[i]['subject']} - From: {emails[i]['from']}"
            with st.expander(expander_title, expanded=False):
                st.write(f"Date: {emails[i]['date']['month']} {emails[i]['date']['day']}")
                st.write(emails[i].get("body", ""))

                col1, col2 = st.columns([5, 0.3])
                with col1:
                    st.write("---")
                    option = st.radio("Select an option", ("Option 1", "Option 2", "Option 3", "Option 4"), key=f"option_{i}")
                    query = st.text_input("Enter a query", key=f"query_{i}")
                    if st.button("Process", key=f"process_button_{i}"):
                        # Add your LLM processing logic here based on the selected option and query
                        st.success("LLM processing completed!")
                with col2:
                    pdf_icon = ":page_facing_up:" if len(emails[i]["pdf_ids"]) > 0 else ""
                    spreadsheet_icon = ":bar_chart:" if i % 3 == 0 else ""
                    st.write(f"{pdf_icon} {spreadsheet_icon}")

else:
    st.info("Please log in to access your Gmail inbox.")
