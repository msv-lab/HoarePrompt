from node_base_style.helper import extract_result

# while i < n:
#     total += i
#     i += 1
PROMPT = """
You have been assigned the task of a program verifier, responsible for modifying the program state so that the next iteration of the `while` loop can proceed. You will be provided with the program state after the previous iteration, which you need to modify. You will also see the `while` loop statement. You must adhere to the text format: State: **state**.


Example:
State at the end of the previous iteration: `total` is 10, `i` is 4, `n` is greater than 3.
```
while i < n:
    # the loop body is omit
```
Now, please think step by step: Which states need to be adjusted for the loop to execute one more time?


Example Answer:
According to the code, whether the loop can execute depends on the variables `i` and `n`. If `i` is less than `n`, the loop can execute again. At the end of the last iteration, `i` is 4, `n` is greater than 3. `n` being greater than 3 does not ensure that the loop will execute again, so it needs to be adjusted to `n` is greater than 4. No other states need to be adjusted.
State: **`total` is 10, `i` is 4, `n` is greater than 4**


Your Task:
State at the end of the previous iteration: {post}
```
{loop_head}
    # the loop body is omit
```
Now, please think step by step: Which states need to be adjusted for the loop to execute one more time?
"""


def get_precondition(model, post: str, loop_head: str) -> str:
    prompt = PROMPT.format(post=post, loop_head=loop_head)
    response = model.query(prompt)
    pre = extract_result(response, "State")
    return pre

