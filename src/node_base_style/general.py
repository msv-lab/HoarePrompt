import re

from node_base_style.hoare_triple import Triple, pprint_cmd, print_state
from node_base_style.helper import extract_result


# This script's responsible for executing small code snippets and determining the resulting program state based on the provided initial state and program code. It is the general script for a simple program statement (not loops or ifs, try etc)
PROMPT = """
You have been assigned the role of a program executor, responsible for simulating the execution of Python code. You will be provided with an initial state and a Python code snippet. You need to provide the output state after running the Python code based on the initial state. Please avoid describing how the program runs. When a variable has a specific value, use that specific value directly for calculations. If a return takes place makes sure to always mention that a value or variable has been returned at the output state. You must adhere to the text format: Output State: **output state**.
Include all the information of the precondition that is still valid after the code has been executed. Just update the values of the variables that have been changed by the code.
I am giving you some examples to understand the task better. Then I am giving you your task.


Example1:
Initial State: `str` is a string
```
n = int(input())
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
Example Answer 1:
`n` is assigned the value `int(input())`, where `input` accepts an input and `int` converts it to an integer. Other variables are not affected, so the output state is `str` is a string, `n` is an input integer.
Output State: **`str` is a string, `n` is an input integer**


Example2:
Initial State: variables can hold any values
```
i += 1
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
Example Answer 2:
The value of `i` is incremented by 1, but the previous value of `i` is unknown, so the output state is: variable `i` is increased by 1.
Output State: **variable `i` is increased by 1**


Example3:
Initial State: `n` is either 3 or 5
```
m = n + 1
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
Example Answer 3:
m is assigned the value n + 1. The value of n can be 3 or 5, so the value of m is 4 or 6. Therefore, the Output State is: n is either 3 or 5; m is either 4 or 6.
Output State: **`n` is either 3 or 5; `m` is either 4 or 6**


Example4:
Initial State: `x` is a positive integer, if x is greater than 10 then z=0 else z=1.
```
y = -z
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
Example Answer : 
`y` is assigned the value of minus `z`, and if x is greater than 10 then z=0 else z=1.The states of the other variables are not affected. 
Output State: **`x` is a positive integer, if x is greater than 10 then z=0 and y =0 , else z=1 and y=-1**


Example 5:
Initial State: `total' is 0, `i` is 1
```
break
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
Example Answer 5: 
`The values of the variables do not change but we break out of the loop of if statement we were directly inside. Therefore, the Output State is:  `total' is 0, `i` is 1 and we break out of the most internal loop or if statement.
Output State: **`total' is 0, `i` is 1 and we break out of the most internal loop or if statement.**

Example 6:
Initial State: `total' is positive, `num` is negative, `x` is 0
```
x = total - num
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
Example Answer 6: 
`x' becomes total minus num. The value of `total` is positive, and the value of `num` is negative, so the value of `x` is a positive valye greater than total. The states of the other variables are not affected. Therefore, the Output State is: `total' is positive, `num` is negative, `x` is a positive value `total` - `num.
Output State: **`total' is positive, `num` is negative, `x` is a positive value equal to `total` - `num'.**

Your Task:
Initial State: {pre}
```
{program}
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result. You must adhere to the text format: Output State: **output state**.
Be as specific as possible. If a variable has a specific value or is equal to some combination of variables, use that specific value  or expression it is equal to. nclude all the information of the precondition that is still valid after the code has been executed. Just update the values of the variables that have been changed by the code.
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
