from node_base_style.helper import extract_result

# while i < n:
#     total += i
#     i += 1
# This is the prompt that is used to get the precondition after entering the Loop after the current iteration
PROMPT = """
You have been assigned the task of a program verifier, responsible for understanding the program state at the start of the for loop. You will be provided with the program state after the previous iteration, which you need to modify. You will also see the for loop statement. Please do not make any assumptions. You must adhere to the text format: State: **state**.
I am giving you 2 examples to understand the task better. Then I am giving you your task.



Example 1:
State at the end of the previous iteration: `total` is 10, `i` is 3, `n` must be  greater than 3.
```
for i in range(n):
    # the loop body is omit
```
Now, please think step by step: Which states need to be adjusted at the start of the next iteration of the loop?


Example Answer:
According to the code, whether the loop can execute depends on the variables `i` and `n`. If `i` is less than `n`, the loop can execute again. At the end of the last iteration, `i` is 3, `n` is greater than 3. At the for the i is increased by 1 so i is 4 and for the loop to execute again n must be greater than 4.
State: **`total` is 10, `i` is 4, `n` must be  greater than 4**

Example 2:
State at the end of the previous iteration: `total` is 0, students_list is a list of students that must have at least 2 students, student is the second student in the list, index is 1 
```
for index, student in enumerate(students_list):
    # the loop body is omit
```
Now, please think step by step: Which states need to be adjusted for the loop to execute one more time?


Example Answer:
According to the code, whether the loop can execute depends on the student_list.  If the list has at least 3 students the loop executes again for the third time. At the end of the last iteration, students_list has at least 2 students, student is the second student in the list, index is 1. So for the loop to be executed one more time the list must have at least 3 students and the index is 2 and student is the trird student in the list.
State: **`total` is 0, students_list is a list of students that must have at least 3 students, student is the third student in the list, index is 3**


Your Task:
State at the end of the previous iteration: {post}
```
{loop_head}
    # the loop body is omit
```
Now, please think step by step: Which states need to be adjusted for the loop to execute one more time?
"""

# The function to get the precondition so that the next iteration can take place
def get_for_precondition(model, post: str, loop_head: str) -> str:
    prompt = PROMPT.format(post=post, loop_head=loop_head)
    response = model.query(prompt)
    pre = extract_result(response, "State")
    return pre
