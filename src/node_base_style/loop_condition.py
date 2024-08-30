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
You have been assigned the task of a program verifier, responsible for updating the program state so that a `for` loop can execute at least a specified number of times. You also need to add or update the loop variables to reflect the state just before the specified iteration. If it is impossible for the loop to execute at least the specified number of times, please respond with 'None.' You will be provided with the state after executing the previous iteration as the initial state. You need to modify it so that the loop can execute at least one more time. lease note, you only need to change the initial condition to allow the next iteration. For variables in the initial state that do not require modification, please repeat them in the condition, as they are already in the state after the previous iteration. You must adhere to the text format: Condition: **condition.**

Example1:
Under what conditions can the loop execute at least 5 times? Before loop iteration 5, what is the state of the loop variable?
State at the end of iteration 4: `n` is greater then 4, `total_sum` is 10, `i` is 4.
```
for i in range(1, n):
    total_sum += i
```
Now, please think step by step: How can the loop reach the next iteration? What is the loop variable just before the loop executes?
Example Answer:
The number of loop iterations depends only on `n`. The loop iterates over the integers from 1 to `n` (excluding `n`), increasing by 1 each time. For the loop to execute at least 5 times, `n` should be greater than 5. Before the 5th iteration, the loop variable `i` is 5. `total_sum` is not related to whether the loop can execute, therefore it should retain the state after the previous iteration, i.e., `total_sum = 10`. Therefore, the condition state is `n` is greater than 5, `total_sum` is 10, `i` is 5.
Condition: **`n` is greater then 5, `total_sum` is 10, `i` is 5.**


Example2:
Under what conditions can the loop execute at least 6 times? Before loop iteration 6, what is the state of the loop variable?
State at the end of iteration 5: `squares` is a list: `[0, 1, 4, 9, 16]`.
```
for i in range(5):
    squares.append(i ** 2)
```
Now, please think step by step: How can the loop reach the next iteration? What is the loop variable just before the loop executes?
Example Answer:
This is a fixed-count loop that can only run 5 times, so it cannot execute 6 times under any conditions.
Condition: **None**


Your Task:
Under what conditions can the loop execute at least {k} times? Before loop iteration {k}, what is the state of the loop variable?
State at the end of iteration {km1}: {pre}
```
{program}
```
Now, please think step by step: How can the loop reach the next iteration? What is the loop variable just before the loop executes?
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
