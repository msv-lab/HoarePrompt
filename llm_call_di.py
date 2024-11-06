import os
import requests

# Replace with your actual DeepInfra API key
deepinfra_api_key = os.environ.get("DEEPINFRA_API_KEY")

def get_llama_response(prompt):
    # Define headers for DeepInfra API
    headers = {
        "Authorization": f"Bearer {deepinfra_api_key}",
        "Content-Type": "application/json"
    }

    # Define the API URL for the OpenAI-compatible chat completion endpoint
    model_url = "https://api.deepinfra.com/v1/openai/chat/completions"

    # Construct the request data payload
    data = {
        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    # Send the POST request to the API
    response = requests.post(model_url, headers=headers, json=data)

    # Check if the response was successful
    if response.status_code == 200:
        # Extract and return the assistant's response
        return response.json()["choices"][0]["message"]["content"]
    else:
        # Raise an error if the request was unsuccessful
        raise Exception(f"Request failed: {response.status_code}, {response.text}")

# Example usage
prompt = "Hello! How can I help you today?"
response = get_llama_response(prompt)
print(response)
