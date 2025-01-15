from node_base_style.helper import extract_result

# while i < n:
#     total += i
#     i += 1
# This is the prompt that is used to get the precondition after entering the Loop after the current iteration
PROMPT = """
You have been assigned the task of a program verifier, responsible for modifying the program state so that the next iteration of the `while` loop can proceed. You will be provided with the program state after the previous iteration, which you need to modify. You will also see the `while` loop statement. If it is a `while True` loop or if the loop can certainly execute one more time, please simply repeat the program state at the end of the previous iteration. Please do not make any assumptions. You must adhere to the text format: State: **state**.
I am giving you 2 examples to understand the task better. Then I am giving you your task.



Example 1:
State at the end of the previous iteration: `total` is 10,  `i` is 4, `n` is greater than 3.
```
while i < n:
    # the loop body is omit
```
Now, please think step by step: Which states need to be adjusted for the loop to execute one more time? Only the states of objects in the loop head can be adjusted.


Example Answer:
The variables in the loop head are i and n, so we can only adjust them.. According to the code, whether the loop can execute depends on the variables `i` and `n`. If `i` is less than `n`, the loop can execute again. At the end of the last iteration, `i` is 4, `n` is greater than 3. `n` being greater than 3 does not ensure that the loop will execute again, so it needs to be adjusted to `n` is greater than 4. No other states need to be adjusted.
State: **`total` is 10, `i` is 4,  `n` must be greater than 4**

Example 2:
State at the end of the previous iteration: `total` is 0,  students is 3 less than its initial value.
```
while students >=1 :
    # the loop body is omit
```
Now, please think step by step: Which states need to be adjusted for the loop to execute one more time? Only the states of objects in the loop head can be adjusted.


Example Answer:
The only variable in the loop head is variable students, so we can only adjust that one.According to the code, whether the loop can execute depends on the variable students.  If students is greater than or equal to 1, the loop can execute again. At the end of the last iteration, students is 3 less than its initial value, So for the loop to be executed one more time the initial value of students needed to have been equal or greater than 4 and students currently must be greater than 1.
State: **`total` is 0, students is 3 less than its initial value and students currently must be greater or equal to 1**


Your Task:
State at the end of the previous iteration: {post}
```
{loop_head}
    # the loop body is omit
```
Now, please think step by step: Which states need to be adjusted for the loop to execute one more time? Only the states of objects in the loop head can be adjusted.
"""

# The function to get the precondition so that the next iteration can take place
def get_precondition(model, post: str, loop_head: str) -> str:
    prompt = PROMPT.format(post=post, loop_head=loop_head)
    response = model.query(prompt)
    pre = extract_result(response, "State")
    return pre
