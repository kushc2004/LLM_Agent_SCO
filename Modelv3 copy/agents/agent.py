from typing import Dict, Optional, List, Tuple
from utils.misc import gemini_client
from utils.misc import gemini_client1
from utils.misc import gemini_client2
from utils.misc import gemini_client3


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
    