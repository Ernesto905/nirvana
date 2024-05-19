from backend.v1.llm import ChatArctic
from backend.v1.database import RdsManager
from dotenv import load_dotenv
import os
import regex as re
import base64

load_dotenv()

def process_chat(user_message: str, user_email: str) -> str:
    print("domain", os.getenv("DB_HOST"))
    with RdsManager(
        os.getenv("DB_HOST"),
        os.getenv("DB_PORT"),
        os.getenv("DB_USER"),
        os.getenv("DB_PASSWORD")
    ) as rds:
        rds.create_user_schema(user_email)
        rds.switch_user_schema(user_email)
        rds.create_metadata_table()
        metadata = rds.get_metadata()
        print("-service.py Metadata: ", metadata)
        model = ChatArctic(rds=rds)
        response = model.invoke(user_message)

        print("Model response: ", response)

        # if <viz> in response
        if "<viz>" in response:
            with open("visualization.png", "rb") as f:
                viz = base64.b64encode(f.read()).decode("utf-8")
            os.remove("visualization.png") # Remove the file after reading it
            response = re.sub(r"<viz>", f"""<viz encoding="{viz}">""", response)

        return response