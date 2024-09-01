import re

from node_base_style.hoare_triple import LoopTriple, pprint_cmd

CONDITION_PROMPT = """
You have been assigned the task of a program verifier. You need to determine the conditions under which the loop can execute at least a specified number of times. You must adhere to the text format: Condition: **condition.**


Example1:
Under what conditions can the following loop execute 5 times?
```
while x > 0:
    sum += x
    x -= 1
```
The impact on the variable each time the loop body is executed: `sum` increased by `x`, and `x` decreased by 1.
Now, please think step by step, list the conditions for the first few iterations of the loop, and then try to generalize.


Example Answer:
The number of times the loop can execute depends only on `x`. Each iteration of the loop increases `sum` by `x` and decreases `x` by 1. 

- If `x` is greater than 0, the loop can start.
- If `x` is greater than 1, the loop can execute at least 2 times.
- If `x` is greater than 2, the loop can execute at least 3 times.

Therefore, the condition for the loop to execute at least 5 times is: `x` is greater than 4.  
Condition: **x > 4**


Example2:
Under what conditions can the following loop execute 2 times?
```
for i in range(1, n):
    total_sum += i
```
The impact on the variable each time the loop body is executed: `total_sum` is increased by `i`.
Now, please think step by step, list the conditions for the first few iterations of the loop, and then try to generalize.


Example Answer:
The number of times the loop can execute depends only on `n`. The loop variable `i` starts at 1 and iterates up to (but not including) `n`, increasing by 1 each time.

- If `n` is greater than 1, the loop can start.
- If `n` is greater than 2, the loop can execute at least 2 times.

Therefore, the condition for the loop to execute at least 2 times is: `n` is greater than 2.
Condition: **n > 2**


Your Task:
Under what conditions can the following loop execute {k} times?
```
{program}
```
The impact on the variable each time the loop body is executed: {body_post}
Now, please think step by step, list the conditions for the first few iterations of the loop, and then try to generalize.
"""

VARIABLE_PROMPT = """
You have been assigned the task of a program verifier, responsible for extracting the value of the loop variable just before a specific iteration of a `for` loop. The loop variable refers to the local variable defined in the for loop header, which takes on different values in different iterations. Regardless of whether this variable is an underscore ('_') placeholder, you should still provide the value of the loop variable. Please note that any variables and operations within the loop body are not your concern. Focus only on the changes in the variable defined in the loop header. You must adhere to the text format: Variables: **variables.**


Example:
What is the value of the loop variable at the start of iteration 5?
```
for i in range(1, n):
    total_sum += i
```
Now, please think step by step: How does the loop variable change at the start of each iteration? List the results for the first few iterations, and then try to generalize.


Example Answer:
The loop variable `i` starts at 1 and iterates up to (but not including) `n`, increasing by 1 each time.

- At the start of the first iteration, `i = 1`.
- At the start of the second iteration, `i` increases by 1, so `i = 2`.
- At the start of the third iteration, `i` increases by 1, so `i = 3`.

Therefore, at the start of the fifth iteration, the loop variable `i = 5`.
Variables: **i = 5**


Your Task:
What is the value of the loop variable at the start of iteration {k}?
```
{program}
```
Now, please think step by step: How does the loop variable change at the start of each iteration? List the results for the first few iterations, and then try to generalize.
"""

COMBIN_PROMPT = """
You have been assigned the task of a program verifier, responsible for updating the program's state. You will be provided with an old program state and an update patch. Please apply the update to the old state. Please note that according to Python conventions, any variables with an underscore ('_') do not need to be written or updated in the state. You must adhere to the text format: New State: **new state.**


Example1:
Old State: `x` is 1, `y` is 2
Update: `x` is 2, `z` is 3

Example answer:
New State: **`x` is 2, `y` is 2, `z` is 3**


Example2:
Old State: `n` is an integer greater then 1
Update： `n` is an integer greater then 2


Example Answer:
New State: **`n` is an integer greater then 2**


Your Task:
Old State: {condition}
Update: {update}
"""


def get_conditions(model, incomplete_triple: LoopTriple, k: int) -> list[str]:
    conditions = []
    program = pprint_cmd(incomplete_triple.command)
    for i in range(1, k + 1):
        prompt = CONDITION_PROMPT.format(program=program, k=i, body_post=incomplete_triple.body_postcondition)
        response = model.query(prompt)
        condition = extract_result(response, "Condition")
        if incomplete_triple.type == "for":
            v_prompt = VARIABLE_PROMPT.format(k=i, program=program)
            v_response = model.query(v_prompt)
            loop_var = extract_result(v_response, "Variables")
            condition = condition + ", " + loop_var
        conditions.append(condition)

    return conditions


def combin_condition(model, condition: str, update: str) -> str:
    prompt = COMBIN_PROMPT.format(condition=condition, update=update)
    response = model.query(prompt)
    new_condition = extract_result(response, "New State")
    return new_condition


