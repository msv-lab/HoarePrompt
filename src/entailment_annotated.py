import re

# This is the final step after the final post condition has been generated. This is the prompt template that will be filled in with the problem description, the program,
# and the final output hints (postcondition). It instructs the model to determine whether the program
# satisfies the description and output specification, and asks it to return either "True" or "False".

ENTAILMENT_CHECKING_PROMPT_TEMPLATE = """
You have been assigned the role of a program verifier. Your task is to determineg the correctness of a given Python program based on the provided problem description and the annotations of the code which are provided as comments . If the program is correct, that is it meets the requirements in the problem description, print "True"; otherwise, print "False". Partially correct programs should be considered incorrect. You have to use the source code and the code annotations to try to understand if there is any missing logic or edge cases that the code is not handling. 
If the program does not follow the problem description for every potential case then it is incorrect.Since if for at least one input or potential case the program does not work then Correctness **False**.
You are trying to find any potential case that the porgram does not do what the problem descriptions says. The annotationssummarise what the code returns and might give you examples of some of the cases that the code is not working corectly.
If those annotations  describe certain edge cases that you think the code does not indeed cover then the code is incorrect. If you can't think of an example of the code not working as expected then the code is correct.
You need to strictly follow the format Correctness: **True or False**.

# Your task:
Problem description: {description}
Annotated Program:
```
{annotated_program}
```


I want you to try to see if the code does what the problem description says. The code must follow the problem description for it to be correct!!
You can also use the code annotations to understand the code better. Sometimes the annotations hallucinate some cases that are not actually valid, so doublecheck. Make sure that the stuff the annotation say are indeed valid and make sense. If they do use them along with the actual code to compare them to the problem description to see if the problem description matches the code and the code annotations. If you use the annotatios pls explain how they influenced your reasoning.
Does the code follow the problem description for every potential case?
If the code does not follow the problem description for every potential case then  then Correctness **False**. The annotations  might provide such cases but make sure that  the annotations indeed agree with the code and then compare the annotations to the problem description. Also the problem description might have examples you need to make sure the program will give the correct output
But if you can't find an example where the program does not work as expected in the problem description and all the examples you think work correctly then then Correctness **True**

You need to strictly follow the format Correctness: **True or False**. Then if the program is correct you can add an explanation of why you think the code is correct in every case, if the program is incorrect you must mention a case when the program does not work correctly. You can also say how the annotations influenced your reasoning.
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

    if result.lower() == 'true':
        return (True , response)
    if result.lower() == 'false':
        return (False , response)
    raise ValueError('failed to parse entailment checking response')


# TBD: WHAT OTHER APPROACH CAN BE USED OTHER THAN NAIVE?