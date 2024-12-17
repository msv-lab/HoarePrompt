import re

# This is the final step after the final post condition has been generated. This is the prompt template that will be filled in with the problem description, the program,
# and the final output description (postcondition). It instructs the model to determine whether the program
# satisfies the description and output specification, and asks it to return either "True" or "False".

ENTAILMENT_CHECKING_PROMPT_TEMPLATE = """
You have been assigned the role of a program verifier. Your task is to determine the correctness of a given Python program based on the provided problem description and the description of program's output. If the program is correct, that is it meets the requirements in the problem description,  print Correctness: **True**; otherwise, print  Correctness: **False**. Partially correct programs should be considered incorrect. You have to use the source code and the Output hints to try to understand if there is any missing logic or edge cases that the code is not handling. 
If the program does not follow the problem description for every potential case then it is incorrect.Since if for at least one input or potential case the program does not work then Correctness **False**.
The output hints summarise the code functionality and might give you examples of some of the cases that the code is not working corectly, but make sure the hints agree with the code.
You need to strictly follow the format Correctness: **True or False**.

I am giving you some examples to understand the task better. Then I am giving you your task.
# Example 1

Problem description: Write a python function to identify non-prime numbers.


Functions with output hints for each function:
Function nummber 1 :
 Code:
 '''
def is_divisible(number1, number2):
    if number1 % number2 == 0:
        return True
''' 

Output hints for function1:  The function accepts 2 numbers as input, if number 1 is divisible than number2 then the function returns True.
Function nummber 2 :
 Code:
 '''
def is_not_prime(n):
    if n < 2:
        return True
    for i in range(2, n):
        if is_divisible(n,i):
            return True
    return False
''' 

Output hints for function 2:  The function returns True if n is less than 2 or if n is divisible by any integer in the range [2, n). Otherwise, it returns False.

Example Answer 1:
Explanation: The program initially seems to do what the description says. Lets see if the hints also agree with the code and if they give us any reason to think the program is incorrect. The output hints seem to agree with the program code and from their contents they reenforce our reasoning that the code is correct.
The function returns True if `n` is less than 2 or if `n` is divisible by any integer in the range [2, n). Otherwise, it returns False. Since the smallest prime number is 2 and prime numbers can only be divided by 1 and themselves, this approach correctly identifies non-prime numbers as per the given specification. 

Correctness: **True**.

# Example 2

Problem description: Write a python function to count all the substrings starting and ending with same characters.
Function nummber 1 :
 Code:
```
def count_Substring_With_Equal_Ends(s):
    count = 0
    for i in range(len(s)-1):
        for j in range(i,len(s)-1):
            if s[i] == s[j+1]:
                count += 1
    return count
```

Output hints for function number 1 : The function returns the value of the variable 'count', which is equal to the number of times a character at position 'i' in the string 's' is equal to a character at position 'j + 1' for some 'j' in the range '[i, len(s) - 2]'. This implies that 'count' represents the number of consecutive occurrences of identical characters in the string 's' that may form a substring with equal ending and beginning characters, excluding the last character of the string from this comparison.

Example Answer 2:
Explanation: The function initially seems to be correct. Lets see if the output hints agree with the code and if they give us any reason to think the code is incorrec. Indeed they agree with the code and they show that the code might not always follow the program description. The function returns the value of the variable `count`, which is equal to the number of times a character at position `i` in the string `s` is equal to a character at position `j + 1` for some `j` in the range `[i, len(s) - 2]`. This does not account for substrings of length 1, so it is incorrect.

Correctness: **False**.


# Example 3

Problem description: Write a python function to find the minimum number of rotations (greater than 0) required to get the same string.

Functions with output hints for each function:
Function nummber 1 :
 Code:
 '''
def get_list_size(list):
    return len(list)
''' 

Output hint for function1:  The function accepts a string and returns the size of that string
Function nummber 2 :
 Code:
 '''
def find_Rotations(str1):
    n = get_list_size(str1)
    for i in range(1,n+1):
        if str1[i:] + str1[:i] == str1:
            return i
''' 

Output hint for function 2: If the string is a palindrome, the function does not return a value and the variable n remains unchanged, holding the length of the string str1. If the string is not a palindrome, then the function returns an integer i such that 0 < i < n, where n is the length of the string str1, and i represents the length of the shortest non-empty rotation of str1 to return to its original state.. If no such rotation exists, then the function does not return a value.

Example Answer 3:
Explanation: The code initially does not seem to be correct. Lets see if the output hints agree with the code and reenforce our belief that the code is incorrect. The hints do seem to agree with the code and they also show that the code does not always follow the program description. If the string is a palindrome, the function does not return a value, and the variable `n` remains unchanged, holding the length of the string `str1`. This behavior is correct as the specification states that the rotation count must be greater than 0. If the string is not a palindrome, then the function returns an integer `i` such that `0 < i < n`, where `n` is the length of the string `str1`. The value `i` represents the length of the shortest non-empty rotation of str1 to return to its original state.. However, the code iterates from `1` to `n-1`, meaning it does not include `n`. This omission is problematic because it fails to check the complete rotation case, where `i` could be equal to `n`. Consequently, the function does not meet the specification as it should return the rotation count up to `n` times. Therefore, it does not meet the specification.

Correctness: **False**.

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