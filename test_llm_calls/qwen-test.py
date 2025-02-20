import os
from tenacity import retry, wait_random_exponential, stop_after_attempt
from openai import OpenAI

class QwenModel:
    def __init__(self, name, temperature, log_directory=None):
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
        return response.choices[0].message.content

# Example usage
def main():
    # Ensure DASHSCOPE_API_KEY is set in your environment
    if not os.environ.get("DASHSCOPE_API_KEY"):
        print("Error: The environment variable DASHSCOPE_API_KEY is not set.")
        return

    # Initialize the QwenModel
    model = QwenModel(name="llama3.3-70b-instruct", temperature=0.7)

    # Define your prompt
    prompt = "What is the capital of France?"

    try:
        # Make the API call
        response = model._query(prompt)
        print("Response from Qwen Model:", response)
    except Exception as e:
        print("Error occurred:", e)

if __name__ == "__main__":
    main()

# import os
# from openai import OpenAI

# client= OpenAI(
#     api_key=os.environ.get("DASHSCOPE_API_KEY"),
#     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
# )

# completion = client.chat.completions.create(
#     model="qwen-plus",
#     messages=[{"role": "user", "content": "What is the capital of France?"}],
#     temperature=0.7
# )

# print(completion.model_dump_json())