import replicate

def generate_response(prompt: str, system_message: str | None = None, temperature: float = 0.2, token_limit: int = 512):
    if system_message is None:
        system_message = "You're a helpful assistant"

    output = ""
    for event in replicate.stream(
        "snowflake/snowflake-arctic-instruct",
        input={
            "top_k": 50,
            "top_p": 0.9,
            "temperature": temperature,
            "max_new_tokens": token_limit,
            "min_new_tokens": 0,
            "stop_sequences": "<|im_end|>",
            "prompt_template": f"<|im_start|>system\n{system_message}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n\n<|im_start|>assistant\n",
            "presence_penalty": 1.15,
            "frequency_penalty": 0.2
        },
    ):
        output += str(event)

    return output.strip()