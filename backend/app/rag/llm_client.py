import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


class LLMClient:
    """
    Handles communication with the Groq API.
    """

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Please add it to your .env file."
            )

        self.client = Groq(api_key=api_key)

        self.model_name = "llama-3.3-70b-versatile"

    def generate_response(self, prompt: str) -> str:
        """
        Sends the prompt to the Groq LLM
        and returns the generated response.
        """

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0, 
        )

        return response.choices[0].message.content