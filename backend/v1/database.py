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

    def execute_sql(self, sql, values=None):
        try:
            self.cursor.execute(sql, values)
            print("SQL executed successfully!")
        except Exception as e:
            print(f"Error executing SQL: {str(e)}")

    def sync_jira(self, issues, issue_type):
        table_name = issue_type.capitalize() + 's'  # Determine the table name based on the issue type
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
            self.execute_sql(sql, values)

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

        # Drop tables first
        self.execute_sql(f"DROP TABLE IF EXISTS {table_name}")

        self.execute_sql(create_table)

    def create_metadata_table(self):
        sql = """CREATE TABLE IF NOT EXISTS metadata (
            table_name VARCHAR(255) PRIMARY KEY,
            table_columns TEXT[]
            );
        """
        self.execute_sql(sql)

    def update_metadata(self, sql):
    # Regular expression to capture CREATE TABLE statements
    create_table_pattern = r"CREATE TABLE IF NOT EXISTS (\w+) \(([^)]+)\)"
    match = re.search(create_table_pattern, sql, re.IGNORECASE)
    
    if match:
        table_name = match.group(1)
        columns_part = match.group(2)
        columns = [col.strip().split()[0] for col in columns_part.split(',')]

        # Insert/update metadata table
        update_sql = """
        INSERT INTO metadata (table_name, table_columns)
        VALUES (%s, %s)
        ON CONFLICT (table_name) DO UPDATE SET
            table_columns = EXCLUDED.table_columns;
        """
        self.execute_sql(update_sql, (table_name, columns))
        print(f"Metadata for table '{table_name}' updated.")

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed")
