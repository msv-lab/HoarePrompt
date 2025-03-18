import re

# This is the final step after the final post condition has been generated. This is the prompt template that will be filled in with the problem description, the program,
# and the final output description (postcondition). It instructs the model to determine whether the program
# satisfies the description and output specification, and asks it to return either "True" or "False".

ENTAILMENT_CHECKING_PROMPT_TEMPLATE = """
Your task is to determine if a given Python program is correct the based on the provided problem description and the execution summaries of its functions. You can use the execution summaries as a guides to understand the program’s behavior. Assume valid inputs as described in the problem.
The program is made of multiple functions and the program is **correct** only if all its functions together meet the problem description.
First explain your reasoning then reply Correctness: **True**  if the given program is correct or Correctness: **False**  if the given program is incorrect.


# Problem:
{description}

# Functions with Execution Summary:
{functions}

# Your response:
Reasoning:  
Correctness: **True** or **False**

"""


ENTAILMENT_CHECKING_PROMPT_TEMPLATE_old = """
You have been assigned the role of a program verifier. Your task is to determine the correctness of a given Python program based on the provided problem description and the description of program's output. If the program is correct, that is it meets the requirements in the problem description,  print Correctness: **True**; otherwise, print  Correctness: **False**. Partially correct programs should be considered incorrect. You have to use the source code and the Output hints to try to understand if there is any missing logic or edge cases that the code is not handling. 
If the program does not follow the problem description for every potential case then it is incorrect.Since if for at least one input or potential case the program does not work then Correctness **False**.
The output hints summarise the code functionality and might give you examples of some of the cases that the code is not working corectly, but make sure the hints agree with the code.
You need to strictly follow the format Correctness: **True or False**.

# Your task:
Problem description: {description}
Functions with output description for each function:
{functions}


Does the code do what  the problem description says,  for every potential case?
If the program does not follow the problem description for every potential case then  then Correctness **False**. The hints might provide such cases but make sure that the hints indeed agree with the code. Also the program description might have examples you need to make sure the program will give the correct output
But if you can't find an example where the program does not work as expected in the description and all the examples you think work correctly then then Correctness **True**
Also we assume that the input will be valid and will not cause any errors in the program. So for example if the program is supposed to accept a list but does not handle the case when the input is not a list or an empty list then the program isstill correct since we assume the user will always provide a valid input. The same if we expecta positive integer and the program does not handle the case when the input is negative or zero.
You need to strictly follow the format Correctness: **True or False**. Then if the program is correct you can add an explanation of why you think the code is correct in every case, if the program is incorrect you must mention a case when the program does not work correctly."""

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
def naive_mult_func(model, description, functions, module_name, config, cex_path=None):
    prompt = ENTAILMENT_CHECKING_PROMPT_TEMPLATE.format(functions=functions,
                                                        description=description)
    
    response = model.query(prompt)
    result = extract_correctness_from_response(response)

    if 'true' in result.lower().strip() :
        return (True, response)
    if "false" in result.lower().strip() :
        return (False, response)
    raise ValueError('failed to parse entailment checking response')

# TBD: WHAT OTHER APPROACH CAN BE USED OTHER THAN NAIVE?