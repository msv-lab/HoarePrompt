import re

from node_base_style.hoare_triple import Triple, pprint_cmd, print_state
from node_base_style.helper import extract_result




PROMPT_COMPLEX = """
You have been assigned the role of a program executor, responsible for simulating the execution of Python code. You will be provided with an initial state(precondition) and a Python code snipet (usually a function). You need to provide the output state after running the Python code based on the initial state. Please avoid describing how the program runs. When a variable has a specific value, use that specific value directly for calculations. If a return takes place makes sure to always mention that a value or variable has been returned at the output state. You must adhere to the text format: Output State: **output state**.
Include all the information of the precondition that is still valid after the code has been executed. Just update the values of the variables that have been changed by the code.
You must adhere to the text format: Output State: **output state**.
I am giving you some examples to understand the task better. Then I am giving you your task.

#Example 1:
Precondition: lst is a list of integers
Program:
```
def sum_odd(lst):
    total = 0
    for num in lst:
        if num % 2 != 0:
            total += num
    return total
```
Example Response 1: Output State: **lst is a list of integers, the function returns total which is the sum of all numbers in the list that are odd *

#Example 1:
Precondition: sum is an array of integers of size n x n
Program:
```
#function that sums the 2 main diagonals of the array
# the function returns the sum of the 2 main diagonals of the array 
def sum_diagonals(sum):
    total = 0
    for i in range(len(sum)):
        total += sum[i][i]
        total += sum[i][len(sum) - i - 1]
    if len(sum) % 2 != 0:
        total -= sum[len(sum) // 2][len(sum) // 2]
    return total
```
Example Response 1: Output State: **sum is an array of integers of size n x n, the function returns total which is the sum of the 2 main diagonals of the array**

# Your task:
Precondition: {precondition}
Program:
```
{code}
```

Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result. You must adhere to the text format: Output State: **output state**.
"""


# This is the main function, it completes the prompt, queries the model and extracts the result, meaining the output state of that program part
def single_post(precondition, code, model):
   
    prompt = PROMPT_COMPLEX.format(precondition=precondition, code=code)
    response = model.query(prompt)
    print(response)
    post = extract_result(response, "Output State")
    print("*" * 50)
    print(f"LLM Reply: {post}")
    return post
