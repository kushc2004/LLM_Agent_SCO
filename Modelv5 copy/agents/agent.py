from typing import Dict, Optional, List, Tuple
from utils.misc import gemini_client
from utils.misc import gemini_client1
from utils.misc import gemini_client2
from utils.misc import gemini_client3
from utils.misc import *
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models


class Agent:
    def __init__(self, name: str, description: str, **kwargs):
        self.name = name
        self.description = description
        self.system_prompt = "You're a helpful assistant."
        self.kwargs = kwargs

        # Load the model
        self.model = gemini_client()

    def llm_call(
        self,
        prompt: Optional[str] = None,
        messages: Optional[List] = None,
        seed: int = 10,
    ) -> str:
        # Ensure exactly one of prompt or messages is provided
        assert (prompt is None) != (messages is None)

        # Ensure if messages is provided, it is a list of dicts with role and content
        if messages is not None:
            assert isinstance(messages, list)
            for message in messages:
                assert isinstance(message, dict)
                assert "role" in message
                assert "content" in message

        if prompt is not None:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]

        output = self.model.generate_content(prompt)
        output = output.text

        return output


    def llm_call1(
        self,
        prompt: Optional[str] = None,
        messages: Optional[List] = None,
        seed: int = 10,
    ) -> str:
        # Ensure exactly one of prompt or messages is provided
        assert (prompt is None) != (messages is None)

        # Ensure if messages is provided, it is a list of dicts with role and content
        if messages is not None:
            assert isinstance(messages, list)
            for message in messages:
                assert isinstance(message, dict)
                assert "role" in message
                assert "content" in message

        if prompt is not None:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]


        self.model = gemini_client1()
        output = self.model.generate_content(prompt)
        output = output.text

        return output


    def llm_call2(
        self,
        prompt: Optional[str] = None,
        messages: Optional[List] = None,
        seed: int = 10,
    ) -> str:
        # Ensure exactly one of prompt or messages is provided
        assert (prompt is None) != (messages is None)

        # Ensure if messages is provided, it is a list of dicts with role and content
        if messages is not None:
            assert isinstance(messages, list)
            for message in messages:
                assert isinstance(message, dict)
                assert "role" in message
                assert "content" in message

        if prompt is not None:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]
        self.model = gemini_client2()
        output = self.model.generate_content(prompt)
        output = output.text

        return output

    def llm_call3(
        self,
        prompt: Optional[str] = None,
        messages: Optional[List] = None,
        seed: int = 10,
    ) -> str:
        # Ensure exactly one of prompt or messages is provided
        assert (prompt is None) != (messages is None)

        # Ensure if messages is provided, it is a list of dicts with role and content
        if messages is not None:
            assert isinstance(messages, list)
            for message in messages:
                assert isinstance(message, dict)
                assert "role" in message
                assert "content" in message

        if prompt is not None:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]
        self.model = gemini_client3()
        output = self.model.generate_content(prompt)
        output = output.text

        return output
    
    def llm_call_vertexai(
        self,
        prompt: Optional[str] = None,
        messages: Optional[List] = None,
        seed: int = 10,
        ) -> str:
        # Ensure exactly one of prompt or messages is provided
        assert (prompt is None) != (messages is None)

        # Ensure if messages is provided, it is a list of dicts with role and content
        if messages is not None:
            assert isinstance(messages, list)
            for message in messages:
                assert isinstance(message, dict)
                assert "role" in message
                assert "content" in message

        if prompt is not None:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]

        generation_config = {
            "max_output_tokens": 8192,
            "temperature": 0.2,
            "top_p": 1,
        }

        safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        self.model = vertexai_client()
        chat = self.model.start_chat()
        chat.send_message(
        [prompt],
        generation_config=generation_config,
        safety_settings=safety_settings
        )
        output = chat.text

        return output


    def generate_reply(
        self,
        task: str,
        state: Dict,
        sender: "Agent",
    ) -> Tuple[str, Dict]:
        return (
            "This is a reply from the agent. REPLY NOT IMPLEMENTED! Terminate the whole process!",
            state,
        )
    