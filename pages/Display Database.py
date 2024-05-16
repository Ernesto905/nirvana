import streamlit as st
import pandas as pd
from SQL.manager import RdsManager


def display_tables(db):

    """Retrieve the list of tables in the user's schema"""

    db.cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = current_schema()
    """)
    tables = [row[0] for row in db.cursor.fetchall()]

    selected_table = st.selectbox("Select a table", tables)

    if selected_table:
        if selected_table == 'metadata':
            columns = ['table_name', 'table_columns']
        else: 
            db.cursor.execute(f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = '{selected_table}'
                ORDER BY ordinal_position
            """)
            columns = [row[0] for row in db.cursor.fetchall()]

        db.cursor.execute(f"SELECT * FROM {selected_table}")
        data = db.cursor.fetchall()

        import pandas as pd
        df = pd.DataFrame(data, columns=columns)

        st.table(df)

with RdsManager(st.secrets.db_credentials.HOST, 
                st.secrets.db_credentials.PORT,
                st.secrets.db_credentials.USER,
                st.secrets.db_credentials.PASS) as db:
    db.create_user_schema("ernesto90543@gmail.com")
    db.switch_user_schema("ernesto90543@gmail.com")          
    display_tables(db)

    if st.button("show metadata"):
        print("THE RETURN VAlUES ARE: ", db.get_metadata())
    
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

                    print("Hello0")
                    db.sync_jira(epics, 'epic')
                    print("Hello1")
                    db.sync_jira(tasks, 'task')
                    print("Hello2")
                    db.sync_jira(bugs, 'bug')
                    print("Hello3")
                    st.success("Jira data synced successfully!")
                except Exception as e:
                    st.error(f"Failed to sync: {e}")
            












