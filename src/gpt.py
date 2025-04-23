import os
import re
from typing import Optional, List, Dict

import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# System prompt for the chat
PROMPT = """We are a small non-profit company that specialises in building software and data solutions for the research sector. We build web, desktop and data engineering applications. Domains that we service include biomedical, bioinformatics, statistics, eresearch, life sciences, agriculture, sensitive data and geospatial. Please assess the grant below and respond with only a score from 0-10 where 0 indicates a poor fit, and 10 indicates a perfect fit for our company."""

class GPT:
    """Interface for interacting with OpenAI's GPT models."""

    def __init__(self, model: str = "gpt-4-turbo-preview"):
        """Initialize the GPT interface.

        Args:
            model: The OpenAI model to use. Defaults to "gpt-4-turbo-preview".
        """
        self.model = model
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Get a chat completion from the OpenAI API.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
            temperature: Controls randomness. Higher values make output more random.
            max_tokens: Maximum number of tokens to generate.

        Returns:
            The generated text response.

        Raises:
            openai.OpenAIError: If the API request fails.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            print(f"DEBUG: API response content: {content}")  # Debug print
            return content
        except openai.OpenAIError as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def analyze_email(self, email_content: str) -> int:
        """Analyze an email using GPT and extract importance score.

        Args:
            email_content: The content of the email to analyze.

        Returns:
            An integer between 0 and 10 representing the email's importance.

        Raises:
            ValueError: If no number is found in the response.
        """
        messages = [
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": email_content}
        ]

        # Get the response
        response = self.chat_completion(messages)
        print(f"DEBUG: Response before regex: {response}")  # Debug print

        # Extract the first number from the response
        match = re.search(r'\d+', response)
        print(f"DEBUG: Regex match: {match}")  # Debug print
        if not match:
            raise ValueError("No number found in GPT response")

        importance = int(match.group())
        print(f"DEBUG: Extracted importance: {importance}")  # Debug print
        if not 0 <= importance <= 10:
            raise ValueError(
                f"Importance score {importance} is not between 0 and 10")

        return importance
