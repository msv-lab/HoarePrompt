import re

from node_base_style.hoare_triple import Triple, pprint_cmd, print_state
from node_base_style.helper import extract_result


# This script's responsible for executing small code snippets and determining the resulting program state based on the provided initial state and program code. It is the general script for a simple program statement (not loops or ifs, try etc)
PROMPT = """
You have been assigned the role of a program executor, responsible for simulating the execution of Python code. You will be provided with an initial state and a Python code snippet. You need to provide the output state after running the Python code based on the initial state. Please avoid describing how the program runs. When a variable has a specific value, use that specific value directly for calculations. If a return takes place makes sure to always include the return value or variable at the output state. You must adhere to the text format: Output State: **output state**.


Example1:
Initial State: `str` is a string
```
n = int(input())
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
Example Answer:
`n` is assigned the value `int(input())`, where `input` accepts an input and `int` converts it to an integer. Other variables are not affected, so the output state is `str` is a string, `n` is an input integer.
Output State: **`str` is a string, `n` is an input integer**


Example2:
Initial State: variables can hold any values
```
i += 1
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
Example Answer:
The value of `i` is incremented by 1, but the previous value of `i` is unknown, so the output state is: variable `i` is increased by 1.
Output State: **variable `i` is increased by 1**


Example3:
Initial State: `n` is either 3 or 5
```
m = n + 1
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
Example Answer:
m is assigned the value n + 1. The value of n can be 3 or 5, so the value of m is 4 or 6. Therefore, the Output State is: n is either 3 or 5; m is either 4 or 6.
Output State: **`n` is either 3 or 5; `m` is either 4 or 6**


Example4:
Initial State: `x` is 1, `y` is 0, `z` is 0
```
y = x
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
Example Answer: 
`y` is assigned the value of `x`, and `x` is 1, so after execution, `y` is 1. The states of the other variables are not affected. Therefore, the Output State is: `x` is 1, `y` is 1, `z` is 0.
Output State: **`x` is 1, `y` is 1, `z` is 0**


Example5:
Initial State: `n` is 0, `m` is 2
```
return n
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
Example Answer: 
The function returns `n`, and `n` has a value of 0, so the function returns 0. The return statement does not change the state, so the output state is `n` is 0, `m` is 2, and the function returns 0.
Output State: **`n` is 0, `m` is 2, and the function returns 0**


Your Task:
Initial State: {pre}
```
{program}
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
"""

# This is the main function, it completes the prompt, queries the model and extracts the result, meaining the output state of that program part
def complete_triple(incomplete_triple: Triple, model):
    pre = print_state(incomplete_triple.precondition)
    program = pprint_cmd(incomplete_triple.command)
    prompt = PROMPT.format(pre=pre, program=program)
    response = model.query(prompt)
    post = extract_result(response, "Output State")
    print("*" * 50)
    print(incomplete_triple)
    print(f"LLM post: {post}")
    return post
