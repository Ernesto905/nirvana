import streamlit as st
from streamlit_navigation_bar import st_navbar
import replicate
import os
from transformers import AutoTokenizer

from SQL.parse import extract_sql
from SQL.manager import RdsManager 

# App title
st.set_page_config(
    page_title="Nirvana",
    page_icon="⛰️ ",
)

page = st_navbar(["Email", "Assistant", "Display Database", "Jira"], selected="Assistant")

if page == "Jira":
    st.switch_page("pages/jira.py")
elif page == "Display Database":
    st.switch_page("pages/display_db.py")
elif page == "Email":
    st.switch_page("Email.py")

def main():

    # RdsManager is a context manager for database connectivity throughout the program
    with RdsManager(st.secrets.db_credentials.HOST, 
                    st.secrets.db_credentials.PORT,
                    st.secrets.db_credentials.USER,
                    st.secrets.db_credentials.PASS) as db:
        email = "ernesto90643@gmail.com"
        db.create_user_schema(email)
        db.switch_user_schema(email)
        get_replicate_api_token()
        init_chat_history()
        display_chat_messages()
        get_and_process_prompt(db)




    # """Execution starts here."""
    # connect_to_rds(st.secrets.db_credentials.HOST, 
    #                st.secrets.db_credentials.PORT,
    #                st.secrets.db_credentials.USER,
    #                st.secrets.db_credentials.PASS)
    # get_replicate_api_token()
    # init_chat_history()
    # display_chat_messages()
    # get_and_process_prompt()


def get_replicate_api_token():
    os.environ["REPLICATE_API_TOKEN"] = st.secrets.api["REPLICATE_API_TOKEN"]


def clear_chat_history():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Please describe your data format and I'll generate a postgres sql table for you.",
        }
    ]
    st.session_state.chat_aborted = False


def init_chat_history():
    """Create a st.session_state.messages list to store chat messages"""
    if "messages" not in st.session_state:
        clear_chat_history()


def display_chat_messages():
    # Set assistant icon to Snowflake logo
    icons = {"assistant": "./public/PSQL.webp", "user": "⛷️"}

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
        with st.chat_message("assistant", avatar="./public/PSQL.webp"):
            response = generate_arctic_response()
            st.write_stream(response)
        

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
            prompt.append("<|im_start|>user\n" + dict_message["content"] + "<|im_end|>")
        else:
            prompt.append(
                "<|im_start|>assistant\n" + dict_message["content"] + "<|im_end|>"
            )

    prompt.append("<|im_start|>assistant")
    prompt.append("")
    prompt_str = "\n".join(prompt)

    num_tokens = get_num_tokens(prompt_str)
    max_tokens = 1500

    if num_tokens >= max_tokens:
        abort_chat(
            f"Conversation length too long. Please keep it under {max_tokens} tokens."
        )

    st.session_state.messages.append({"role": "assistant", "content": ""})

    for event_index, event in enumerate(
        replicate.stream(
            "snowflake/snowflake-arctic-instruct",
            input={
                "prompt": prompt_str,
                "prompt_template": r"{prompt}",
                "temperature": 0.3,
                "top_p": 0.9,
            },
        )
    ):
        st.session_state.messages[-1]["content"] += str(event)
        yield str(event)

    content = st.session_state.messages[-1]["content"]
    sql = extract_sql(content)

    if sql:
        st.write("Generated SQL:")
        st.code(sql, language="sql")
        st.session_state.generated_sql = sql  

if __name__ == "__main__":
    main()
