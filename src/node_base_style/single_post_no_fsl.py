import re

from node_base_style.hoare_triple import Triple, pprint_cmd, print_state
from node_base_style.helper import extract_result




PROMPT_COMPLEX = """
You have been assigned the role of a program executor, responsible for simulating the execution of Python code. You will be provided with an initial state and a Python code snippet. You need to provide the output state after running the Python code based on the initial state. Please avoid describing how the program runs. When a variable has a specific value, use that specific value directly for calculations. If a return takes place makes sure to always mention that a value or variable has been returned at the output state. You must adhere to the text format: Output State: **output state**.
Include all the information of the precondition that is still valid after the code has been executed. Just update the values of the variables that have been changed by the code and explain what is the value of those veriables
You must adhere to the text format: Output State: **output state**.

# Your task:
Precondition: {precondition}
Program:
```
{code}
```

Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result. You must adhere to the text format: Output State: **output state**.
"""


# This is the main function, it completes the prompt, queries the model and extracts the result, meaining the output state of that program part
def single_post_no_fsl(precondition, code, model):
   
    prompt = PROMPT_COMPLEX.format(precondition=precondition, code=code)
    response = model.query(prompt)
    print(response)
    post = extract_result(response, "Output State")
    print("*" * 50)
    print(f"LLM Reply: {post}")
    return post

