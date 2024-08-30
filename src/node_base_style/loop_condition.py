import re

from node_base_style.hoare_triple import LoopTriple, pprint_cmd

WHILE_PROMPT = """
You have been assigned the task of a program verifier, responsible for analyzing the conditions under which the `while` loop can execute at least a specified number, denoted as `k`, of times. You will be provided with the conditions under which the loop can execute at least `k-1` times, along with how a single iteration of the loop body affects the variables as reference information. If the loop cannot execute the specified number of iterations, please respond with 'None'. If the conditions do not need to be changed, please repeat it unchanged. If the conditions need to be adjusted, modify only the necessary parts. You must adhere to the text format: Condition: **condition.**

Example:
Under what conditions can the loop execute at least 3 times?
The condition that allows the loop to execute at least 2 times: `sum` is 10, `x` is greater then 2.
```
while x > 0:
    sum += x
    x -= 1
```
The effect of the loop body on the variables: `sum` is increased by `x`, and then `x` is decremented by 1.
Please think step by step about the conditions under which the loop can be entered, whether and how the loop body affects the loop condition.
Example Answer:
When x is greater than 0, the loop is entered, meaning the loop executes at least once. Each iteration decrements x by 1, so if the loop is expected to execute at least 3 times, x needs to be greater than 3.
Condition: **`sum` is 10, `x` is greater than 3.**


Your Task:
Under what conditions can the loop execute at least {k} times?
The condition that allows the loop to execute at least {km1} times: {pre}
```
{program}
```
The effect of the loop body on the variables: {body_post}
Please think step by step about the conditions under which the loop can be entered, whether and how the loop body affects the loop condition.
"""

FOR_PROMPT = """
You have been assigned the task of a program verifier, responsible for analyzing the conditions under which a `for` loop can execute at least a specified number of iterations, denoted as `k`. The value of the loop variable before iteration `k` should also be provided as part of the condition. You will be given the conditions under which the loop can execute at least `k-1` times, along with information on how a single iteration of the loop body affects the variables as reference. If the loop cannot execute the specified number of iterations, please respond with 'None'. If the conditions do not need to be changed, please only update the value of the loop variable and leave the rest unchanged. If the conditions need to be adjusted, only modify the necessary parts. You must adhere to the text format: Condition: **condition.**

Example1:
Under what conditions can the loop execute at least 5 times? Before loop iteration 5, what is the state of the loop variable?
The condition that allows the loop to execute at least 4 times: `total_sum` is 10, `i` is 4.
```
for i in range(1, 6):
    total_sum += i
```
Please think step by step about how the loop variable changes during each iteration of the loop.
Example Answer:
When entering the first iteration of the loop, the loop variable `i` is 1, and each iteration increases `i` by 1. The loop can execute 5 times, and on the fifth iteration, the loop variable `i` is 5.
Condition: **`total_sum` is 10, `i` is 5.**


Example2:
Under what conditions can the loop execute at least 6 times? Before loop iteration 6, what is the state of the loop variable?
The condition that allows the loop to execute at least 5 times: `squares` is a list: `[0, 1, 4, 9, 16]`.
```
for i in range(5):
    squares.append(i ** 2)
```
Please think step by step about how the loop variable changes during each iteration of the loop.
Example Answer:
When entering the first iteration of the loop, the loop variable `i` is 0, and each iteration increases `i` by 1. The loop can execute a total of 5 times but cannot execute 6 times.
Condition: **None**


Example3:
Under what conditions can the loop execute at least 2 times? Before loop iteration 2, what is the state of the loop variable?
The condition that allows the loop to execute at least 1 times: `numbers` must have at least one elements, `number` is the first element of `numbers`.
```
for number in numbers:
    squared = number ** 2
    result.append(squared)
```
Please think step by step about how the loop variable changes during each iteration of the loop.
Example Answer:
The loop iterates over each element in numbers, so for the loop to run twice, `numbers` must have at least two elements. During the second iteration, `number` is the second element of `numbers`.
Condition: **`numbers` must have at least two elements, `number` is the second element of `numbers`.**


Your Task:
Under what conditions can the loop execute at least {k} times? Before loop iteration {k}, what is the state of the loop variable?
The condition that allows the loop to execute at least {km1} times: {pre}
```
{program}
```
Please think step by step about how the loop variable changes during each iteration of the loop.
"""


def get_condition(model, incomplete_triple: LoopTriple, n: int):
    program = pprint_cmd(incomplete_triple.command)
    body_post = incomplete_triple.body_postcondition
    if incomplete_triple.type == "for":
        pre = incomplete_triple.precondition
        prompt = FOR_PROMPT.format(program=program, k=n, body_post=body_post, pre=pre, km1=n-1)
    elif incomplete_triple.type == "while":
        pre = incomplete_triple.precondition
        prompt = WHILE_PROMPT.format(program=program, k=n, body_post=body_post, pre=pre, km1=n-1)
    else:
        raise ValueError("Unsupported loop type")

    response = extract_condition(model.query(prompt))
    print("*"*50)
    print(f'LLM pre for {n} iterations: {response}')
    print(response)
    return response


def extract_condition(s: str) -> str:
    pattern = r"Condition:\s*\*\*(.*?)\*\*"
    match = re.search(pattern, s, re.DOTALL)
    if match:
        return match.group(1)
    return s
