from abc import ABC, abstractmethod
from pathlib import Path

from groq import Groq

import openai

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff


def get_model(name: str, temperature: float, log_directory: Path = None):
    openai_models = {
        "gpt-4o-2024-05-13",
        "gpt-4o-mini-2024-07-18",
        "gpt-4-turbo-2024-04-09",
        "gpt-3.5-turbo-0125"
    }

    if name in openai_models:
        return OpenAIModel(name, temperature, log_directory)

    groq_models = {
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768"
    }
    
    if name in greq_models:
        return GroqModel(name, temperature, log_directory)

    raise ValueError(f"unsupported model {name}")


class Model(ABC):

    def query(self, prompt):
        response = self._query(prompt)
        
        if self.log_directory:
            prompt_file = f"{self.log_counter:04}.prompt.md"
            response_file = f"{self.log_counter:04}.response.md"
            with prompt_file.open("w", encoding ="utf-8") as f:
                f.write(prompt)
            with response_file.open("w", encoding ="utf-8") as f:
                f.write(response)
            self.log_counter += 1

        return response

    @abstractmethod
    def _query(self, prompt):
        pass


class OpenAIModel(Model):

    def __init__(self, name, temperature, log_directory):
        if log_directory:
            self.log_counter = 0
        self.name = name
        self.temperature = temperature
        
        openai.api_key = os.getenv("OPENAI_API_KEY")

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def _query(self, prompt):
        return openai.ChatCompletion.create(
            model=self.name,
            messages={"role": "user", "content": prompt},
            temperature=self.temperature)


class GroqModel(Model):
    
    def __init__(self, name, temperature, log_directory):
        if log_directory:
            self.log_counter = 0
        self.name = name

        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))        
    def _query(self, prompt):
        return self.client.chat.ChatCompletion.create(
            model=self.name,
            messages={"role": "user", "content": prompt},
            temperature=self.temperature)
