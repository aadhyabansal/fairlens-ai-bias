import os
import time
from abc import ABC, abstractmethod
from google import genai
from dotenv import load_dotenv

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Returns raw text output for a given prompt. Raises on total failure."""
        pass

load_dotenv()

class GeminiProvider(LLMProvider):
    def __init__(self, primary_model="gemini-3.6-flash", fallback_model="gemini-3.5-flash-lite", max_retries=3):
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self.models = [primary_model, fallback_model]
        self.max_retries = max_retries

    def generate(self, prompt: str) -> str:
        last_error = None
        for model_name in self.models:
            for attempt in range(self.max_retries):
                try:
                    response = self.client.models.generate_content(
                        model=model_name, contents=prompt
                    )
                    return response.text.strip()
                except Exception as e:
                    last_error = e
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
        raise RuntimeError(f"All LLM providers/models failed. Last error: {last_error}")