#
# WHILE_PROMPT = """
# You have been assigned the task of a program verifier, responsible for updating the program state so that the loop can execute at least a specified number of times. You will be provided with a Python `for` loop code snippet and the program state at the end of the previous iteration. You need to adjust the state so that the loop can execute at least one more time. You also need to adjust the loop variables to reflect the state just before the next iteration, as the `for` loop statement will change them between iterations. For states that do not require adjustment, simply repeat them as they were at the end of the previous iteration, since they will not change between iterations. The program state should only include the values of variables and the relationships between them. It should not include how the program runs or phrases like 'the variables remain as previously described.' You must adhere to the text format: Condition: **condition.**
# Now, please think step by step, list the conditions for the first few iterations of the loop, and then try to generalize.
#
#
# Example:
# Under what conditions can the loop execute at least 3 times?
# The condition that allows the loop to execute at least 2 times: `sum` is 10, `x` is greater than 2.
# ```
# while x > 0:
#     sum += x
#     x -= 1
# ```
# The effect of the loop body on the variables: `sum` is increased by `x`, and then `x` is decremented by 1.
# Please think step by step about the conditions under which the loop can be entered, whether and how the loop body affects the loop condition.
# Example Answer:
# When x is greater than 0, the loop is entered, meaning the loop executes at least once. Each iteration decrements x by 1, so if the loop is expected to execute at least 3 times, x needs to be greater than 3.
# Condition: **`sum` is 10, `x` is greater than 3.**
#
#
# Your Task:
# Under what conditions can the loop execute at least {k} times?
# The condition that allows the loop to execute at least {km1} times: {pre}
# ```
# {program}
# ```
# The effect of the loop body on the variables: {body_post}
# Please think step by step about the conditions under which the loop can be entered, whether and how the loop body affects the loop condition.
# """
#
# FOR_PROMPT = """
# You have been assigned the task of a program verifier, responsible for updating the program state so that the loop can execute at least a specified number of times. You will be provided with a Python `for` loop code snippet and the program state at the end of the previous iteration. You need to adjust the state so that the loop can execute at least one more time. You also need to update the variable controlled by the `for` loop statement itself (the variable that is directly modified by the loop header) to reflect the state just before the next iteration, as the `for` loop statement will change it between iterations. For states that do not require adjustment, simply repeat them as they were at the end of the previous iteration, since they will not change between iterations. The program state should only include the values of variables and the relationships between them, and should not include how the program runs or phrases like 'the variables remain as previously described.' When variables have specific values, you should directly calculate and use those specific values instead of describing how the variables change. You must adhere to the text format: Condition: **condition.**
#
# Example:
# Under what conditions can the loop execute at least 5 times? Before loop iteration 5, what is the state of the loop variable?
# State at the end of iteration 4: `n` is greater than 4, `total_sum` is 10, `i` is 4.
# ```
# for i in range(1, n):
#     total_sum += i
# ```
# Now, please think step by step: How can the loop reach the next iteration? What is the loop variable just before the loop executes?
# Example Answer:
# The number of loop iterations depends only on `n`. The loop iterates over the integers from 1 to `n` (excluding `n`), increasing by 1 each time. For the loop to execute at least 5 times, `n` should be greater than 5. Before the 5th iteration, the variable `i`, controlled by the for loop statement, is 5. `total_sum` is not related to whether the loop can execute one more time, therefore it should retain the state after the previous iteration. Therefore, the condition state is `n` is greater than 5, `total_sum` is 10, `i` is 5.
# Condition: **`n` is greater than 5, `total_sum` is 10, `i` is 5.**
#
#
# Your Task:
# Under what conditions can the loop execute at least {k} times? Before loop iteration {k}, what is the state of the loop variable?
# State at the end of iteration {km1}: {pre}
# ```
# {program}
# ```
# Now, please think step by step: How can the loop reach the next iteration? What is the loop variable just before the loop executes?
# """
#
#
# def get_condition(model, incomplete_triple: LoopTriple, n: int):
#     program = pprint_cmd(incomplete_triple.command)
#     body_post = incomplete_triple.body_postcondition
#     if incomplete_triple.type == "for":
#         pre = incomplete_triple.precondition
#         prompt = FOR_PROMPT.format(program=program, k=n, body_post=body_post, pre=pre, km1=n - 1)
#     elif incomplete_triple.type == "while":
#         pre = incomplete_triple.precondition
#         prompt = WHILE_PROMPT.format(program=program, k=n, body_post=body_post, pre=pre, km1=n - 1)
#     else:
#         raise ValueError("Unsupported loop type")
#
#     response = extract_result(model.query(prompt), "Condition")
#     print("*" * 50)
#     print(f'LLM pre for {n} iterations: {response}')
#     print(response)
#     return response
#

def extract_result(s: str, keyword: str) -> str:
    pattern = fr"{keyword}:\s*\*\*(.*?)\*\*"
    match = re.search(pattern, s, re.DOTALL)
    if match:
        return match.group(1)
    return s
