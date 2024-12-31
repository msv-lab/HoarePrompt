import re

# This is the template for the prompt that will be used to extract the precondition.
# It is pretty straight forward
# The user is given a problem description and a program that supposedely solves the problem.
# The LLM is then asked to extract the precondition from the problem description.
# The precondition is then surrounded by double asterisks (**)


PRECONDITION_EXTRACTION_PROMPT_TEMPLATE = """
You are given a programming problem description and an incomplete python program that is supposed to solve this problem. From the problem description, and the part of the program that is avaliable to us you have to try to make a guess at the state of the program at the beggining of the incomplete program. You hav to  extract a description of the values of the program's variables and relationship between these variables just before the icnomplete program starts. We refer to this description as precondition. Print the precondition following the word "Precondition", and surrounded with double asterisks (**). Follow these examples:

# Example 1

Problem description: Write a python function to identify non-prime numbers".
Incomplete Program:
```
    for i in range(2,int(math.sqrt(n)) + 1):
        if n % i == 0:
            result = True
    return result
```

Precondition: **n is an integer greater than 1 ,  result is False**

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

Precondition: **n is a positive integer**



# Your task

Problem description: {description}
Incomplete Program:
```
{program}
```

"""

def extract_precondition_from_response_incomplete(response_content):
    pattern = r"Precondition:\s*\*\*(.*?)\*\*|Precondition:\s*(.*)"
    match = re.search(pattern, response_content)
    if match:
        if match.group(1):
            return match.group(1).strip()
        elif match.group(2):
            return match.group(2).strip()
    return response_content


def default(model, description, program):
    prompt = PRECONDITION_EXTRACTION_PROMPT_TEMPLATE.format(program=program, description=description)
    response = model.query(prompt)
    return extract_precondition_from_response_incomplete(response)
    
