from node_base_style.hoare_triple import TryTriple, pprint_cmd, print_state
from node_base_style.helper import extract_result

# The prompt template to instruct the model to summarize the final state of a try block
# The model is given the initial state, the try block code, and the except block code and as well as the intermidiate states after try and catch
# then it describes the overall state after both blocks are executed, including handling any exceptions.

PROMPT = """
You have been assigned the role of a program verifier, responsible for summarizing the state of the function after executing a Python `try` statement. You will be provided with the final state of the program after executing the `try` block, and the changes in the program after executing the `except` block in any situation. Please combine this information to summarize the program's state after the complete execution of the `try` statement.


Example:
Program state after fully executing the `try` block:
Initial State: `a` is an integer, `b` is an integer.
```
result = a / b
return result
```
Program state after the execution of the `try` statement: `a` is an integer, `b` is an integer, `result` is the result of `a` divided by `b`, and the function returns `result`.


Changes in the program state after executing the `except` block in any case:
Initial State: variables can hold any values.
```
return None
```
Program state after executing the except statement in any case: The function return None.


Below is the initial program state and the complete `try` statement:
```
try:
    result = a / b
    return result
except ZeroDivisionError:
    return None
```
Now, please think step by step: At which point in the program could such an exception occur? What is the program's state after the `try` statement is executed?


Example Answer:
A `ZeroDivisionError` might be triggered at `result = a / b`. If `b` is 0, the `ZeroDivisionError` is raised, and the function returns `None`. Otherwise, the function returns the value of `a` divided by `b`. Therefore, the output state is: `a` and `b` are integers. If `b` is zero, the function returns `None`, otherwise, the function returns the value of `a` divided by `b`.
Output State: **`a` and `b` are integers. If `b` is zero, the function returns `None`, otherwise the function returns the value of `a` divided by `b`.**


Your Task:
Program state after fully executing the `try` block:
Initial State: {pre}
```
{try_code}
```
Program state after the execution of the `try` statement: {try_post}


Changes in the program state after executing the `except` block in any case:
Initial State: variables can hold any values.
```
{except_code}
```


Below is the initial program state and the complete `try` statement:
Initial State: {pre}
```
{code}
```
Now, please think step by step: At which point in the program could such an exception occur? What is the program's state after the `try` statement is executed?
"""

# This function completes the postcondition for a TryTriple
# It constructs a prompt describing the try and except blocks, along with the initial state, and intermidiate states and sends it to the model.
def complete_try_triple(incomplete_triple: TryTriple, model):
    pre = print_state(incomplete_triple.precondition)
    try_code = pprint_cmd(incomplete_triple.try_command)
    try_post = incomplete_triple.try_post
    except_code = pprint_cmd(incomplete_triple.except_command)
    except_post = incomplete_triple.except_post
    code = pprint_cmd(incomplete_triple.command)
    prompt = PROMPT.format(pre=pre, try_code=try_code, try_post=try_post, except_code=except_code,
                            except_post=except_post, code=code)
    response = model.query(prompt)
    post = extract_result(response, "Output State")
    return post
