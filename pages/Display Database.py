import streamlit as st
import pandas as pd
from SQL.manager import RdsManager

st.title("Table Viewer")

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
    if st.button("Sync with Jira"):
        if 'access_token' not in st.session_state:
            st.error("Please authenticate with Jira before continuing.")
        else:
            print("Oh no this is bad")
            client = st.session_state.JiraClient
            epics = client.search_with_jql("issueType = Epic")
            tasks = client.search_with_jql("issueType = Task")
            bugs = client.search_with_jql("issueType = Bug")

            print("\n\n\nvalue for epics is: ", epics)











