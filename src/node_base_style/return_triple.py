import re

from node_base_style.hoare_triple import Triple, pprint_cmd, print_state
from node_base_style.helper import extract_result


# This script's responsible for executing small code snippets and determining the resulting program state based on the provided initial state and program code. It is the general script for a simple program statement (not loops or ifs, try etc)
PROMPT = """
You have been assigned the role of a program executor, responsible for simulating the execution of Python code. You will be provided with an initial state and a Python code snippet. You need to provide the output state after running the Python code based on the initial state. Please avoid describing how the program runs. When a variable has a specific value, use that specific value directly for calculations. If a return takes place makes sure to always mention that a value or variable has been returned at the output state. You must adhere to the text format: Output State: **output state**.
I am giving you some examples to understand the task better. Then I am giving you your task.


Example1:
Initial State: `str` is a string
```
eturn str
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
Example Answer:
Output State: **The program returns string 'str'**


Example2:
Initial State: A is a matrix n x m
```
return A
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
Example Answer:
Output State: **The program returns the n x m sized matrix A**


Example3:
Initial State: `n` is either 3 or 5
```
return n + 1
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
Example Answer:
The value of n can be 3 or 5, so the program returns either 4 or 6.
Output State: **The program returns 4 or 6**


Example4:
Initial State: `x` is 1, `y` is 0, `z` is 0
```
retrun y+x
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
Example Answer: 
`y' is 0 and 'x' is one so the program returns  0+1=1.
Output State: **`The program returns 1**

xample4:
Initial State: `count' contains the number of numbers greater than 1 in the list `numbers`, 'numbers' is a list of integers, 'total' is 0
```
retrun count
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
Example Answer: 
Output State: **`The program returns the number of integers greater than 1 in list 'numbers' **


Your Task:
Initial State: {pre}
```
{program}
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate what the program returns. You must adhere to the text format: Output State: **output state**.
"""

# This is the main function, it completes the prompt, queries the model and extracts the result, meaining the output state of that program part
def complete_return_triple(incomplete_triple: Triple, model):
    pre = print_state(incomplete_triple.precondition)
    program = pprint_cmd(incomplete_triple.command)
    prompt = PROMPT.format(pre=pre, program=program)
    response = model.query(prompt)
    post = extract_result(response, "Output State")
    print("*" * 50)
    print(incomplete_triple)
    print(f"LLM post: {post}")
    return post
