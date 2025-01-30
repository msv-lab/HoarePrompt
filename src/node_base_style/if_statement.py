from node_base_style.hoare_triple import IfTriple, parse_stmt, State,  pprint_cmd, pprint_if_else, pprint_outer_if_else
# from node_base_style.helper import extract_postcondition, format_prompt
import re
# prompt template for asking the model to verify and describe if-statements
VERIFYER_SYSTEM_PROMPT_IF = """You are assigned the role of a program verifier, responsible for completing the overall postcondition of Hoare triples for if statements based on the postconditions of the if and the else part. In addition to the Hoare triples, you will also see the postconditions for the if and else parts. Each Hoare triple is made up of three components: a precondition, a program fragment, and a postcondition. The precondition and the postcondition are expressed in natural language.

Precondition: describes the initial state of the program variables before the execution of the program fragment. This description should only include the values of the variables, without detailing the operational aspects of the program.

Program Fragment: This is a given part of the task and is not something you need to create or modify. This contains the condition of the if statement and if there is an else part there will also be an else: in the program fragment.

Postcondition: describes the state of the program variables after the execution of the program fragment with the initial state described in the precondition. This description should include both the values of the variables and the relationships between them. Similar to the precondition, avoid explaining how the program operates; concentrate solely on the variable values and their interrelations. Ensure that the postcondition retains the conditions stated in the precondition. You need to strictly follow the format and summarize the if statement in a coherent paragraph, rather than discussing it in separate paragraphs.

The if part : the postcondition of the if part

The else part : the postcondition of the else part

Combine the postconditions of the if and else part(if an else exists), taking into account the if condition,  to get the overall postcondition of the if else block

I am giving you some examples to understand the task better. Then I am giving you your task.
Follow the format Postcondition: **the calculated postcondition**

Example 1:
Precondition: `str` is a string
Program Fragment:
```
if len(str) < 3:
```
If part: `str` is a string with lenght less than 3, the function returns None
Else part: there is no else part in the code

Example Answer 1:
Postcondition: ***`str` is a string, if the length of `str` is less then 3, the function return None***


Example 2:
Precondition: `n` can have any value
Program Fragment:
```
if isinstance(n, int):
    
else:
    
```

If part: n is an integer of any value and the function returns `n`
Else part: n can have any value except an integer one and the function returns `int(n)`

Example Answer 2:
Postcondition: ***if `n` is integer, then the function returns `n` itself. Otherwise, the function return `int(n)`***

Example 3:
Precondition: `x` is an positive integer
Program Fragment:
```
if x < 2:
   
else:
    
```

If part: `x` is an positive integer less than 2, the function returns False
Else part: `x` is an positive integer larger or equal to 2 and the function returns True

Example Answer 3:
Postcondition: ***x is a positive integer, if x is less then 2, the function return False. Otherwise, the function return True***

Example 4:
Precondition: `m` is an integer, `n` is an integer
Program Fragment:
```
if n < 0:
    
else:
    
```
if part: the integer n was originally negative and `n` is updated to its negation. Integer `m` is increased by 1
else part: if n is 0 then return m , otherwise the integer `n` is decreased by 13. Integer `m` is increased by 1

Example Answer 4:
Postcondition: ***`m`, `n` are integers. If n < 0, `m` is increased by 1 and `n` is negated. If n == 0, the function returns `m`. Otherwise, `n` is decreased by 13 and `m` is increased by 1.***

Example 5:
Precondition: `x` is an integer, y is zero.
Program Fragment:
```
if x > 0:
```
If part: `x` is a positive integer, if `x` > 10, `y` is set to twice the value of `x`. Otherwise, `y` is set to the value of `x` plus 5.
Else part: there is no else part in the code

Example Answer 5:
Postcondition: ***`x` is an integer. If `x` > 10, `y` is set to twice the value of `x`. If x is larger than 0 but lower than 10, `y` is set to the value of `x` plus 5.***

Your Task:
Precondition: {precondition}
Program Fragment:
```
{program_fragment}
```
if part: {postconditions_if}
else part: {postconditions_else}

Your task is to complete the overall postcondition of the whole if else block. Summarise all the cases and give the overall postcondition of the program after the if else executes.
In your response strictly use the format: Postocndition: **the postocndition you calculate.**, and describe this postcondition in Natural language easily understandable by humans
"""

def extract_postcondition(s: str) :
    pattern = r"Postcondition:\s*\*\*(.*?)\*\*"
    matches = re.findall(pattern, s, re.DOTALL)
    if matches:
        # Select the last match
        res = matches[-1]
        # Clean up the beginning and end of the string for any weird characters like * or newlines
        return res.strip(), True
    return s, False
# Function to complete the IfTriple by computing its overall postcondition using the model
def complete_if_triple(incomplete_triple: IfTriple, model, retry=True):
    program = pprint_outer_if_else(incomplete_triple.command)
    prompt = VERIFYER_SYSTEM_PROMPT_IF.format(precondition=incomplete_triple.precondition,
                                              program_fragment=program,
                                              postconditions_if=incomplete_triple.if_postcondition,
                                              postconditions_else=incomplete_triple.else_postcondition)
    
    response = model.query(prompt)
    post, found = extract_postcondition(response)
    if retry and not found:
        return complete_if_triple(incomplete_triple, model, retry=False)
    # print("*" * 50)
    # print(incomplete_triple)
    # print(f"LLM post: {post}")
    return post
