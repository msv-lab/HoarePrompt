import re

# This is the final step after the final post condition has been generated. This is the prompt template that will be filled in with the problem description, the program,
# and the final output hints (postcondition). It instructs the model to determine whether the program
# satisfies the description and output specification, and asks it to return either "True" or "False".

ENTAILMENT_CHECKING_PROMPT_TEMPLATE = """
You have been assigned the role of a program verifier. Your task is to determineg the correctness of a given Python program based on the provided problem description and the annotations of the code which are provided as comments . If the program is correct, that is it meets the requirements in the problem description, print "True"; otherwise, print "False". You need to strictly follow the format Correctness: **True or False**.

# Your task:
Problem description: {description}
Annotated Program:
```
{annotated_program}
```
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