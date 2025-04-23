import unittest
from unittest.mock import patch, MagicMock

from src.gpt import GPT


class TestGPT(unittest.TestCase):
    """Test cases for the GPT class."""

    @patch("src.gpt.openai.OpenAI")
    def setUp(self, mock_openai):
        """Set up test fixtures."""
        self.mock_client = MagicMock()
        self.mock_response = MagicMock()
        self.mock_message = MagicMock()
        self.mock_choice = MagicMock()
        self.mock_choice.message = self.mock_message
        self.mock_response.choices = [self.mock_choice]
        self.mock_client.chat.completions.create.return_value = (
            self.mock_response)
        mock_openai.return_value = self.mock_client
        self.gpt = GPT()

    def test_analyze_email_success(self):
        """Test successful email analysis."""
        self.mock_message.content = "8"

        # Test the analyze_email method
        score = self.gpt.analyze_email("Test email content")

        # Verify the mock was called correctly
        self.mock_client.chat.completions.create.assert_called_once()
        call_args = self.mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], "gpt-4-turbo-preview")
        self.assertEqual(len(call_args["messages"]), 2)
        self.assertEqual(
            call_args["messages"][1]["content"],
            "Test email content"
        )

        # Verify the result
        self.assertEqual(score, 8)

    def test_analyze_email_no_number(self):
        """Test email analysis when no number is found in response."""
        self.mock_message.content = "No number here"

        # Test that ValueError is raised when no number is found
        with self.assertRaises(ValueError) as cm:
            self.gpt.analyze_email("Test email content")
        self.assertEqual(str(cm.exception), "No number found in GPT response")

    def test_analyze_email_invalid_score(self):
        """Test email analysis when score is outside valid range."""
        self.mock_message.content = "15"

        # Test that ValueError is raised when score is invalid
        with self.assertRaises(ValueError) as cm:
            self.gpt.analyze_email("Test email content")
        self.assertEqual(
            str(cm.exception),
            "Importance score 15 is not between 0 and 10"
        )


if __name__ == "__main__":
    unittest.main()
