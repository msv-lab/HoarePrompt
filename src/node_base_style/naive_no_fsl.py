import re

# from node_base_style.hoare_triple import Triple, pprint_cmd, print_state
# from node_base_style.helper import extract_result


# This script's responsible for executing small code snippets and determining the resulting program state based on the provided initial state and program code. It is the general script for a simple program statement (not loops or ifs, try etc)
PROMPT = """
You will be provided with a function description and a Python function code snippet. You need to provide if the code does what the function description says. Please avoid describing how the program runs. If the code satisfies the description reply CORRECT, otherwise reply INCORRECT with an explanation. You must adhere to the text format: RESULT: **Correct or Incorrect**.

Description: {description}
Python Fucntion:
```
{code}
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
Use the format: RESULT: **Correct or Incorrect**.
"""

# PROMPT_COMPLEX = """
# You have been assigned the role of a program verifier. Your task is to determine the correctness of a given Python program based on the provided problem description. If the program is correct, that is it meets the requirements in the problem description, print "True"; otherwise, print "False". Partially correct programs should be considered incorrect. You have to use the source code to try to understand if there is any missing logic or edge cases that the code is not handling. 
# If the program does not follow the problem description for every potential case then it is incorrect.Since if for at least one input or potential case the program does not work then Correctness **False**.
# You are trying to find any potential case that the porgram does not does what the descriptions says.  If you can't think of an example of the ocde not working as expected then the code is correct.
# You need to strictly follow the format Correctness: **True or False**.

# # Your task:
# Problem description: {description}
# Program:
# ```
# {code}
# ```


# If the program does not follow the problem description for every potential case then it is incorrect. Then if even for one input or potential case the program does not work then Correctness **False** .You are trying to find any potential case that the porgram does not does what the descriptions says. But if you cant find an example where the program does not work as expected in the description and all the examples you think work correctly then the program is correct.
# You need to strictly follow the format Correctness: **True or False**. Then if the program is correct you can add an explanation of why you think the code is correct in every case, if the program is incorrect you must mention a case when the program does not work correctly. If you cant find a single case then the program is correct.
# """

# PROMPT_COMPLEX = """
# You have been assigned the role of a program verifier. Your task is to determine the correctness of a given Python program based on the provided problem description. If the program is correct, that is it meets the requirements in the problem description, print "True"; otherwise, print "False". Partially correct programs should be considered incorrect. You have to use the source code to try to understand if there is any missing logic or edge cases that the code is not handling. 
# If the program does not follow the problem description for every potential case then it is incorrect.Since if for at least one input or potential case the program does not work then Correctness **False**.
# You are trying to find any potential case that the porgram does not does what the descriptions says.  If you can't think of an example of the ocde not working as expected then the code is correct.
# You need to strictly follow the format Correctness: **True or False**.

# # Your task:
# Problem description: {description}
# Program:
# ```
# {code}
# ```


# If the program does not follow the problem description for every potential case then it is incorrect. Then if even for one input or potential case the program does not work then Correctness **False** .You are trying to find any potential case that the porgram does not does what the descriptions says. But if you cant find an example where the program does not work as expected in the description and all the examples you think work correctly then the program is correct.
# You need to strictly follow the format Correctness: **True or False**. Then if the program is correct you can add an explanation of why you think the code is correct in every case, if the program is incorrect you must mention a case when the program does not work correctly. If you cant find a single case then the program is correct.
# """

PROMPT_COMPLEX= """
Your task is to determine if a given Python program is correct based on the provided problem description. Assume valid inputs as described in the problem description.

First explain your reasoning step by step, then reply Correctness: **True**  if the given program is correct or Correctness: **False**  if the given program is incorrect.

# Problem:
{description}

# Program:
{code}

# Your response:
Reasoning:  
Correctness: **True** or **False**
"""

PROMPT_COMPLEX_NO_COT= """
Your task is to determine if a given Python program is correct based on the provided problem description. Assume valid inputs as described in the problem description.

Reply Correctness: **True**  if the given program is correct or Correctness: **False**  if the given program is incorrect.

# Problem:
{description}

# Program:
{code}

# Your response:
Correctness: **True** or **False**
"""

