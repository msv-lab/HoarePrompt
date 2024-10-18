from node_base_style.hoare_triple import TryTriple, pprint_cmd, print_state
from node_base_style.helper import extract_result

# The prompt template to instruct the model to summarize the final state of a try block
# The model is given the initial state, the try block code, and the except block code and as well as the intermidiate states after try and catch
# then it describes the overall state after both blocks are executed, including handling any exceptions.

PROMPT = """
You have been assigned the role of a program verifier, responsible for summarizing the state of the function after executing a Python `try` statement. You will be provided with the final state of the program after executing the `try` block, and the changes in the program after executing one or more `except` blocks in any situation. Please combine this information to summarize the program's state after the complete execution of the `try` statement. If there is a return always include it in the output sate. You must adhere to the text format: Output State: **output state**.


Example 1:
Program state after fully executing the `try` block:
Initial State: `a` is an integer, `b` is an integer.
```
result = a / b
return result
```
Program state after the execution of the `try` statement: `a` is an integer, `b` is an integer, `result` is the result of `a` divided by `b`, and the function returns `result`.


Changes in the program state after executing the `except` block :
Initial State: variables can hold any values.
```
return None
```
Program state after executing the except statement(s) : Except statement 1:The function return None.


Below is the initial program state and the complete `try` statement:
Initial State: `a` is an integer, `b` is an integer.
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

Example 2:

Program state after fully executing the `try` block:
Initial State: file_path is a string that's supposed to be a path to a file.
```
with open(file_path, 'r') as file:
        data = file.read()
        print("File content successfully read.")
        return data
```
Program state after the execution of the `try` statement: `file_path` is a string thats supposed to be a path to a file, data is the contents of that file and the function returns that content.


Changes in the program state after executing the `except` block :
Initial State: variables can hold any values.
```
Except 1:
    print("Error: The file was not found. Please check the file path.")
    return None

Except 2:
    print("Error: You do not have permission to read this file.")
    return None
```
Program state after executing the except statement(s) : Except statement 1:The function return None and prints "Error: The file was not found. Please check the file path." 
                                                        Except statement 2: The function return None and prints "Error: You do not have permission to read this file."

                                                        
Below is the initial program state and the complete `try` statement:
Initial State: file_path is a string that's supposed to be a path to a file.


```
def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = file.read()
            print("File content successfully read.")
            return data

    except FileNotFoundError:
        print("Error: The file was not found. Please check the file path.")
        return None

    except PermissionError:
        print("Error: You do not have permission to read this file.")
        return None
```

Now, please think step by step: At which point in the program could such an exception occur? What is the program's state after the `try` statement is executed?


Example Answer:
The program could raise a `FileNotFoundError` if the file is not found at the specified path or a `PermissionError` if the user does not have permission to read the file. If the file is found and the user has permission, the function reads the file content and returns it. Therefore: Output State: **file_path is a string that's supposed to be a path to a file. If the file is found and the user has permission, the function returns the file content, otherwise, it prints an error message and returns None.**


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

Program state after executing the except statement(s) : {except_post}
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
    # for every except block, pretty print the except block  an add execpt block {counter}: in front of it and new line after
    except_command_list=[]
    for i in range(len(incomplete_triple.except_command)):
       except_command_list.append( f"Except {i+1}:\n" + pprint_cmd(incomplete_triple.except_command[i].body))
    except_code = "\n".join(except_command_list)
    # except_code = pprint_cmd(incomplete_triple.except_command)
    except_post = incomplete_triple.except_post
    code = pprint_cmd(incomplete_triple.command)
    prompt = PROMPT.format(pre=pre, try_code=try_code, try_post=try_post, except_code=except_code,
                            except_post=except_post, code=code)
    response = model.query(prompt)
    post = extract_result(response, "Output State")
    return post
