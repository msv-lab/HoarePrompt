# from node_base_style.helper import extract_result
import re

# while i < n:
#     total += i
#     i += 1
# This is the prompt that is used to get the precondition after entering the Loop after the current iteration
PROMPT = """
You have been assigned the task of a program verifier, responsible for modifying the program state so that the first iteration of the `while` loop can proceed. You will be provided with the program state right before the loop, which you need to modify. You will also see the `while` loop statement. If it is a `while True` loop or if the loop can certainly execute one time, please simply repeat the program state right before the loop. You must adhere to the text format: State: **state**.
I am giving you 2 examples to understand the task better. Then I am giving you your task.



Example 1:
State right before the while loop: `total` is 10, `i` is 0, `n` is an integer.
```
while i < n:
    # the loop body is omit
```
Now, please think step by step: Which states need to be adjusted for the loop to execute the first time? Only the states of objects in the loop head can be adjusted.


Example Answer:
The only variables in the loop head are variables  i and n, so we can only adjust those ones. According to the code, whether the loop can execute depends on the variables `i` and `n`. If `i` is less than `n`, the loop can execute. Right before the loop, `i` is 0, `n` is an integer. `n` beinng an integer does not ensure that the loop will execute, so it needs to be adjusted to `n` is greater than 0. No other states need to be adjusted.
State: **`total` is 10, `i` is 0, `n` must be greater than 0**

Example 2:
State right before the while loop: `total` is 0, students is 2 less than its initial value.
```
while students >=1 :
    # the loop body is omit
```
Now, please think step by step: Which states need to be adjusted for the loop to execute the first time? Only the states of objects in the loop head can be adjusted.


Example Answer:
The only variable in the loop head is variable students, so we can only adjust that one. According to the code, whether the loop can execute depends on the variable students.  If students is greater than or equal to 1, the loop can execute . Rigtht before the loop, students is 2 less than its initial value, So for the loop to  executed the first time time the initial value of students needed to have been equal or greater than 3 and students currently must be greater than 1.
State: **`total` is 0, students is 2 less than its initial value and students currently must be greater or equal to 1**


Your Task:
State right before the while loop: {post}
```
{loop_head}
    # the loop body is omit
```
Now, please think step by step: Which states need to be adjusted for the loop to execute the first time ? Only the states of objects in the loop head can be adjusted.
"""

def extract_result(s: str, keyword: str) :
    pattern = fr"{keyword}:\s*\*\*(.*?)\*\*"
    matches = re.findall(pattern, s, re.DOTALL)
    if matches:
        # Select the last match
        res = matches[-1]
        # Clean up the beginning and end of the string for any weird characters like * or newlines
        return res.strip(), True
    return s, False


# The function to get the precondition so that the next iteration can take place
def get_while_precondition_first(model, post: str, loop_head: str, retry= True) -> str:
    prompt = PROMPT.format(post=post, loop_head=loop_head)
    response = model.query(prompt)
    pre, found = extract_result(response, "State")
    if retry and not found:
        return  get_while_precondition_first(model, post, loop_head, retry=False)
    return pre
