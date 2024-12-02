import re

# This is the final step after the final post condition has been generated. This is the prompt template that will be filled in with the problem description, the program,
# and the final Output state (postcondition). It instructs the model to determine whether the program
# satisfies the description and output specification, and asks it to return either "True" or "False".

ENTAILMENT_CHECKING_PROMPT_TEMPLATE = """
You have been assigned the role of a program verifier. Your task is to determine the correctness of a given Python program based on the provided problem description and  the annotations in the code. If the program is correct, that is it meets the requirements in the problem description, print Correctness: **True**; otherwise, print  Correctness: **False**. Partially correct programs should be considered incorrect. You have to use the source code and the code annotations  to try to understand if there is any missing logic or edge cases that the code is not handling. 
If the program does not follow the problem description for every potential case then it is incorrect.Since if for at least one input or potential case the program does not work then Correctness **False**.
You are trying to find any potential case that the porgram does not does what the problem descriptions says. The annotations in the code summarise the state of the program and  might give you examples of some of the cases that the code is not working corectly.
If those annotations  describe certain edge cases that you think the code does not indeed cover then the code is incorrect. If you can't think of an example of the ocde not working as expected then the code is correct.
You need to strictly follow the format Correctness: **True or False**.

I am giving you some examples to understand the task better. Then I am giving you your task.
# Example 1

Problem description: Write a python function to identify non-prime numbers.


Annotated Functions:

Function number 1 :
 Code:
 '''
def is_divisible(number1, number2):
    if (number1 % number2 == 0) :
        return True
        #State of the program after the return statement: No variables involved, the function returns True
    #State of the program after the if part has been executed: No variables involved, the function returns True
    #State of the program after the if block has been executed: l and r are integers such that 1 <= l <= r < 10^18, k is an integer such that 1 <= k <= 10. If number1 is divisible by number2, the function returns True. Otherwise, there is no change in the state of the variables.
#Overall this is what the function does: The function accepts two integers number1 and number2. If number1 is divisible by number2, it returns True. Otherwise, there is no change in the state of the variables.
''' 

Function number 2 :
 Code:
 '''
def func(n):
    if (n < 2) :
        return True
        #State of the program after the return statement: `l` and `r` are integers such that 1 <= l <= r < 10^18, and `k` is an integer such that 1 <= k <= 10
    #State of the program after the if part has been executed: `l` and `r` are integers such that 1 <= l <= r < 10^18, and `k` is an integer such that 1 <= k <= 10
    #State of the program after the if block has been executed: *`l` and `r` are integers such that 1 <= l <= r < 10^18, and `k` is an integer such that 1 <= k <= 10. If `n` is less than 2, the function returns True.
    for i in range(2, n):
        if is_divisible(n, i):
            return True
        
    #State of the program after the  for loop has been executed: If `n` is less than 2, the function returns True. If `n` is greater than or equal to 2, the loop checks if `n` is divisible by any number from 2 to `n-1`. If `n` is divisible by any of these numbers, the function returns True. If `n` is not divisible by any number from 2 to `n-1`, the function returns False.
    return False
    #State of the program after the return statement: The function returns False
#Overall this is what the function does: The function accepts a parameter n and returns True if n is less than 2, or if n is not a prime number. It returns False if n is a prime number.

''' 


Example Answer 1:
Explanation: The program initially seems to do what the problem description says. Lets see if  the annotations also agree with the code  and if they give us any reason to think the program is incorrect. The  annotations seem to agree with the program code and from their contents they reenforce our reasoning that the code is correct.
The function returns True if `n` is less than 2 or if `n` is divisible by any integer in the range [2, n). Otherwise, it returns False. Since the smallest prime number is 2 and prime numbers can only be divided by 1 and themselves, this approach correctly identifies non-prime numbers as per the given specification. 

Correctness: **True**.


# Example 2

Problem description: Write a python function to find the minimum number of rotations (greater than 0) required to get the same string.

Annotated Functions :
Function number 1 :
 Code:
 '''
def func_1(list):
    return len(list)
    #State of the program after the return statement: The function returns the length of the list named `list`.
#Overall this is what the function does: The function accepts a list as a parameter and returns the length of that list.

''' 


Function number 2 :
 Code:
 '''
def func_2(str1):
    n = func_1(str1)
    #State of the program here: `str1` is a string, value of `n` depends on the implementation of func_1
    for i in range(1, n + 1):
        if str1[i:] + str1[:i] == str1:
            return i
        
    #State of the program after the  for loop has been executed: `str1` is a string, `n` is at least 1. The loop iterates through the range from 1 to `n` inclusive. If the concatenation of the substring starting from index `i` to the end of `str1` and the substring from the start of `str1` to index `i` is equal to `str1`, the loop returns the value of `i`. If this condition is never met, then the loop does not return any value.
#Overall this is what the function does: The function accepts a string parameter `str1` and an integer `n`, iterates through the range from 1 to `n` inclusive, and returns the value of `i` if a specific condition is met. If the condition is never met, the function does not return any value.

''' 


Example Answer 2:
Explanation: The code initially does not seem to be correct. Lets see if the code annotations agree with the code and reenforce our belief that the code is incorrect. The annotations do seem to agree with the code and they also show that the code does not always follow the problem description. If the string is a palindrome, the function does not return a value, and the variable `n` remains unchanged, holding the length of the string `str1`. This behavior is correct as the specification states that the rotation count must be greater than 0. If the string is not a palindrome, then the function returns an integer `i` such that `0 < i < n`, where `n` is the length of the string `str1`. The value `i` represents the length of the shortest non-empty rotation of str1 to return to its original state.. However, the code iterates from `1` to `n-1`, meaning it does not include `n`. This omission is problematic because it fails to check the complete rotation case, where `i` could be equal to `n`. Consequently, the function does not meet the specification as it should return the rotation count up to `n` times. Therefore, it does not meet the specification.

Correctness: **False**.

# Your task:
Problem description: {description}
Annotated Functions:
{functions}


I want you to try to see if the code (including all the functions) does what the problem description says. The code must follow the problem description for it to be correct!!
You can also use the code annotations to understand the code better. Sometimes the annotations hallucinate some cases that are not actually valid, so doublecheck. Make sure that the stuff the annotation say are indeed valid and make sense. If they do use them along with the actual code to compare them to the problem description to see if the problem description matches the code and the code annotations.
Does the code follow the problem description for every potential case?
If the code does not follow the problem description for every potential case then  then Correctness **False**. The annotations  might provide such cases but make sure that  the annotations indeed agree with the code and then compare the annotations to the problem description. Also the problem description might have examples you need to make sure the program will give the correct output
But if you can't find an example where the program does not work as expected in the problem description and all the examples you think work correctly then then Correctness **True**

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

    if result.lower() == 'true':
        return (True , response)
    if result.lower() == 'false':
        return (False , response)
    raise ValueError('failed to parse entailment checking response')


# TBD: WHAT OTHER APPROACH CAN BE USED OTHER THAN NAIVE?