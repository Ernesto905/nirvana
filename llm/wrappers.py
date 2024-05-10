import replicate

from typing import Any, Dict, Iterator, List, Optional

from langchain_openai.chat_models import ChatOpenAI
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk

# Define REPLICATE_API_TOKEN in .env file
from dotenv import load_dotenv
load_dotenv()


class Arctic(LLM):
    """A custom LangChain wrapper for Snowflake Arctic.

    Example:

        .. code-block:: python

            model = ArcticModel()
            result = model.invoke([HumanMessage(content="hello")])
            result = model.batch([[HumanMessage(content="hello")],
                                 [HumanMessage(content="world")]])
    """

    def _call(
        self,
        prompt: str,
        temperature: float = 0.2,
        token_limit: int = 512,
        system_message: str = "You're a helpful assistant",
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Run the LLM on the given input.

        Args:
            prompt: The prompt to generate from.
            stop: Stop words to use when generating. Model output is cut off at the
                first occurrence of any of the stop substrings.
            run_manager: Callback manager for the run.
            **kwargs: Arbitrary additional keyword arguments. These are usually passed
                to the model provider API call.

        Returns:
            The model output as a string. Actual completions SHOULD NOT include the prompt.
        """
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
            if stop and str(event) in stop:
                break

            output += str(event)

        return output.strip()

    def _stream(
        self,
        prompt: str,
        temperature: float = 0.2,
        token_limit: int = 512,
        system_message: str = "You're a helpful assistant",
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        """Stream the LLM on the given prompt.

        If not implemented, the default behavior of calls to stream will be to
        fallback to the non-streaming version of the model and return
        the output as a single chunk.

        Args:
            prompt: The prompt to generate from.
            stop: Stop words to use when generating. Model output is cut off at the
                first occurrence of any of these substrings.
            run_manager: Callback manager for the run.
            **kwargs: Arbitrary additional keyword arguments. These are usually passed
                to the model provider API call.

        Returns:
            An iterator of GenerationChunks.
        """
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
            if stop and str(event) in stop:
                break
            chunk = GenerationChunk(text=event)
            if run_manager:
                run_manager.on_llm_new_token(chunk.text, chunk=chunk)

            yield chunk

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            # The model name allows users to specify custom token counting
            # rules in LLM monitoring applications (e.g., in LangSmith users
            # can provide per token pricing for their model and monitor
            # costs for the given LLM.)
            "model_name": "CustomChatModel",
        }

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model. Used for logging purposes only."""
        return "custom"

GPT = ChatOpenAI

# Example usage of LangChain Arctic wrapper
if __name__ == "__main__":
    from langchain_core.messages import HumanMessage
    model = Arctic()
    result = model.invoke([HumanMessage(content="hello")])
    print(result)
    result = model.batch([[HumanMessage(content="what is your name?")],
                         [HumanMessage(content="hello my friend")]])
    print(result)

