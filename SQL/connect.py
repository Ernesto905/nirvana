import os
import psycopg

def connect_to_rds(host, port, user, password):
    try:
        # Connect to the PostgreSQL server
        conn = psycopg.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        conn.autocommit = True
        print("Connection established.")

        # Create a cursor object
        cursor = conn.cursor()

        # Close connections
        cursor.close()
        conn.close()
        print("Database connection closed.")
    except Exception as e:
        print(f"Error {e}")

