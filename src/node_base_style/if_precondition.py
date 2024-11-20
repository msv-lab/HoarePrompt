from node_base_style.hoare_triple import IfTriple, parse_stmt, State,  pprint_cmd
from node_base_style.helper import extract_postcondition, format_prompt

# prompt template for asking the model to verify and describe if-statements
VERIFYER_SYSTEM_PROMPT_IF = """You are assigned the role of a program verifier, responsible for finding the postcondition of an if statement based on the condition of the if statement. You will be given the precondition, the if condition and you need to calculate the postcondition to take into account the condition of the if statement. The precondition and the postcondition are expressed in natural language.

Precondition: describes the initial state of the program variables before entering the if condition.
If condition: This is a given part of the task and is not something you need to create or modify. This is the condition to enter the if statement.

Postcondition: describes the state of the program variables after entering the if condition. So taking into account the precondition it must be extended so the if condition is also true. This description should include both the values of the variables and the relationships between them. Similar to the precondition, avoid explaining how the program operates; concentrate solely on the variable values and their interrelations. Ensure that the postcondition retains the conditions stated in the precondition. 
I am giving you some examples to understand the task better. Then I am giving you your task.
Follow the format Postcondition: **the calculated postcondition**

Example 1:
Precondition: `str` is a string
If condition:
```
if len(str) < 3:
```

Example Answer 1:
Postcondition: ***`str` is a string, and the lenght of the `str` is less than 3***


Example 2:
Precondition: `n` can have any value
if condition:
```
if isinstance(n, int):
```

Example Answer 2:
Postcondition: ***`n` is integer of any value`***

Example 3:
Precondition: `x` is an positive integer
if condition:
```
if x < 2:
```


Example Answer 3:
Postcondition: ***x is a positive less than 2***

Example 4:
Precondition: `m` is an integer, `n` is an integer, a is alist of integers
if condition:
```
if n < 0:
```


Example Answer 4:
Postcondition: ***`m`, `n` are integers. n is lower than 0, a is a list of integers***

Example 5:
Precondition: `x` is an integer, a is a list of integers.
if condition:
```
if a[0] != 0:
```

Example Answer 5:
Postcondition: ***`x` is an integer , a is a list of integers. The first element of a is not 0***

Your Task:
Precondition: {precondition}
if condition:
```
{program_fragment}
```
Your task is to complete the  postcondition . All the information of the precondition must be included in the postcondition. Give the overall state of the program for the program after it enters the if condition.
Follow the format Postcondition: **the calculated postcondition**
"""


# Function to complete the IfTriple by computing its overall postcondition using the model
def complete_if_precondition(precondition, if_condition, model):
    prompt = VERIFYER_SYSTEM_PROMPT_IF.format(precondition=precondition,
                                              program_fragment=if_condition)
    
    response = model.query(prompt)
    post = extract_postcondition(response)
    # print("*" * 50)
    # print(incomplete_triple)
    # print(f"LLM post: {post}")
    return post
