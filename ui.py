import streamlit as st
import replicate
import os
from transformers import AutoTokenizer

# App title
st.set_page_config(page_title="Hackathon Project")


def main():
    """Execution starts here."""
    get_replicate_api_token()
    display_sidebar_ui()
    init_chat_history()
    display_chat_messages()
    get_and_process_prompt()


def get_replicate_api_token():
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]


def display_sidebar_ui():
    with st.sidebar:
        st.title("Adjust Model Parameters")
        st.slider(
            "temperature",
            min_value=0.01,
            max_value=5.0,
            value=0.3,
            step=0.01,
            key="temperature",
        )
        st.slider(
            "top_p", min_value=0.01, max_value=1.0, value=0.9, step=0.01, key="top_p"
        )

        st.button("Clear chat history", on_click=clear_chat_history)


def clear_chat_history():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Please describe your data format and I'll generate a Database Schema for you.",
        }
    ]
    st.session_state.chat_aborted = False


def init_chat_history():
    """Create a st.session_state.messages list to store chat messages"""
    if "messages" not in st.session_state:
        clear_chat_history()


def display_chat_messages():
    # Set assistant icon to Snowflake logo
    icons = {"assistant": "./public/MySql.jpg", "user": "⛷️"}

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


def get_and_process_prompt():
    """Get the user prompt and process it"""
    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant", avatar="./public/MySql.jpg"):
            response = generate_arctic_response()
            st.write_stream(response)

    if st.session_state.chat_aborted:
        st.button("Reset chat", on_click=clear_chat_history, key="clear_chat_history")
        st.chat_input(disabled=True)
    elif prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()


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
                "temperature": st.session_state.temperature,
                "top_p": st.session_state.top_p,
            },
        )
    ):
        st.session_state.messages[-1]["content"] += str(event)
        yield str(event)


if __name__ == "__main__":
    main()
