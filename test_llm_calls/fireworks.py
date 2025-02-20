import openai
import os 
client = openai.OpenAI(
    base_url = "https://api.fireworks.ai/inference/v1",
    api_key=os.environ.get("FIREWORKS_API_KEY")
)
response = client.chat.completions.create(
  model="accounts/mechtaev-89641e/deployedModels/qwen2p5-7b-instruct-fa0f85bd",
  messages=[{
    "role": "user",
    "content": "Say this is a test",
  }],
)
print(response.choices[0].message.content)