import streamlit as st
from streamlit_navigation_bar import st_navbar
import pandas as pd
from SQL.manager import RdsManager

page = st_navbar(["Email", "Assistant", "Display Database", "Jira"], selected="Display Database")

if page == "Assistant":
    st.switch_page("pages/assistant.py")
elif page == "Jira":
    st.switch_page("pages/jira.py")
elif page == "Email":
    st.switch_page("Email.py")

def display_tables(db):

    """Retrieve the list of tables in the user's schema"""

    db.cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = current_schema()
    """)
    tables = [row[0] for row in db.cursor.fetchall()]

    # Display the table names as selectbox options
    selected_table = st.selectbox("Select a table", tables)

    if selected_table:
        # Retrieve the column names of the selected table
        db.cursor.execute(f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{selected_table}'
            ORDER BY ordinal_position
        """)
        columns = [row[0] for row in db.cursor.fetchall()]

        # Retrieve the data from the selected table
        db.cursor.execute(f"SELECT * FROM {selected_table}")
        data = db.cursor.fetchall()

        # Create a DataFrame with the retrieved data and column names
        import pandas as pd
        df = pd.DataFrame(data, columns=columns)

        # Display the DataFrame using Streamlit's table component
        st.table(df)

with RdsManager(st.secrets.db_credentials.HOST, 
                st.secrets.db_credentials.PORT,
                st.secrets.db_credentials.USER,
                st.secrets.db_credentials.PASS) as db:
    db.switch_user_schema("ernesto90643@gmail.com")          
    display_tables(db)
    
    # Check for Jira Auth
    if st.button("sync with Jira"):
        if 'access_token' not in st.session_state:
            st.error("please authenticate with jira before continuing.")
        else:
            client = st.session_state.JiraClient
            
            with st.spinner("syncing Jira data..."):
                try:
                    # sync all three issue types
                    epics = client.search_with_jql("issuetype = epic")
                    tasks = client.search_with_jql("issuetype = task")
                    bugs = client.search_with_jql("issuetype = bug")

                    db.sync_jira(epics, 'epic')
                    db.sync_jira(tasks, 'task')
                    db.sync_jira(bugs, 'bug')
                except Exception as e:
                    st.error(f"Failed to sync: {e}")
            
            st.success("Jira data synced successfully!")