PROMPT_COMPLEX_CONFIDENCE = """
You have been assigned the role of a program verifier. Your task is to determine the correctness of a given Python program based on the provided problem description. If the program is correct, that is it meets the requirements in the problem description, print "True"; otherwise, print "False". Partially correct programs should be considered incorrect. You have to use the source code to try to understand if there is any missing logic or edge cases that the code is not handling. 
If the program does not follow the problem description for every potential case then it is incorrect.Since if for at least one input or potential case the program does not work then Correctness **False**.
You are trying to find any potential case that the porgram does not does what the descriptions says.  If you can't think of an example of the ocde not working as expected then the code is correct.
You also need to tell me how confident you are in your response from 0 to 100. With 0 being no confident at all and 100 bein 100% sure.
You need to strictly follow the format Correctness: **True or False** , Confidence: **number from 0 to 100**.

# Your task:
Problem description: {description}
Program:
```
{code}
```


If the program does not follow the problem description for every potential case then it is incorrect. Then if even for one input or potential case the program does not work then Correctness **False** .You are trying to find any potential case that the porgram does not does what the descriptions says. But if you cant find an example where the program does not work as expected in the description and all the examples you think work correctly then the program is correct.
Tell me how confident you are in your response in a scale from 0 to 100, where 0 means no confident at all.
You need to strictly follow the format Correctness: **True or False** , Confidence: **number from 0 to 100**. Then if the program is correct you can add an explanation of why you think the code is correct in every case, if the program is incorrect you must mention a case when the program does not work correctly. If you cant find a single case then the program is correct.
"""

PROMPT_Confidence = """
You have been assigned the role of a program verifier. Your task is to determine the correctness of a given Python program based on the provided problem description. If the program is correct, that is it meets the requirements in the problem description, reply 1; otherwise, reply 0. Partially correct programs should be considered incorrect. You have to use the source code to try to understand if there is any missing logic or edge cases that the code is not handling. 
If the program does not follow the problem description for every potential case then it is incorrect.Since if for at least one input or potential case the program does not work then reply 0.
You are trying to find any potential case that the porgram does not does what the descriptions says.  If you can't think of an example of the ocde not working as expected then the code is correct.
You need to reply either 1 for correct or 0 for incorrect.

# Your task:
Problem description: {description}
Program:
```
{code}
```


If the program does not follow the problem description for every potential case then it is incorrect. Then if even for one input or potential case the program does not work then reply 0 .You are trying to find any potential case that the porgram does not does what the descriptions says. But if you cant find an example where the program does not work as expected in the description and all the examples you think work correctly then the program is correct.
You need to strictly reply 1 or 0. 
"""


PROMPT_COMPLEX_CONFIDENCE_QWEN = """
You have been assigned the role of a program verifier. Your task is to determine the correctness of a given Python program based on the provided problem description . If the program is correct, that is it meets the requirements in the problem description, print "True"; otherwise, print "False". You need to strictly follow respond with one word **True or False**.

# Your task:
Problem description: {description}
Program:
```
{code}
```


The program is correct only if it meets the problem description! The problem description is defined before the program.  
Return  True if the program follows the problem description, otherwise return False. if the program does not do what the problem description asks for for every potential case.
Remember to return just one word for your response.
"""
TEST_GENERATION_PROMPT = """
Your task is to generate a Python script with assertions to test the correctness of a given Python program, based on the provided problem description. Assume valid inputs as described in the problem description.

The output must be a complete Python script with assertions that verify the program’s correctness. Do not execute the program yourself; just provide the test code.
If the code uses `stdin`, include the following helper function to automate input/output capture:

import io
import sys

def capture_output(func, input_data):
    sys.stdin = io.StringIO(input_data)
    captured_output = io.StringIO()
    sys.stdout = captured_output
    func() 
    sys.stdout = sys.__stdout__
    return captured_output.getvalue().strip()


# Problem:
{description}

# Program:
{code}

# Your response:
```python
# Include necessary imports if any
# Assume the provided program is saved as 'program.py' and can be imported from the same dir.

from program import *

# Write your test cases below
# Each test case should include assertions based on the problem description
# Example:
# assert function_name(input) == expected_output

# Add multiple test cases to ensure correctness across edge cases
assert ...

# End of script
"""

def extract_code_from_response(response: str) :
    """
    Extracts Python code from a response containing a code block.

    Args:
        response (str): The LLM response containing the Python code block.

    Returns:
        str: The extracted Python code.
    """
    code_block_pattern = re.compile(r"```python(.*?)```", re.DOTALL)
    match = code_block_pattern.search(response)
    if match:
        return match.group(1).strip(), True
    else:
        return response, False


 
def tester_call(description, code, model, retry=True):
   
    prompt = TEST_GENERATION_PROMPT.format(description=description, code=code)
    response = model.query(prompt)
    print(response)
    post, found =extract_code_from_response(response)
    print("*" * 50)
    print(f"LLM Reply: {post}")
    if retry and not found:
        return tester_call(description, code, model, retry=False)
    return post

