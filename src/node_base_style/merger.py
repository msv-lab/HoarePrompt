import re

from node_base_style.hoare_triple import Triple, pprint_cmd, print_state
from node_base_style.helper import extract_result


# This script's responsible for merging the output state of a program to a smaller output state so that the output state is easier to understand
PROMPT = """
You have been assigned the role of a program verifier, responsible for simulating the execution of Python code and finding the output state after some commands have been executed. You will be provided with an initial output state and a Python code snippet. You need to try to merge the output state into a smaller output state to try to summarise the functionality of what the initial output state was describing.  When a variable has a specific value, use that specific value directly for calculations. If a return takes place makes sure to always mention that a value or variable has been returned at the output state. You must adhere to the text format: Output State: **output state**.


Example1:
Initial Output state: 'i' is 1, 'n' is 'i+1'

Code that lead to the initial output state
```
i=1
n=i+1
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then try to merge the output state, summarising it.
Example Answer:
Since i is assigned 1, n is assigned i+1, which is 2. Therefore, the output state can be summarised as 'i' is 1, 'n' is 2.
Output State: **'i' is 1, 'n' is 2**


Example2:
Initial output state: if string 's' is empty then 'n' is 0, otherwise 'n' is len(s)

Code that lead to the initial output state
```
if s == "":
    n = 0
else:
    n = len(s)
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then try to merge the output state, summarising it.
Example Answer:
Since the code checks if the string 's' is empty or not, and assigns 0 to 'n' if it is empty, otherwise assigns the length of 's' to 'n'. Therefore, the output state can be summarised as 'n' holds the size of string 's'.
Output State: **variable 'n' holds the size of string 's'*


Example3:
Initial output State: 'n' can hold any value, result has been multiplied with 2 as many times as n

Code that lead to the initial output state
```
result=1
while i < n:
     result*= 2

```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then try to merge the output state, summarising it.
Example Answer:
result is originally 1 and then multiplied by 2 as many times as 'n'. Therefore, the output state can be summarised as 'result' is 2^n and 'n' can hold any value.
Output State: **'n' can hold any value and 'result' is 2^n**


Example4:
Initial output state: 'x', 'z' can hold any value, 'y' is x/z if the try succeds, otherwise 0 if an exception occurs

Code that lead to the initial output state
```
try:
    y =x/z
except ZeroDivisionError:
    y=0
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then try to merge the output state, summarising it.
Example Answer: 
A ZeroDivisionError exception is caught only if 'z' = 0, so 'x' , 'y' can hold any value, z=x/y if y!=0, otherwise 0. Therefore, the output state can be summarised as 'x' and 'z' can hold any value, 'y' is x/z if z!=0, otherwise 0 if 'z'=0.
Output State: **`'x' and 'z' can hold any value, 'y' is x/z if z!=0, otherwise 0 if 'z'=0**


Your Task:
Initial State: {pre}
```
{program}
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the merged Output State..
"""

# This is the main function, it completes the prompt, queries the model and extracts the result, meaining the output state of that program part
def merge_triple(incomplete_triple: Triple, model):
    pre = print_state(incomplete_triple.precondition)
    program = pprint_cmd(incomplete_triple.command)
    prompt = PROMPT.format(pre=pre, program=program)
    response = model.query(prompt)
    post = extract_result(response, "Output State")
    print("*" * 50)
    print(incomplete_triple)
    print(f"LLM post: {post}")
    return post
