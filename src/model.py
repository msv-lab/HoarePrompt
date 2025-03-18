import os
from abc import ABC, abstractmethod
from pathlib import Path
import math
import json

from groq import Groq

from openai import OpenAI

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff

import requests
def log_token_usage(prompt_tokens, completion_tokens, total_tokens, filepath):
    """
    Appends usage data to a file named tokens.json (JSON-line format).
    """
    # Open (or create if doesn't exist) and append to the file
    
    with open(filepath, "a") as f:
        record = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }
        f.write(json.dumps(record) + "\n")



# Returns the appropriate model object based on the model name. Supports OpenAI, Groq, DeepSeek, and Qwen models.
def get_model(name: str, temperature: float, log_directory: Path = None):
    openai_models = {
        "gpt-4o-2024-08-06",
        "gpt-3.5-turbo-instruct",
        "gpt-4o-2024-05-13",
        "gpt-4o-mini-2024-07-18",
        "gpt-4-turbo-2024-04-09",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-1106"
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

    deepinfra_models = {
        "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "meta-llama/Llama-3.3-70B-Instruct"
    }

    if name in deepinfra_models:
        return DeepInfraModel(name, temperature, log_directory)

    if name in deepseek_models:
        return DeepSeekModel(name, temperature, log_directory)

    qwen_models = {
        "qwq-32b-preview",  # reasoning model
        "qwen2.5-7b-instruct",  # model better than gpt3.5
        "qwen-plus",
        "qwen2.5-72b-instruct",
        "qwen2.5-coder-7b-instruct",
        "qwen2.5-coder-32b-instruct"
    }
    fireworks_models = {"qwen2p5-7b-instruct",  # model better than gpt3.5
        "qwen2p5-coder-32b-instruct",
        "qwen2p5-72b-instruct",
        "accounts/mechtaev-89641e/deployedModels/qwen2p5-7b-instruct-fa0f85bd"
    }
    if name in fireworks_models:
        return FireworksModel(name, temperature, log_directory)



    if name in qwen_models:
        return QwenModel(name, temperature, log_directory)

    # Raise an error if the model name does not match any supported models
    raise ValueError(f"unsupported model {name}")


# Abstract base class for all models
# It defines a query method to interact with the model and log the queries and responses
class Model(ABC):

    # Queries the model with a given prompt and logs the interaction if a log directory is set.
    # Since we now create a temporary log dir, all interactions are logged but if log not specified they will be overwritten at the next invocation of the tool
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

    #Abstract method that must be implemented by subclasses to handle the model query.
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

        # Initialize OpenAI client using the API key from environment variables
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        
    # Queries the OpenAI API with a prompt, using exponential backoff for retries in case of failures.
    # When a request to the API fails , the system will automatically try again after waiting for a certain period . Each retry will wait a different time than the previous one to avoid overloading the server.
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def _query(self, prompt):
        response = self.client.chat.completions.create(
            model=self.name,
            messages=[{"role": "user", "content": prompt}] if isinstance(prompt, str) else prompt,
            temperature=self.temperature)
        return response.choices[0].message.content
    
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def query_confidence(self, prompt):
        response = self.client.completions.create(
            model="gpt-3.5-turbo-instruct",  # Use the updated model
            prompt=prompt,
            max_tokens=50,
            logprobs=5  # Request token-level log probabilities
        )
        
         # Get the response content
        content = response.choices[0].text.strip()

        # Extract log probabilities
        logprobs = response.choices[0].logprobs

        if logprobs and logprobs.token_logprobs:
            token_logprobs = logprobs.token_logprobs

            # Filter out invalid log probabilities
            valid_logprobs = [lp for lp in token_logprobs if lp > -1000]

            if valid_logprobs:
                # Calculate the average log probability
                average_logprob = sum(valid_logprobs) / len(valid_logprobs)
                # Convert to confidence score
                confidence = math.exp(average_logprob)
            else:
                confidence = None
        else:
            confidence = None

        return content, confidence

class GroqModel(Model):
    
    def __init__(self, name, temperature, log_directory):
        self.log_directory = log_directory
        if log_directory:
            self.log_counter = 0 # Counter for logging interactions
        self.name = name
        self.temperature = temperature

        # Initialize Groq client using the API key from environment variables
        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )

    # Queries the Groq API with a prompt, using exponential backoff for retries in case of failures.
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def _query(self, prompt):
        response = self.client.chat.completions.create(
            model=self.name,
            messages=[{"role": "user", "content": prompt}] if isinstance(prompt, str) else prompt,
            temperature=self.temperature)
        return response.choices[0].message.content

# Same for the other models
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
class FireworksModel(Model):
    def __init__(self, name, temperature, log_directory):
        self.log_directory = log_directory
        if log_directory:
            self.log_counter = 0
        self.name = name
        self.temperature = temperature

        self.client = OpenAI(
            api_key=os.environ.get("FIREWORKS_API_KEY"),
            base_url="https://api.fireworks.ai/inference/v1"
        )

    # @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def _query(self, prompt):
        if "accounts" in self.name:
            model_name=self.name
        else:
            model_name =f"accounts/fireworks/models/{self.name}"
        # print(f"the name of the model is {self.name}\n{ model_name}")
        response = self.client.chat.completions.create(
            model=model_name,
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

    # @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def _query(self, prompt):
        response = self.client.chat.completions.create(
            model=self.name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature
        )

            # Extract usage stats (if the API provides them)
      
        
        return response.choices[0].message.content
    
    def query_confidence_qwen(self, prompt):
        # Call the API and get the response
        response = self.client.chat.completions.create(
            model=self.name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            logprobs=1
        )

        # Extract the response message
        choice = response.choices[0]
        response_content = choice.message.content.strip()

        # Extract log probabilities
        logprobs = choice.logprobs.content
        response_token = logprobs[0]  # The main token (True or False)
        print(response_token)
        # Calculate probability
        probability = math.exp(response_token.logprob)

        # Return the response and its probability
        return response_content, probability


class DeepInfraModel(Model):

    def __init__(self, name, temperature, log_directory):
        self.log_directory = log_directory
        if log_directory:
            self.log_counter = 0
        self.name = name
        self.temperature = temperature
        self.api_key = os.environ.get("DEEPINFRA_API_KEY")

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def _query(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature
        }

        response = requests.post(
            "https://api.deepinfra.com/v1/openai/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Request failed: {response.status_code}, {response.text}")

