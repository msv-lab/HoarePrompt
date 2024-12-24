import openai
import os
import time

# Replace with your actual OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

def get_response_from_file(file_path):
    # Read prompt from file
    with open(file_path, 'r') as file:
        prompt = file.read()
    
    # Start timing
    start_time = time.time()
    
    # Call ChatGPT-3.5
    response = openai.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    # End timing
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(response)
     # Extract token usage
    tokens_used = response.usage
    input_tokens = tokens_used.prompt_tokens
    output_tokens = tokens_used.completion_tokens
    total_tokens = tokens_used.total_tokens
    
    # Extract and return the response text
    response_text = response.choices[0].message.content
    
    # Print statistics
    print(f"Input Tokens: {input_tokens}")
    print(f"Output Tokens: {output_tokens}")
    print(f"Total Tokens: {total_tokens}")
    print(f"Elapsed Time: {elapsed_time:.2f} seconds")
    
    return response_text

# Example usage
file_path = '/home/jim/magpie_llm/llm_logs/prompt_1225.md'  # Replace with your prompt file path
response = get_response_from_file(file_path)
print(response)
