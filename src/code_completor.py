import re

# This is the template for the prompt that will be used to extract the precondition.
# It is pretty straight forward
# The user is given a problem description and a program that supposedely solves the problem.
# The LLM is then asked to extract the precondition from the problem description.
# The precondition is then surrounded by double asterisks (**)


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
            added_lines.append(f"{line} # ADDED LINE")

    # Join the modified lines back into a single string
    marked_response = "\n".join(added_lines)
    print("Marked Response:", marked_response)
    return marked_response

