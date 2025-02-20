import openai
import os
import requests
# Replace with your actual OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

def get_response_from_file(file_path):
    # Read prompt from file
    with open(file_path, 'r') as file:
        prompt = file.read()
        temperature = 0.5
        api_key = os.environ.get("DEEPINFRA_API_KEY")
        name="meta-llama/Meta-Llama-3.1-70B-Instruct"

   
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
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

# Example usage
file_path = '/home/jim/HoarePrompt/log190/compute-postcondition/0000.prompt.md'  # Replace with your prompt file path
# file_path = 'log_053/0000.prompt.md'  # Replace with your prompt file path

response = get_response_from_file(file_path)
print(response)
# import re

# resp='''The code seems to be following the problem description, as it iterates through the list of numbers and calculates the total sum and count of positive integers. It also correctly handles non-positive numbers by skipping them and returning a message. Additionally, the code correctly handles the case of an empty input list by returning 0 for the total and count, and `None` for the average.

# Correctnessd

# The output hints also agree with the code as they describe the function's behavior and the handling of non-positive numbers and empty input list. The cases described in the output hints are valid and make sense with respect to the code.

# Therefore, based on both the problem description and the output hints, the code is correct and follows the specified requirements.

# Correctness: **True**'''

# def extract_correctness_from_response(response_content: str) -> str:
#     pattern = r"Correctness:\s*\*\*(.*?)\*\*|Correctness:\s*(True|False)"
#     match = re.findall(pattern, response_content)
#     if match:
#         if match[-1][0]:
#             return match[-1][0].strip()
#         elif match[-1][1]:
#             return match[-1][1].strip()
#     return response_content

# print(extract_correctness_from_response(resp))