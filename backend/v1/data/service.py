from backend.v1.llm import extract_features
from backend.v1.database import RdsManager
from dotenv import load_dotenv
import os

def ingest_data(email: str) -> str:
    """Given an email, extract any features we may want to remember and store them in the database."""
    load_dotenv()
    user_email = "ernesto90643@gmail.com"

    with RdsManager(
        os.getenv("DB_HOST"),
        os.getenv("DB_PORT"),
        os.getenv("DB_USER"),
        os.getenv("DB_PASSWORD")
    ) as rds:
        rds.switch_user_schema(user_email)
        # Get context
        context = rds.get_metadata()
        print(f"Context: {context}")
        features = extract_features(email, context)['extracted_information']
        print(f"Extracted features: {features}")
        for feature in features:
            print(f"Executing SQL: {feature}")
            rds.execute_sql(feature)