import re

from node_base_style.hoare_triple import Triple, pprint_cmd, print_state
# from node_base_style.helper import extract_result
import re

# This script's responsible for executing small code snippets and determining the resulting program state based on the provided initial state and program code. It is the general script for a simple program statement (not loops or ifs, try etc)

PROMPT_COMPLEX = """
You will be given an **initial state** (precondition) and a **Python code snippet** containing a `print` statement. Your task is to **determine exactly what will be printed** when the statement executes.

If a variable or object has a known **explicit value**, use that value in the output.
If a variable or object is defined by a **formula or condition**, describe its value using the given information.
Always provide the most **precise** description possible based on the precondition.
Format the final output as:  Output: **what is printed**.
I am giving you some examples to understand the task better. Then I am giving you your task:


Example1:
Initial State: `arr` is a list containing 1, 2, 3, 4, 5, and 'sum' is the sum of all elements in the list `arr`
```
print(arr[2], sum)
```
Example Answer:
The code prints the element at index 2 of the list `arr` which is 3, and the value of `sum` which is the sum of all elements in the list `arr`.
Output: **3, sum (where sum is the sum of all elements in list)]**

Example2:
Initial State: The poin ts list is a list of points. The `shoelace_sum` is the sum of all terms calculated as \(x_1 * y_2 - y_1 * x_2\) for each consecutive pair of points in the `points` list, the `area` is the absolute value of `shoelace_sum` divided by 2.0, `i` is equal to `len(points) - 2`, and `x1` is the first element of `points[i]`, `y1` is the second element of `points[i]`, while `x2` is the first element of `points[i + 1]`, and `y2` is the second element of `points[i + 1]`.
```
print(area)
```
Example Answer:
The `print(area)` statement will print the calculated area of the polygon formed by the points in the `points` list.
Since the exact `points` list is not provided, we can't compute the exact numerical value of `area`. However, based on the structure of the problem, the print statement will output the calculated area.
Output: **area (where area is the area of the polygon formed by the points in the `points` list)**

Example3:
Initial State: `balances` is a list of integers, `A` is the first element of the balances list, `B` is the second element of the balances list, and the amount is an integer  less than or equal to A.
```
print(f"The amount amount is less than or equal to A")
```
Example Answer:
The code prints a formatted string indicating whether the amount is less than or equal to A. Where A is the first element of the balances list and amount is an integer less than or equal to A.
Output: **The amount [amount] is less than or equal to [A] (where amount is the value of amount and A is the first element of the balances list)**
Your Task:
Initial State: {pre}
```
{program}
```
Now, please think step by step. Based on the precondition which describes the state of the program, variables , objects etc before the code is executed, calculate what will be printed when the print statement is executed. Explain the values of the variables, objects etc. that are printed.
Use natural language to describe the output, easily understandable by a human and strictly adhere to the format Output: **what is printed**.
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

# This is the main function, it completes the prompt, queries the model and extracts the result, meaining the output state of that program part
def complete_print_triple(incomplete_triple: Triple, model , retry=True):
    pre = print_state(incomplete_triple.precondition)
    program = pprint_cmd(incomplete_triple.command)
    prompt = PROMPT_COMPLEX.format(pre=pre, program=program)
    response = model.query(prompt)
    post, found= extract_result(response, "Output")
    if retry and not found:
        return complete_print_triple(incomplete_triple, model, retry=False)
    print("*" * 50)
    print(incomplete_triple)
    print(f"LLM post: {post}")
    return post


