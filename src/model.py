import os
from abc import ABC, abstractmethod
from pathlib import Path

from groq import Groq

from openai import OpenAI

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
    
    if name in groq_models:
        return GroqModel(name, temperature, log_directory)

    deepseek_models = {
        "deepseek-chat",
        "deepseek-coder"
    }

    if name in deepseek_models:
        return DeepSeekModel(name, temperature, log_directory)

    qwen_models = {
        # models below solve complicated problem
        "qwen-max",  # the latest version
        "qwen-max-0403",
        "qwen-max-0107",
        "qwen-max-longcontext",
        # less-complicated
        "qwen-plus",  # the latest version
        "qwen-plus-0806",  # beta stage
        "qwen-plus-0624",
        "qwen-plus-0206",
        # simple
        "qwen-turbo",  # the latest version
        "qwen-turbo-0206"
    }

    if name in qwen_models:
        return QwenModel(name, temperature, log_directory)

    raise ValueError(f"unsupported model {name}")


class Model(ABC):

    def query(self, prompt):
        response = self._query(prompt)
        
        if self.log_directory:
            prompt_file = self.log_directory / f"{self.log_counter:04}.prompt.md"
            response_file = self.log_directory / f"{self.log_counter:04}.response.md"
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
        self.log_directory = log_directory
        if log_directory:
            self.log_counter = 0
        self.name = name
        self.temperature = temperature

        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def _query(self, prompt):
        response = self.client.chat.completions.create(
            model=self.name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature)
        return response.choices[0].message.content


class GroqModel(Model):
    
    def __init__(self, name, temperature, log_directory):
        self.log_directory = log_directory
        if log_directory:
            self.log_counter = 0
        self.name = name

        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def _query(self, prompt):
        response = self.client.chat.ChatCompletion.create(
            model=self.name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature)
        return response.choices[0].message.content


class DeepSeekModel(Model):
    def __init__(self, name, temperature, log_directory):
        self.log_directory = log_directory
        if log_directory:
            self.log_counter = 0
        self.name = name
        self.temperature = temperature

        self.client = OpenAI(
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def _query(self, prompt):
        response = self.client.chat.completions.create(
            model=self.name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature
        )
        return response.choices[0].message.content


class QwenModel(Model):
    def __init__(self, name, temperature, log_directory):
        self.log_directory = log_directory
        if log_directory:
            self.log_counter = 0
        self.name = name
        self.temperature = temperature

        self.client = OpenAI(
            api_key=os.environ.get("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def _query(self, prompt):
        response = self.client.chat.completions.create(
            model=self.name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature
        )
        return response.choices[0].message.content

