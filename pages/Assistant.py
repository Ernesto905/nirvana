import streamlit as st
import replicate
import os
from transformers import AutoTokenizer

from SQL.parse import extract_sql
from SQL.manager import RdsManager 

import json
import requests

# App title
st.set_page_config(
    page_title="Nirvana",
    page_icon="⛰️ ",
)


def main():

    # RdsManager is a context manager for database connectivity throughout the program
    with RdsManager(st.secrets.db_credentials.HOST, 
                    st.secrets.db_credentials.PORT,
                    st.secrets.db_credentials.USER,
                    st.secrets.db_credentials.PASS) as db:
        email = "ernesto90543@gmail.com"
        db.create_user_schema(email)
        db.switch_user_schema(email)
        # get_replicate_api_token()
        init_chat_history()
        display_chat_messages()
        get_and_process_prompt(db)


def clear_chat_history():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hey, I'm ChatNirvana! How can I help? Ask me anything about your data.",
        }
    ]
    st.session_state.chat_aborted = False


def init_chat_history():
    """Create a st.session_state.messages list to store chat messages"""
    if "messages" not in st.session_state:
        clear_chat_history()


def display_chat_messages():
    # Set assistant icon to Snowflake logo
    icons = {"assistant": "./public/Nirvana.png", "user": "⛷️"}

    # Display the messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.write(message["content"])


@st.cache_resource(show_spinner=False)
def get_tokenizer():
    """Get a tokenizer to make sure we're not sending too much text
    text to the Model. Eventually we will replace this with ArcticTokenizer
    """
    return AutoTokenizer.from_pretrained("huggyllama/llama-7b")


def get_num_tokens(prompt):
    """Get the number of tokens in a given prompt"""
    tokenizer = get_tokenizer()
    tokens = tokenizer.tokenize(prompt)
    return len(tokens)


def abort_chat(error_message: str):
    """Display an error message requiring the chat to be cleared.
    Forces a rerun of the app."""
    assert error_message, "Error message must be provided."
    error_message = f":red[{error_message}]"
    if st.session_state.messages[-1]["role"] != "assistant":
        st.session_state.messages.append(
            {"role": "assistant", "content": error_message}
        )
    else:
        st.session_state.messages[-1]["content"] = error_message
    st.session_state.chat_aborted = True
    st.rerun()


def get_and_process_prompt(db):
    """Get the user prompt and process it"""
    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant", avatar="./public/Nirvana.png"):
            response = generate_arctic_response()
            st.write(response)


    if st.session_state.chat_aborted:
        st.button("Reset chat", on_click=clear_chat_history, key="clear_chat_history")
        st.chat_input(disabled=True)
    elif prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    if "generated_sql" in st.session_state:
        if st.button("Execute SQL"):
            db.execute_sql(st.session_state.generated_sql)

def generate_arctic_response():
    """String generator for the Snowflake Arctic response."""
    prompt = []
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            prompt.append("User: " + dict_message["content"])
        else:
            prompt.append(
                "Assistant: " + dict_message["content"]
            )

    prompt.append("Assistant: ")
    prompt_str = "\n".join(prompt)

    with open("token.json", "r") as f:
        token = json.load(f)
        print(token)

    body = {
        "message": prompt_str,
        "google-auth-token": token
    }

    response = requests.post("http://localhost:5000/v1/chat", json=body).json()

    if response["status"] != 200:
        st.error(f"""Error processing chat message: {response["response"]}""")
        # abort_chat(response["response"])

    response = response["response"]

    if "<viz encoding=" in response:
        response = response.replace("<viz encoding=", "<img src='data:image/png;base64,")
        response = response.replace(">", "' />")

    return response

    # content = st.session_state.messages[-1]["content"]

if __name__ == "__main__":
    main()
