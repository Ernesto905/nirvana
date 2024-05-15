from utils.wrappers import Arctic
from langchain_core.messages import HumanMessage

def process_chat(user_message: str) -> str:
    model = Arctic()
    return model.invoke([HumanMessage(content=user_message)])