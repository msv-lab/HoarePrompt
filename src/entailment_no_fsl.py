import re

# This is the final step after the final post condition has been generated. This is the prompt template that will be filled in with the problem description, the program,
# and the final output hints (postcondition). It instructs the model to determine whether the program
# satisfies the description and output specification, and asks it to return either "True" or "False".

ENTAILMENT_CHECKING_PROMPT_TEMPLATE = """
You have been assigned the role of a program verifier. Your task is to determine the correctness of a given Python program based on the provided problem description and the description of program's output. If the program is correct, that is it meets the requirements in the problem description, print Correctness: **True**; otherwise, print Correctness: **False**. Partially correct programs should be considered incorrect. You have to use the source code and the Output hints to try to understand if there is any missing logic or edge cases that the code is not handling. 
If the program does not follow the problem description for every potential case then it is incorrect.Since if for at least one input or potential case the program does not work then Correctness **False**.
The output hints summarise the code functionality and might give you examples of some of the cases that the code is not working corectly, but make sure that the output hints make sense.
You need to strictly follow the format Correctness: **True or False**.

# Your task:
Problem description: {description}
Program:
```
{program}
```
Output hints: {postcondition}

Does the code do what the problem description says,  for every potential case?
If the program does not follow the problem description for every potential case then  then Correctness **False**. The hints might provide such cases but make sure that the hints indeed agree with the code. Also the program description might have examples you need to make sure the program will give the correct output
But if you can't find an example where the program does not work as expected in the description and all the examples you think work correctly then then Correctness **True**

You need to strictly follow the format Correctness: **True or False**. Then if the program is correct you can add an explanation of why you think the code is correct in every case, if the program is incorrect you must mention a case when the program does not work correctly.
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
def naive(model, description, postcondition, program, module_name, config, cex_path=None):
    prompt = ENTAILMENT_CHECKING_PROMPT_TEMPLATE.format(program=program,
                                                        description=description,
                                                        postcondition=postcondition)
    
    response = model.query(prompt)
    result = extract_correctness_from_response(response)

    if result.lower() == 'true':
        return (True , response)
    if result.lower() == 'false':
        return (False , response)
    raise ValueError('failed to parse entailment checking response')


# TBD: WHAT OTHER APPROACH CAN BE USED OTHER THAN NAIVE?