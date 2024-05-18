from backend.v1.llm import ChatArctic
from backend.v1.database import RdsManager
from dotenv import load_dotenv
import os

load_dotenv()

def process_chat(user_message: str, user_email: str) -> str:
    with RdsManager(
        os.getenv("DB_HOST"),
        os.getenv("DB_PORT"),
        os.getenv("DB_USER"),
        os.getenv("DB_PASSWORD")
    ) as rds:
        rds.switch_user_schema(user_email)
        model = ChatArctic(rds=rds)
        return model.invoke(user_message)