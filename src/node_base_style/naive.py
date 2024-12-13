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
You have been assigned the role of a program verifier. Your task is to determine the correctness of a given Python program based on the provided problem description. If the program is correct, that is it meets the requirements in the problem description, print "True"; otherwise, print "False". Partially correct programs should be considered incorrect. You have to use the source code to try to understand if there is any missing logic or edge cases that the code is not handling. 
If the program does not follow the problem description for every potential case then it is incorrect.Since if for at least one input or potential case the program does not work then Correctness **False**.
You are trying to find any potential case that the porgram does not does what the descriptions says.  If you can't think of an example of the ocde not working as expected then the code is correct.
You need to strictly follow the format Correctness: **True or False**.

I am giving you some examples to understand the task better. Then I am giving you your task.
# Example 1

Problem description: Write a python function to identify non-prime numbers.
Program:
```
def is_not_prime(n):
    if n < 2:
        return True
    for i in range(2, n):
        if n % i == 0:
            return True
    return False
```
Example Answer 1:
Correctness: **True**.

# Example 2

Problem description: Write a python function to count all the substrings starting and ending with same characters.
Program:
```
def count_Substring_With_Equal_Ends(s):
    count = 0
    for i in range(len(s)-1):
        for j in range(i,len(s)-1):
            if s[i] == s[j+1]:
                count += 1
    return count
```

Example Answer 2:
Correctness: **False**.

# Example 3

Problem description: Write a function to perform binary search of a number in an list
Program:
```
def binary_search(arr, target):
    left = 0
    right = len(arr) - 1
    while left < right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid
        else:
            right = mid - 1
    if arr[left] == target:
        return left
    return -1
```
Example answer 3:
Correctness: **False**.

# Your task:
Problem description: {description}
Program:
```
{code}
```


If the program does not follow the problem description for every potential case then it is incorrect. Then if even for one input or potential case the program does not work then Correctness **False** .You are trying to find any potential case that the porgram does not does what the descriptions says. But if you cant find an example where the program does not work as expected in the description and all the examples you think work correctly then the program is correct.
You need to strictly follow the format Correctness: **True or False**. Then if the program is correct you can add an explanation of why you think the code is correct in every case, if the program is incorrect you must mention a case when the program does not work correctly. If you cant find a single case then the program is correct.
"""

# This is the main function, it completes the prompt, queries the model and extracts the result, meaining the output state of that program part
def naive_question(description, code, model):
   
    prompt = PROMPT_COMPLEX.format(description=description, code=code)
    response = model.query(prompt)
    print(response)
    post = extract_result(response, "Correctness")
    print("*" * 50)
    print(f"{description} \n {code}")
    print(f"LLM Reply: {post}")

    if 'true' in post.lower().strip() :
        return True
    if "false" in post.lower().strip() :
        return False
    return post

def naive_question_with_response(description, code, model):
   
    prompt = PROMPT_COMPLEX.format(description=description, code=code)
    response = model.query(prompt)
    print(response)
    post = extract_result(response, "Correctness")
    print("*" * 50)
    print(f"{description} \n {code}")
    print(f"LLM Reply: {post}")

    if 'true' in post.lower().strip() :
        return True, response
    if "false" in post.lower().strip() :
        return False, response
    return post, response

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
