from node_base_style.hoare_triple import TryTriple, pprint_cmd, print_state
# from node_base_style.helper import extract_result
import re

# The prompt template to instruct the model to summarize the final state of a try block
# The model is given the initial state, the try block code, and the except block code and as well as the intermidiate states after try and catch
# then it describes the overall state after both blocks are executed, including handling any exceptions.

PROMPT = """
You have been assigned the role of a program verifier, responsible for summarizing the state of the function after executing a Python `try` statement. You will be provided with the final state of the program after executing the `try` block, and the changes in the program after executing one or more `except` blocks in any situation. Please combine this information to summarize the program's state after the complete execution of the `try` statement. If there is a return always include it in the output sate. You must adhere to the text format: Output State: **output state**.
I am giving you some examples to understand the task better. Then I am giving you your task.


Example 1:

Initial State: `a` is an integer, `b` is an integer.
Code for the try except block:
```
try:
    result = a / b
    return result
except ZeroDivisionError:
    return None
```
Ouput state after the execution of the try statement: `a` is an integer, `b` is an integer, `result` is the result of `a` divided by `b`, and the function returns `result`.
Output state after the execution of the except statement(s): The function returns None if a ZeroDivisionError occurs.

Now, please think step by step: At which point in the program could such an exception occur? Summarise what the try except statement accomplishes and what the program output state is after it is executed.


Example Answer 1:
A `ZeroDivisionError` might be triggered at `result = a / b`. If `b` is 0, the `ZeroDivisionError` is raised, and the function returns `None`. Otherwise, the function returns the value of `a` divided by `b`. Therefore, the output state is: `a` and `b` are integers. If `b` is zero, the function returns `None`, otherwise, the function returns the value of `a` divided by `b`.
Output State: **`a` and `b` are integers. If `b` is zero, the function returns `None`, otherwise the function returns the value of `a` divided by `b`.**

Example 2:

Program state after fully executing the `try` block:
Initial State: file_path is a string that's supposed to be a path to a file.

Code for the try except block:
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
Output state after the execution of the try statement: `file_path` is a string that's supposed to be a path to a file, data is the contents of that file and the function returns that content.
Output state after the execution of the except statement(s):
Except statement 1:The function return None and prints "Error: The file was not found. Please check the file path." 
Except statement 2: The function return None and prints "Error: You do not have permission to read this file."

Now, please think step by step: At which point in the program could such an exception occur? Summarise what the try except statement accomplishes and what the program output state is after it is executed.


Example Answer 2 :
The program could raise a `FileNotFoundError` if the file is not found at the specified path or a `PermissionError` if the user does not have permission to read the file. If the file is found and the user has permission, the function reads the file content and returns it. 
Therefore: Output State: **file_path is a string that's supposed to be a path to a file. If the file is found and the user has permission, the function returns the file content, otherwise, it prints an error message and returns None.**


Your Task:

Initial State: {pre}
Code for the try except block:
```
{code}
```
Output state after the execution of the try statement: {try_post}
Output state after the execution of the except statement(s): 
{except_post}

Now, please think step by step: At which point in the program could such an exception occur? Summarise what the try except statement accomplishes and what the program output state is after it is executed. 
In your response strictly use the format: Output State: **the output state you calculate.**, and describe this output state in Natural language easily understandable by humans
"""
def extract_result(s: str, keyword: str):
    pattern = fr"{keyword}:\s*\*\*(.*?)\*\*"
    matches = re.findall(pattern, s, re.DOTALL)
    if matches:
        # Select the last match
        res = matches[-1]
        # Clean up the beginning and end of the string for any weird characters like * or newlines
        return res.strip(), True
    return s, False

# This function completes the postcondition for a TryTriple
# It constructs a prompt describing the try and except blocks, along with the initial state, and intermidiate states and sends it to the model.
def complete_try_triple(incomplete_triple: TryTriple, model, retry= True):
    pre = print_state(incomplete_triple.precondition)
    try_code = pprint_cmd(incomplete_triple.try_command)
    try_post = incomplete_triple.try_post
    # for every except block, pretty print the except block  an add execpt block {counter}: in front of it and new line after
    except_command_list=[]
    #if only one except command
    if len(incomplete_triple.except_command)==1:
        except_command_list.append( pprint_cmd(incomplete_triple.except_command[0].body))
    else:
        for i in range(len(incomplete_triple.except_command)):
            except_command_list.append( f"Except statement {i+1}:\n" + pprint_cmd(incomplete_triple.except_command[i].body))
    # if except command list is empty
    if not except_command_list:
        except_code = "There is no except block"
    else:
        except_code = "\n".join(except_command_list)
    # except_code = "\n".join(except_command_list)
    # except_code = pprint_cmd(incomplete_triple.except_command)
    except_post = incomplete_triple.except_post
    code = pprint_cmd(incomplete_triple.command)
    prompt = PROMPT.format(pre=pre, try_code=try_code, try_post=try_post, except_code=except_code,
                            except_post=except_post, code=code)
    response = model.query(prompt)
    post, found = extract_result(response, "Output State")
    if retry and not found:
        return complete_try_triple(incomplete_triple, model, retry=False)
    return post
