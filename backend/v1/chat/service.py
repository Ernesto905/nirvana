from utils.wrappers import Arctic
from backend.v1.llm import (
    ChatArctic
)
from langchain_core.messages import HumanMessage

def process_chat(user_message: str, user_email: str) -> str:
    model = ChatArctic()
    return model.invoke([HumanMessage(content=user_message)])