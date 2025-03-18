import re

# This is the final step after the final post condition has been generated. This is the prompt template that will be filled in with the problem description, the program,
# and the final output hints (postcondition). It instructs the model to determine whether the program
# satisfies the description and output specification, and asks it to return either "True" or "False".

ENTAILMENT_CHECKING_PROMPT_TEMPLATE = """
Your task is to determine if a given Python program is correct based on the problem description and the execution states of the program provided as comments. Assume valid inputs as described in the problem description.

First explain your reasoning  then reply Correctness: **True**  if the given program is correct or Correctness: **False**  if the given program is incorrect.


# Problem:
{description}

# Annotated Program:
{annotated_program}

# Your response:
Reasoning:  
Correctness: **True** or **False**

"""

ENTAILMENT_CHECKING_PROMPT_TEMPLATE_old = """
You have been assigned the role of a program verifier. Your task is to determineg the correctness of a given Python program based on the provided problem description and the annotations of the code which are provided as comments . If the program is correct, that is it meets the requirements in the problem description, print "True"; otherwise, print "False". You need to strictly follow the format Correctness: **True or False**.

# Your task:
I am now giing you the problem description. This is what the function must do.
PROBLEM DESCRIPTION: {description}
This was the problem description. Lets move on to the  annotated program. The program must do what the problem description says for it to be correct.

Annotated Program:
```
{annotated_program}
```
The program is correct only if it meets the problem description! The problem description is defined before the program.  
Also we assume that the input will be valid and will not cause any errors in the program. So for example if the program is supposed to accept a list but does not handle the case when the input is not a list or an empty list then the program isstill correct since we assume the user will always provide a valid input. The same if we expecta positive integer and the program does not handle the case when the input is negative or zero.

Return Correctness: **True** if the program follows the problem description, otherwise return Correctness: **False** if the program does not do what the problem description asks for for every potential case.
If the program is correct explain why it always does what the problem description say. If it is incorrect explain why it does not do what the problem description says or a case where it doesnot follow the problem description.
"""

# Parses the model response to see if it responded True or False

def extract_correctness_from_response(response_content: str) -> str:
    pattern = r"Correctness:\s*\*\*(.*?)\*\*|Correctness:\s*(True|False)"
    match = re.findall(pattern, response_content)
    if match:
        if match[-1][0]:
            return match[-1][0].strip()
        elif match[-1][1]:
            return match[-1][1].strip()
    return response_content

# This function handles the core logic for checking program correctness using a naive entailment approach.
def naive(model, description, return_str, annotated_func, module_name, config, cex_path=None):
    prompt = ENTAILMENT_CHECKING_PROMPT_TEMPLATE.format(annotated_program=annotated_func,
                                                        description=description,
                                                        return_str=return_str)
    
    response = model.query(prompt)
    result = extract_correctness_from_response(response)

    # if result.lower() == 'true':
    #     return (True , response)
    # if result.lower() == 'false':
    #     return (False , response)
    # raise ValueError('failed to parse entailment checking response')

    if 'true' in result.lower().strip() :
        return (True, response)
    if "false" in result.lower().strip() :
        return (False, response)
    raise ValueError('failed to parse entailment checking response')


# TBD: WHAT OTHER APPROACH CAN BE USED OTHER THAN NAIVE?