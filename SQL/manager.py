import psycopg

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

    def execute_sql(self, sql):
        print("----------Made it here----------")
        try:
            self.cursor.execute(sql)
            print("SQL executed successfully!")
        except Exception as e:
            print(f"Error executing SQL: {str(e)}")


    def __exit__(self, exc_type, exc_value, traceback):
        pass
        # if self.cursor:
        #     self.cursor.close()
        # if self.conn:
        #     self.conn.close()
        # print("Database connection closed")

            
