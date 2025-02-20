# from node_base_style.helper import extract_result
import re
# while i < n:
#     total += i
#     i += 1
# This is the prompt that is used to get the precondition after entering the Loop after the current iteration
PROMPT = """
You have been assigned the task of a program verifier, responsible for understanding the program state at the start of the for loop. You will be provided with the program state before the first execution of the for loop, which you need to modify. You will also see the for loop statement. Please do not make any assumptions. You must adhere to the text format: State: **state**.
I am giving you 2 examples to understand the task better. Then I am giving you your task.



Example 1:
State before the for loop: `total` is 10.
```
for i in range(n):
    # the loop body is omit
```
Now, please think step by step: Which states need to be adjusted for the loop to execute? Only the states of objects in the loop head can be adjusted.


Example Answer 1:
The only variables in the loop head are variables  i and n, so we can only adjust those ones. According to the code, whether the loop can execute depends on the variables `i` and `n`. If n is at least 1, the loop can execute. Before the loop starts, total is 10 does not ensure that the loop will execute , so it needs to be adjusted to `n` is greater than 0 and i is now 1. 
State: **`total` is 10, `i` is 1,  `n` must be greater than 0**

Example 2:
State before the loop starts: `total` is 0, students_list is a list of students.
```
for index, student in enumerate(students_list):
    # the loop body is omit
```
Now, please think step by step: Which states need to be adjusted for the loop to execute? Only the states of objects in the loop head can be adjusted.


Example Answer 2:
The only objects in the loop head are variables  index, students  and list  students_list, so we can only adjust those ones.According to the code, whether the loop can execute depends on the student_list.  If the list has at least 1 student the loop executes. At the end of the last iteration, total is 0. So for the loop to be executed  the list must have at least 1 student and the index is 0 and student is the first student in the list.
State: **`total` is 0,  students_list is a list of students that must have at least 1 student, student is the first student in the list, index is 0**


Your Task:
State before the loop starts: {post}
```
{loop_head}
    # the loop body is omit
```
Now, please think step by step: Which states need to be adjusted for the loop to execute? Only the states of objects in the loop head can be adjusted.
"""

def extract_result(s: str, keyword: str):
    pattern = fr"{keyword}:\s*\*\*(.*?)\*\*"
    matches = re.findall(pattern, s, re.DOTALL)
    if matches:
        # Select the last match
        res = matches[-1]
        # Clean up the beginning and end of the string for any weird characters like * or newlines
        return res.strip() , True
    return s, False

# The function to get the precondition so that the next iteration can take place
def get_for_precondition_first(model, post: str, loop_head: str, retry= True) -> str:
    prompt = PROMPT.format(post=post, loop_head=loop_head)
    response = model.query(prompt)
    pre,found  = extract_result(response, "State")
    if retry and not found:
        return get_for_precondition_first(model, post, loop_head, retry=False)
    return pre


