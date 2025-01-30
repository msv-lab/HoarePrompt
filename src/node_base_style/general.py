import re

from node_base_style.hoare_triple import Triple, pprint_cmd, print_state
# from node_base_style.helper import extract_result
import re

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

Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result. 
Be as specific as possible. If a variable has a specific value or is equal to some combination of variables, use that specific value  or expression it is equal to. nclude all the information of the precondition that is still valid after the code has been executed. Just update the values of the variables that have been changed by the code.
In your response strictly use the format: Output State: **the output state you calculate.**, and describe this output state in Natural language easily understandable by humans
"""

PROMPT_COMPLEX = """
You have been assigned the role of a program executor, responsible for simulating the execution of Python code. You will be provided with an initial state and a Python code snippet consisting of multiple lines. Your task is to execute all the lines in sequence and provide the output state after the entire code block has been run. Avoid describing how the program runs step-by-step for individual lines but instead focus on the combined effect of all lines. When a variable has a specific value, use that specific value directly for calculations.  

Include all the information from the precondition that remains valid after the code execution and update the values of any variables that are modified by the code. Provide the final state, icluding the state of all the variables after the execution of the code snippet. Use the text format: Output State: **output state**.

Here are some examples to help you understand the task:

Example 1:
Initial State: `a` is 5, `b` is 3
```
c = a + b
d = c * 2
```

Example Answer 1:
The first line assigns the value of `a + b` to `c`. Since `a` is 5 and `b` is 3, `c` becomes 8. The second line assigns the value of `c * 2` to `d`, making `d` equal to 16. No other variables are affected. 
Output State: **a is 5, b is 3, c is 8, d is 16**

Example 2:
Initial State: `x` is a positive integer
```
n= int(input())
x += n
```

Example Answer 2:
The first line assigns the integer value of the input to `n`. The second line increments `x` by the value of `n`. The value of `x` is a positive integer, and `n` is an integer. No other variables are affected.
Output State: **x is a positive integer equal to its original value plus n , n is an integer**

Example 3:
Initial State: `n` is 3, `total` is 1
```
total += n
pass
n= max(total, n)
```

Example Answer 3:
The first line increments `total` by the value of `n`, making `total` equal to 4. The second line does not affect any variables. The third line assigns the maximum value between `total` and `n` to `n`. Since `total` is 4, and n was 3, `n` becomes 4.
Output State: **n is 4, total is 4**

Your Task:
Initial State: {pre}
```
{program}
```
Now, please analyze the entire block of code and provide the final output state. List the impact of all lines on the program, check the previous values of affected variables, and calculate the states of the variables after the codeexecutes. Be as specific as possible, combining changes from all lines into a single coherent final state. Include all valid information from the precondition and update only what is modified by the code.
In your response strictly use the format: Output State: **the output state you calculate.**, and describe this output state in Natural language easily understandable by humans
"""
def extract_result(s: str, keyword: str):
    pattern = fr"{keyword}:\s*\*\*(.*?)\*\*"
    matches = re.findall(pattern, s, re.DOTALL)
    if matches:
        # Select the last match
        res = matches[-1]
        # Clean up the beginning and end of the string for any weird characters like * or newlines
        return res.strip(), True
    return s, False

# This is the main function, it completes the prompt, queries the model and extracts the result, meaining the output state of that program part
def complete_triple(incomplete_triple: Triple, model , retry=True):
    pre = print_state(incomplete_triple.precondition)
    program = pprint_cmd(incomplete_triple.command)
    prompt = PROMPT.format(pre=pre, program=program)
    response = model.query(prompt)
    post, found= extract_result(response, "Output State")
    if retry and not found:
        return complete_triple(incomplete_triple, model, retry=False)
    print("*" * 50)
    print(incomplete_triple)
    print(f"LLM post: {post}")
    return post

def complete_triple_batch(incomplete_triple: Triple, model, retry=True):
    if isinstance(incomplete_triple.command, list):
        if len(incomplete_triple.command) == 1:
            return complete_triple(incomplete_triple, model, retry=retry)
    pre = print_state(incomplete_triple.precondition)
    program = pprint_cmd(incomplete_triple.command)
    program=program.replace("\n\n","\n")
    prompt = PROMPT_COMPLEX.format(pre=pre, program=program)
    response = model.query(prompt)
    post, found = extract_result(response, "Output State")
    if retry and not found:
        return complete_triple_batch(incomplete_triple, model, retry=False)
    print("*" * 50)
    print(incomplete_triple)
    print(f"LLM post: {post}")
    return post
