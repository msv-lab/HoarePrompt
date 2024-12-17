import re

# This is the final step after the final post condition has been generated. This is the prompt template that will be filled in with the problem description, the program,
# and the final output hints (postcondition). It instructs the model to determine whether the program
# satisfies the description and output specification, and asks it to return either "True" or "False".

VERIFY_PROMPT_TEMPLATE_FUNCTION_SUMMARY = """
You have been assigned the role of a program verifier. Given a python program and a problem description, we have performed an initial assessment of the program's correctness. We also provide the reasoning behind our assessment. 
We are additionally providing you with some output hints that summarize the program's functionality.
Your task is to analyze the problem description, the program, and the original assessment. Use the provided output hints to systematically evaluate the program's behavior and reasoning. Based on the program, the output hints the problem description and the original assessment, determine the final correctness of the program.

Provide a final assessment of the program's correctness as follows:

If the program meets the problem description and the output hints support the correctness, output: Final: **True**
If the program does not meet the problem description, output: Final: **False**
Focus on evidence from the annotations and the original assesment to justify your conclusion. Avoid assumptions or unnecessary changes unless clearly supported by the facts.

You need to strictly follow the format Final: **True or False**.

# Your task:
Problem description: {description}
Program:
```
{program}
```
Original Assessment: {original_assessment}

Now we are giving you the output hints that summarize the code functionality and might give you examples of some of the cases that the code is not working correctly. Make sure that the output hints make sense. Also we assume that the input will be valid and will not cause any errors in the program. 
So for example if the program is supposed to accept a list but does not handle the case when the input is not a list or an empty list then the program isstill correct since we assume the user will always provide a valid input. The same if we expecta positive integer and the program does not handle the case when the input is negative or zero.
Output hints: {postcondition}

Does the original Assessment make sense based on the problem description and the provided code. 
Based on the output hints, the program  and your reasoning, provide a refined assessment of the program's correctness, either mintaining the original assessment or changing it if the output hints provide a different perspective.
Use all the information available to you to determine  the final correctness of the program based on the problem description. 
You need to strictly follow the format Final: **True or False**. If you believe the program is correct then Final: **True**. If you believe the program is incorrect then Final: **False**.
If you keep the original assessment then you need to provide a reason why you think the original assessment is accurate. If you change the original assessment then you need to provide a reason why you think the original assessment is not accurate.
"""

VERIFY_PROMPT_TEMPLATE_TREE = """
You have been assigned the role of a program verifier. Given a python program and a problem description, we have performed an initial assessment of the program's correctness. We also provide the reasoning behind our assessment. 
We are additionally providing you with the program again but this time we are providing you with an annotated version of the program. This annotated version provides the state of the program at different points in the program.
Your task is to analyze the problem description, the program, and the original assessment. Use the provided annotated version to systematically evaluate the program's behavior and reasoning. Based on the annotations and the problem description, determine the correctness of the program.

Provide a final assessment of the program's correctness as follows:

If the program meets the problem description and the annotations support the correctness, output: Final: **True**
If the program does not meet the problem description, output: Final: **False**
Focus on evidence from the annotations and the original assesment to justify your conclusion. Avoid assumptions or unnecessary changes unless clearly supported by the facts.

You need to strictly follow the format Final: **True or False**.

# Your task:
Problem description: {description}
Program:
```
{program}
```
Original Assessment: {original_assessment}

Now we are giving you an annotated version of the code describing states at different parts of the program. Make sure that the annotations make sense. 
Also we assume that the input of the program will be valid and will not cause any errors in the program. So for example if the program is supposed to accept a list but does not handle the case when the input is not a list or an empty list then the program is still correct since we assume the user will always provide a valid input. It will also not be a problem for example if for input the program expects a  positive integer and the program does not handle the case when the input is negative or zero.
Annotated code:
{postcondition}

Does the original Assessment make sense based on the problem description and the provided code. Based on the annotated version of the code  and your reasoning, provide a refined assessment of the program's correctness, either mintaining the original assessment or changing it if the annotated version provides a different perspective.
Use all the information available to you to determine  the final correctness of the program based on the problem description. 
You need to strictly follow the format Final: **True or False**. If you believe the program is correct then Final: **True**. If you believe the program is incorrect then Final: **False**.
If you keep the original assessment then you need to provide a reason why you think the original assessment is accurate. If you change the original assessment then you need to provide a reason why you think the original assessment is not accurate.
"""

# Parses the model response to see if it responded True or False

def extract_correctness_from_response(response_content: str) -> str:
    pattern = r"Final:\s*\*\*(.*?)\*\*|Final:\s*(True|False)"
    match = re.findall(pattern, response_content)
    if match:
        if match[-1][0]:
            return match[-1][0].strip()
        elif match[-1][1]:
            return match[-1][1].strip()
    return response_content

# This function handles the core logic for checking program correctness using a naive entailment approach.
def verify_function_summary(model, description, postcondition, program, original_assessment, module_name, config, cex_path=None):
    prompt = VERIFY_PROMPT_TEMPLATE_FUNCTION_SUMMARY.format(program=program,
                                                        description=description,
                                                        original_assessment= original_assessment,
                                                        postcondition=postcondition)
    
    response = model.query(prompt)
    result = extract_correctness_from_response(response)

    if result.lower() == 'true':
        return (True , response)
    if result.lower() == 'false':
        return (False , response)
    raise ValueError('failed to parse entailment checking response')

def verify_tree(model, description, postcondition, program, original_assessment, module_name, config, cex_path=None):
    prompt = VERIFY_PROMPT_TEMPLATE_TREE.format(program=program,
                                                        description=description,
                                                        original_assessment= original_assessment,
                                                        postcondition=postcondition)
    
    response = model.query(prompt)
    result = extract_correctness_from_response(response)

    if result.lower() == 'true':
        return (True , response)
    if result.lower() == 'false':
        return (False , response)
    raise ValueError('failed to parse entailment checking response')


# TBD: WHAT OTHER APPROACH CAN BE USED OTHER THAN NAIVE?