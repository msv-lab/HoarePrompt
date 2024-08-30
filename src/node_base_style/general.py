import re

from node_base_style.hoare_triple import Triple, pprint_cmd

PROMPT = """
You have been assigned the task of a program state analyzer, responsible for analyzing the changes in the program's state after executing a Python code snippet. You will be given an initial state and a piece of Python code. You need to describe the program's state in natural language after the code executes. The program's state should only include the values of variables and the relationships between them, and when specific values can be calculated, prioritize using those specific values; please avoid describing how the program runs. Note that information in the initial state not affected by the program should not be omitted in the Output State. You must adhere to the text format: Output State: **output state.**


Example1:
Initial State: `str` is a string
```
n = int(input())
```
Example Answer:
`n` is assigned the value `int(input())`, where `input` accepts an input and `int` converts it to an integer. Other variables are not affected, so the output state is `str` is a string, `n` is an input integer.
Output State: **`str` is a string, `n` is an input integer**


Example2:
Initial State: variables can hold any values
```
i += 1
```
Example Answer:
The value of `i` is incremented by 1, but the previous value of `i` is unknown, so the output state is: variable `i` is increased by 1.
Output State: **variable `i` is increased by 1.**


Example3:
Initial State: `n` is either 3 or 5
```
m = n + 1
```
Example Answer:
m is assigned the value n + 1. The value of n can be 3 or 5, so the value of m is 4 or 6. Therefore, the Output State is: n is either 3 or 5; m is either 4 or 6.
Output State: **`n` is either 3 or 5; `m` is either 4 or 6.**


Example4:
Initial State: `x` is 1, `y` is 0, `z` is 0
```
y = x
```
Example Answer: 
`y` is assigned the value of `x`, and `x` is 1, so after execution, `y` is 1. The states of the other variables are not affected. Therefore, the Output State is: `x` is 1, `y` is 1, `z` is 0.
Output State: **`x` is 1, `y` is 1, `z` is 0.**


Your Task:
Initial State: {pre}
```
{program}
```
"""

def complete_triple(incomplete_triple: Triple, model):
    pre = incomplete_triple.precondition
    program = pprint_cmd(incomplete_triple.command)
    prompt = PROMPT.format(pre=pre, program=program)
    response = model.query(prompt)
    post = extract_postcondition(response)
    print("*" * 50)
    print(incomplete_triple)
    print(f"LLM post: {post}")
    return post


def extract_postcondition(s: str) -> str:
    pattern = r"Output State:\s*\*\*(.*?)\*\*"
    match = re.search(pattern, s, re.DOTALL)
    if match:
        return match.group(1)
    return s