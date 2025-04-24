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
            messages: List of message dictionaries with 'role' and 'content'
                keys.
            temperature: Controls randomness. Higher values make output more
                random.
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
            return content
        except openai.OpenAIError as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def classify_tender(self, tender_content: str) -> int:
        """Classify a tender using GPT and extract relevance score.

        Args:
            tender_content: The content of the tender to analyze, including
                          agency, category, and description.

        Returns:
            An integer between 0 and 10 representing the tender's relevance
            to our company's capabilities and interests.

        Raises:
            ValueError: If no number is found in the response.
        """
        messages = [
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": tender_content}
        ]

        # Get the response
        response = self.chat_completion(messages)

        # Extract the first number from the response
        match = re.search(r'\d+', response)
        if not match:
            raise ValueError("No number found in GPT response")

        importance = int(match.group())
        if not 0 <= importance <= 10:
            raise ValueError(
                f"Importance score {importance} is not between 0 and 10")

        return importance
