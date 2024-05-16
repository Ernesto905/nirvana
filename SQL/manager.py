import psycopg
import json
import re

class RdsManager():
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port 
        self.user = user 
        self.password = password 
        self.conn = None 
        self.cursor = None

    def __enter__(self):
        try:
            # Connect to the PostgreSQL server
            self.conn = psycopg.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )
            self.conn.autocommit = True
            print("Connection established.")

            # Create a cursor object
            self.cursor = self.conn.cursor()

            return self

        except Exception as e:
            print(f"Error encountered {e}")
            raise

    def create_user_schema(self, user_email):
        schema_name = self.get_schema_name(user_email)
        self.cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
        print(f"Schema '{schema_name}' created (if not exists).")

    def switch_user_schema(self, user_email):
        schema_name = self.get_schema_name(user_email)
        self.cursor.execute(f"SET search_path TO {schema_name}")
        print(f"Switched to schema '{schema_name}'.")

    # Generate a valid schema name based on the user's email
    def get_schema_name(self, user_email):
        schema_name = user_email.replace("@", "_").replace(".", "_")
        return schema_name

    def get_tables(self) -> list:
        self.cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = current_schema()
        """)
        return self.cursor.fetchall()

    def execute_core_sql(self, sql, values=None):
        # Check if values are in the correct format (tuple or list), adjust if it's a dictionary
        if isinstance(values, dict):
            # Assume the keys of the dictionary match the placeholders order
            values = tuple(values[key] for key in sorted(values))
            
        try:
            self.cursor.execute(sql, values)
            print("SQL executed successfully!", sql)
        except Exception as e:
            print(f"Error executing SQL: {str(e)}")
            print(f"The SQL we can't execute is: {sql}")
            print(f"With values: {values}")
    

    def execute_sql(self, sql, values=None):
        self.create_metadata_table()

        # Regex to match "CREATE TABLE" with or without "IF NOT EXISTS"
        match_create_pattern = r"CREATE TABLE(\s+IF NOT EXISTS)?\s+(\w+)\s+\((.+)\)"
        match_drop_pattern = r"DROP TABLE\s+(IF EXISTS\s+)?(\w+);"
        match_create = re.search(match_create_pattern, sql, re.IGNORECASE)
        match_drop = re.search(match_drop_pattern, sql, re.IGNORECASE)


        if match_create:
            # Execute the SQL without introspection to avoid recursion
            self.execute_core_sql(sql, values)
            
            table_name = match_create.group(2)
            columns_part = match_create.group(3)
            
            columns = []
            for column_detail in columns_part.split(','):
                first_word = column_detail.strip().split()[0]
                columns.append(first_word)
            
            # Update metadata with newfound table info
            self.update_metadata(table_name, columns)
        elif match_drop: 
            self.execute_core_sql(sql, values)
            table_name = match_drop.group(2)
            print("THE TABLE NAME IS", table_name)

            self.delete_metadata(table_name)
        else:
            # If not a CREATE TABLE statement, just execute the SQL
            self.execute_core_sql(sql, values)



    def delete_metadata(self, table_name):
        delete_sql = "DELETE FROM metadata WHERE table_name = %s;"
        self.execute_core_sql(delete_sql, (table_name,))
        print(f"Metadata for table '{table_name}' deleted.")

    def sync_jira(self, issues, issue_type):
        # Determine the table name based on the issue type
        table_name = issue_type.capitalize() + 's'  
        issues = json.loads(issues)

        # Initialize Issue tables
        self.create_tables(table_name)

        for issue in issues['issues']:
            issue_id = issue['id']
            project_key = issue['fields']['project']['key']
            issue_key = issue['key']
            summary = issue['fields']['summary']
            description = issue['fields']['description']
            status = issue['fields']['status']['name']
            created_date = issue['fields']['created']
            updated_date = issue['fields']['updated']
            due_date = issue['fields']['duedate']

            # Insert the issue data into the corresponding SQL table
            sql = f"""
            INSERT INTO {table_name} (IssueID, Summary, Description, Status, CreatedDate, UpdatedDate, DueDate)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (IssueID) DO UPDATE SET
                Summary = EXCLUDED.Summary,
                Description = EXCLUDED.Description,
                Status = EXCLUDED.Status,
                CreatedDate = EXCLUDED.CreatedDate,
                UpdatedDate = EXCLUDED.UpdatedDate,
                DueDate = EXCLUDED.DueDate;
            """
            values = (issue_id, summary, description, status, created_date, updated_date, due_date)
            self.execute_core_sql(sql, values)

    def create_tables(self, table_name):
        create_table = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            IssueID VARCHAR(255) PRIMARY KEY,
            Summary VARCHAR(255),
            Description TEXT,
            Status VARCHAR(255),
            CreatedDate TIMESTAMP,
            UpdatedDate TIMESTAMP,
            DueDate DATE
        );
        """

        columns = ["IssueID", "Summary", "Description", "Status", "CreatedDate", "UpdatedDate", "DueDate"]
        # Drop tables first
        self.execute_core_sql(f"DROP TABLE IF EXISTS {table_name}")

        # Add table information to metadata table  
        self.update_metadata(table_name, columns)

        self.execute_core_sql(create_table)

    def create_metadata_table(self):
        sql = """CREATE TABLE IF NOT EXISTS metadata (
            table_name VARCHAR(255) PRIMARY KEY,
            table_columns TEXT[]
            );
        """
        try:
            self.execute_core_sql(sql)
        except Exception as e:
            print(f"Error creating metadata table: {e}")
            raise 

    def update_metadata(self, table_name, columns):
        self.create_metadata_table()
        update_sql = """
        INSERT INTO metadata (table_name, table_columns)
        VALUES (%s, %s)
        ON CONFLICT (table_name) DO UPDATE SET
            table_columns = EXCLUDED.table_columns;
        """
        # Execute using execute_core_sql to avoid triggering additional checks
        print("\n\n\n ---- I am here in update_metadata. This should work!", table_name, columns)
        self.execute_core_sql(update_sql, (table_name, columns))

    def get_metadata(self):
        fetch_sql = "SELECT table_name, table_columns FROM metadata"
        self.cursor.execute(fetch_sql)
        rows = self.cursor.fetchall()
        
        metadata_dict = {row[0]: row[1] for row in rows}
        return metadata_dict


    def __exit__(self, exc_type, exc_value, traceback):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed")
