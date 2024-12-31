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
            # logprobs=1 
        )
        print("Response from Qwen Model:", response)
        return response.choices[0].message.content

# Example usage
def main():
    # Ensure DASHSCOPE_API_KEY is set in your environment
    if not os.environ.get("DASHSCOPE_API_KEY"):
        print("Error: The environment variable DASHSCOPE_API_KEY is not set.")
        return

    # Initialize the QwenModel
    model = QwenModel(name="qwen2.5-72b-instruct", temperature=1.0)
    #read the content of the file
    with open('/home/jim/HoarePrompt/log141/temp.txt', 'r') as file:
    # with open('/home/jim/HoarePrompt/log_134/check_entailment/0000.prompt.md', 'r') as file:
        prompt = file.read()

    

    try:
        # Make the API call
        response = model._query(prompt)
        print("Response 1 from Qwen Model:", response)
    except Exception as e:
        print("Error occurred:", e)
    print("-------------------------------------------------------------------------\n\n\n")
    # with open('/home/jim/HoarePrompt/log131/0000.prompt.md', 'r') as file:
    #     prompt2 = file.read()

    # try:
    #     response2 = model._query(prompt2)
    #     print("Response from Qwen Model:", response2)
    # except Exception as e:
    #     print("Error occurred:", e)


CODE_COMPLETION_PROMPT_TEMPLATE = """
You are given:
1. A programming problem description.
2. An incomplete Python program that is supposed to solve the problem.

Your task:
1. **Complete the code** by adding only the missing code blocks at the beginning or end of the incomplete code.
2. Leave the existing code unchanged.
3. Ensure the completed program is valid Python and can be parsed without any syntax errors.
Important notes:
- Do not rewrite the existing code; only add what is necessary.
- Handle indentation properly.
- Do not include any explanations or comments in your output.
- Write only the code, nothing else.

Examples for reference:


Problem description: Write a python function to identify non-prime numbers".
Incomplete Program:
```
    for i in range(2,int(math.sqrt(n)) + 1):
        if n % i == 0:
            result = True
    return result
```

Response:
```
result = False
for i in range(2,int(math.sqrt(n)) + 1):
        if n % i == 0:
            result = True
    return result
```

# Example 2

Problem description: Write a function to find the n th fibonacci number.
Incomplete Program:
```
    elif n == 1:
        return b
    else:
        for i in range(1, n):
            c = a + b
            a = b
            b = c
        return b
```

Response:
```
    a = 0
    b = 1
    if n == 0:
        return a
    elif n == 1:
        return b
    else:
        for i in range(1, n):
            c = a + b
            a = b
            b = c
        return b
```

# Example 3

Problem description: Write a function to find  the maximum number in a list.

Incomplete Program:
```
    max_num = 0
    for num in nums:
        if num > max_num:
```

Response:
```
    max_num = 0
    for num in nums:
        if num > max_num:
            max_num = num
    return max_num
```

# Your task

Problem description: {description}
Incomplete Program:
```
{program}
```

"""

def default(model, description, program):
    """
    Completes the given program using the LLM and marks the lines added by the LLM.
    """
    prompt = CODE_COMPLETION_PROMPT_TEMPLATE.format(program=program, description=description)
    response = model._query(prompt)
    #the response might contain ''' at the start and the end pls remove them
    #but only at the start and end
    print ("Response from Qwen Model:", response)
    response = response.strip()
    if response.startswith("```") and response.endswith("```"):
        print("Response starts and ends with ```")
        response = response[3:-3].strip()
    elif response.startswith("'''") and response.endswith("'''"):
        print("Response starts and ends with '''")
        response = response[3:-3].strip()
    elif response.startswith('"""') and response.endswith('"""'):
        print("Response starts and ends with '''")
        response = response[3:-3].strip()

    #if response starts with python remove it
    if response.startswith("python"):
        response = response[6:].strip()
    # Split the response into lines
    response_lines = response.strip().splitlines()
    program_lines = program.strip().splitlines()

    # Helper function to normalize lines for comparison
    def normalize_line(line):
        return line.strip()

    # Identify the added lines
    added_lines = []
    i = 0  # Pointer for the original program lines
    for line in response_lines:
        
        if i < len(program_lines) and normalize_line(line) == normalize_line(program_lines[i]):
            # Line exists in the original program
            added_lines.append(line)
            i += 1
        else:
            # Line is added by the LLM
            added_lines.append(f"{line}  # ADDED_LINE")

    # Join the modified lines back into a single string
    marked_response = "\n".join(added_lines)
    return marked_response



if __name__ == "__main__":

    main()
    
#     model = QwenModel(name="qwen2.5-7b-instruct", temperature=1.0)
#     outp= default(model, "Write a python function to find 2 consecutive numbers in a list that when added amount to 5", """
#    if nums[i] + nums[i+1] == 5:
#          return nums[i], nums[i+1]
# """)
#     print(outp)

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