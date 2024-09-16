import ast

from node_base_style.hoare_triple import FuncTriple
from node_base_style.helper import extract_result

PROMPT = """
You have been assigned the task of a program verifier, responsible for describing the functionality of a Python function. You will be provided with the constraints and relationships between the input parameters, as well as the resulting output of the function based on these inputs. Your task is to organize this information and describe the functionality of the function. Please avoid describing how the function operates or details such as how local variables are initialized—only describe what parameters the function accepts and what it returns. You must adhere to the text format: Functionality: **functionality**.


Example:
Parameter constraints and relationships: `number` is an integer.
```
def func(number):
```
Output: `number` is an integer. If `number` is even, the function returns True; otherwise, it returns False.
Now, please think step by step: What are the parameters the function accepts, and the return value?


Example Answer:
The function `func` accepts a parameter `number`. `number` is an integer. After executing the function body, if number is even, the function returns `True`; otherwise, it returns `False`. Therefore, the functionality of the function func is to accept an integer `number`, and if `number` is even, it returns True. If `number` is not even, it returns False.
Functionality: **The function accepts a parameter number, returns `True` if `number` is even. If `number` is not even, it returns `False`.**


Your Task:
Parameter constraints: {pre}
```
{head}
```
Output: {body_post}
Now, please think step by step: What are the parameters the function accepts, and the return value?
"""


def complete_func_triple(incomplete_triple: FuncTriple, model):
    pre = incomplete_triple.precondition
    body_post = incomplete_triple.body_postcondition
    head = incomplete_triple.head
    prompt = PROMPT.format(pre=pre, body_post=body_post, head=head)
    response = model.query(prompt)
    post = extract_result(response, "Functionality")
    return post


def get_func_def(node: ast.FunctionDef):
    name = "func"
    args = [arg.arg for arg in node.args.args]
    args_str = ", ".join(args)
    return f"def {name}({args_str}):"