def extract_result_new(s: str, keyword: str):
    temp=s
    s=s[-25:]
    pattern = fr"{keyword}:\s*\*\*(.*?)\*\*"
    matches = re.findall(pattern, s, re.DOTALL)
    if matches:
        # Select the last match
        res = matches[-1]
        # Clean up the beginning and end of the string for any weird characters like * or newlines
        return res.strip(), True
    if "false" in s[-20:].lower().strip() :
        return "false", True
    if "true" in s[-20:].lower().strip():
        return "true", True
    
    s=temp
    matches = re.findall(pattern, s, re.DOTALL)
    if matches:
        # Select the last match
        res = matches[-1]
        # Clean up the beginning and end of the string for any weird characters like * or newlines
        return res.strip(), True
    s=temp[-200:]
    if "code is correct" in s.lower().strip():
        return "true", True
    if "code is incorrect" in s.lower().strip():
        return "false", True
    if "code is not correct" in s.lower().strip():
        return "false", True
    return s, False
 
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
def naive_question_no_fsl(description, code, model, retry=True):
   
    prompt = PROMPT_COMPLEX.format(description=description, code=code)
    response = model.query(prompt)
    print(response)
    post, found = extract_result_new(response, "Correctness")
    print("*" * 50)
    print(f"{description} \n {code}")
    print(f"LLM Reply: {post}")
    if retry and not found:
        return naive_question_no_fsl(description, code, model, retry=False)
    if 'true' in post.lower().strip() :
        return True
    if "false" in post.lower().strip() :
        return False
    return post

def naive_question_no_fsl_no_cot(description, code, model, retry=True):
   
    prompt = PROMPT_COMPLEX_NO_COT.format(description=description, code=code)
    response = model.query(prompt)
    print(response)
    post, found = extract_result(response, "Correctness")
    print("*" * 50)
    print(f"{description} \n {code}")
    print(f"LLM Reply: {post}")
    if retry and not found:
        return naive_question_no_fsl(description, code, model, retry=False)
    if 'true' in post.lower().strip() :
        return True
    if "false" in post.lower().strip() :
        return False
    return post

def naive_question_no_fsl_with_response(description, code, model, retry=True):
    prompt = PROMPT_COMPLEX.format(description=description, code=code)
    response = model.query(prompt)
    print(response)
    post, found = extract_result(response, "Correctness")
    if retry and not found:
        return naive_question_no_fsl_with_response(description, code, model, retry=False)
    print("*" * 50)
    print(f"{description} \n {code}")
    print(f"LLM Reply: {post}")

    if 'true' in post.lower().strip() :
        return True , response
    if "false" in post.lower().strip() :
        return False , response
    return post , response

def naive_question_no_fsl_confidence(description, code, model, retry=True):
    prompt = PROMPT_Confidence.format(description=description, code=code)
    response, confidence = model.query_confidence(prompt)
    print(response)
    print(confidence)
    post, found = extract_result(response, "Correctness")
    if retry and not found:
        return naive_question_no_fsl_confidence(description, code, model, retry=False)
    print("*" * 50)
    print(f"{description} \n {code}")
    print(f"LLM Reply: {post}")
    print(f"Confidence: {confidence}")

    if 'true' in post.lower().strip() :
        return True, confidence
    if "false" in post.lower().strip() :
        return False , confidence
    return post , confidence


def naive_question_no_fsl_confidence_2(description, code, model, retry=True):
    prompt = PROMPT_COMPLEX_CONFIDENCE.format(description=description, code=code)
    response = model.query(prompt)
    print(response)
    
    post, found1 = extract_result(response, "Correctness")
    confidence, found2 = extract_result(response, "Confidence")
    if retry :
        if not found1 or not found2:
            return naive_question_no_fsl_confidence_2(description, code, model, retry=False)
    print("*" * 50)
    print(f"{description} \n {code}")
    print(f"LLM Reply: {post}")
    print(f"Confidence: {confidence}")

    if 'true' in post.lower().strip() :
        return True , confidence
    if "false" in post.lower().strip() :
        return False, confidence
    return post

def naive_question_no_fsl_confidence_qwen(description, code, model, retry=True):
    prompt = PROMPT_COMPLEX_CONFIDENCE_QWEN.format(description=description, code=code)
    print (f"the Prompt is \n\n\n {prompt}")

    response, confidence = model.query_confidence_qwen(prompt)
    print(response, confidence)
    
    

    if 'true' in response.lower().strip() :
        return True , confidence
    if "false" in response.lower().strip() :
        return False, confidence
    return response, confidence

# def main():
#     # VariableA (Annotated Code)
#     code = """
#     def func(students):
#     total = 0
#     while students >= 1:
#         total += students
#         nstudents -= 1
#     if (total>100):
#         return 'not enough money'
#     try:
#         cost_per_student = total / student
#         return cost_per_student
#     except ZeroDivisionError:
#         return 'Division by zero error'
#     """

#     # VariableB (Return Postconditions)
#     des = "Every student must get one more than the previous.The first student gets 1.  If the total cost is more than 100 we dont have enough money to give so print a message. calculate average cost per student."
#     # Initialize your model (this is pseudocode)
#     model = ()

#     # Get the functionality summary
#     res = naive_question(code, des, model)

#     print("Result:")
#     print(res)

# if __name__ == "__main__":
#     main()


