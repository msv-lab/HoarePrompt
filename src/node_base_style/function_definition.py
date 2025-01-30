import ast

from node_base_style.hoare_triple import FuncTriple
import re

# This script handles functions to get its functionality
# A prompt template to query the language model (LLM) for verifying and describing the functionality of a Python function.
PROMPT = """
You have been assigned the task of a program verifier, responsible for describing the functionality of a Python function. You will be provided with the constraints and relationships between the input parameters, as well as the resulting output of the function based on these inputs. Your task is to organize this information and describe the functionality of the function. Please avoid describing how the function operates or details such as how local variables are initialized—only describe what parameters the function accepts and what it returns. If there are multiple return points in the function we will split them in Cases with an arithmetic counter and remember if one case is fullfilled none of the others are. You must adhere to the text format: Functionality: **functionality**.


Example1:
Parameter constraints and relationships: `number` is an integer.
```
def func(number):
```
Output: `number` is an integer. If `number` is even, the function returns True; otherwise, it returns False.
Now, please think step by step: What are the parameters the function accepts, and the return value?


Example Answer1:
The function `func` accepts a parameter `number`. `number` is an integer. After executing the function body, if number is even, the function returns `True`; otherwise, it returns `False`. Therefore, the functionality of the function func is to accept an integer `number`, and if `number` is even, it returns True. If `number` is not even, it returns False.
Functionality: **The function accepts a parameter number, returns `True` if `number` is even. If `number` is not even, it returns `False`.**


Parameter constraints and relationships: `age` is an integer.
```
def func(age):
```
Output: Case_1:`number` is an integer. If `number` is lower than 0, the function returns an error message that ages can't be negative; 
        Case_2: `number` is an integer. If `number` is between 0 and 18, the function returns "minor"; otherwise, it returns "adult".
Now, please think step by step: What are the parameters the function accepts, and the return value?


Example Answer:
The function `func` accepts a parameter `age`. `age` is an integer. If `age` is lower than 0, the function returns an error message that ages can't be negative. If `age` is between 0 and 18, the function returns "minor"; otherwise, it returns "adult". Therefore, the functionality of the function func is to accept an integer `age`  and return if the person is a minor or an adult based on the age while handling wrong negative input values.


Your Task:
Parameter constraints: {pre}
```
{head}
```
Output: {body_post}
Now, please think step by step: What are the parameters the function accepts, and the return value?
In your response strictly use the format: Functionality: **the functionality you calculate.**, and describe this functionality in Natural language easily understandable by humans
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

# This function completes the functionality of a function given its precondition, postcondition, and head
def complete_func_triple(incomplete_triple: FuncTriple, model, retry=True):
    pre = incomplete_triple.precondition
    body_post = incomplete_triple.body_postcondition
    head = incomplete_triple.head # The function signature, ehich is the function name and parameters
    prompt = PROMPT.format(pre=pre, body_post=body_post, head=head)
    response = model.query(prompt)
    post , found= extract_result(response, "Functionality")
    if retry and not found:
        return  complete_func_triple(incomplete_triple, model, retry=False)
    return post

# This function extracts the function definition (signature) from an AST node 
# It returns the function name and the list of parameters as a formatted string
def get_func_def(node: ast.FunctionDef):
    name = node.name
    args = [arg.arg for arg in node.args.args]
    args_str = ", ".join(args)
    return f"def {name}({args_str}):"
