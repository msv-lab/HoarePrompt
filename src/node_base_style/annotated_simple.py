import re

from node_base_style.hoare_triple import Triple, pprint_cmd, print_state
from node_base_style.helper import extract_result


# This script's responsible for executing small code snippets and determining the resulting program state based on the provided initial state and program code. It is the general script for a simple program statement (not loops or ifs, try etc)
PROMPT = """


You have been assigned the role of a program verifier, responsible for simulating the execution of Python code. You will be provided with a function description and a Python function code snippet. You need to provide if the code does what the function description says. Please avoid describing how the program runs. If the code satisfies the description reply CORRECT, otherwise reply INCORRECT with an explanation. You must adhere to the text format: RESULT: **Correct or Incorrect**.

Description: {description}
Python Fucntion:
```
{code}
```
Now, please think step by step: List the impact of the code on the program, check the previous values of the affected variables, and then calculate the result.
Use the format: RESULT: **Correct or Incorrect**.
"""

PROMPT_COMPLEX = """
You have been assigned the role of a program verifier. Your task is to determineg the correctness of a given Python program based on the provided problem description . If the program is correct, that is it meets the requirements in the problem description, print "True"; otherwise, print "False". You need to strictly follow the format Correctness: **True or False**.

# Your task:
I am now giing you the problem description. This is what the function must do.
PROBLEM DESCRIPTION: {description}
This was the problem description. Lets move on to the  annotated program. The program must do what the problem description says for it to be correct.

Annotated Program:
```
{code}
```
The program is correct only if it meets the problem description! The problem description is defined before the program.  Return Correctness: **True** if the program follows the problem description, otherwise return Correctness: **False** if the program does not do what the problem description asks for for every potential case.
If the program is correct explain why it always does what the problem description say. If it is incorrect explain why it does not do what the problem description says or a case where it doesnot follow the problem description.
"""

# This is the main function, it completes the prompt, queries the model and extracts the result, meaining the output state of that program part
def annotated_simple(description, code, model):
   
    prompt = PROMPT_COMPLEX.format(description=description, code=code)
    response = model.query(prompt)
    print(response)
    post = extract_result(response, "Correctness")
    print("*" * 50)
    print(f"{description} \n {code}")
    print(f"LLM Reply: {post}")

    if 'true' in post.lower().strip() :
        return (True, response)
    if "false" in post.lower().strip() :
        return (False, response)
    raise ValueError('failed to parse entailment checking response')

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
