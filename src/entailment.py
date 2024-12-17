import re

# This is the final step after the final post condition has been generated. This is the prompt template that will be filled in with the problem description, the program,
# and the final output hints (postcondition). It instructs the model to determine whether the program
# satisfies the description and output specification, and asks it to return either "True" or "False".

ENTAILMENT_CHECKING_PROMPT_TEMPLATE = """
You have been assigned the role of a program verifier. Your task is to determineg the correctness of a given Python program based on the provided problem description and the description of program's output. If the program is correct, that is it meets the requirements in the problem description, print Correctness: **True**; otherwise, print Correctness: **False**. Partially correct programs should be considered incorrect. You have to use the source code and the Output hints to try to understand if there is any missing logic or edge cases that the code is not handling. 
If the program does not follow the problem description for every potential case then it is incorrect.Since if for at least one input or potential case the program does not work then Correctness **False**.
The output hints summarise the code functionality and might give you examples of some of the cases that the code is not working corectly, but make sure that the output hints make sense.
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

Output hints: The function returns True if n is less than 2 or if n is divisible by any integer in the range [2, n). Otherwise, it returns False.

Example Answer 1:
Explanation:The code originally looks correct. The function hints agree with the code and with their help we determine that the code indeed follows the problem description. the function returns True if `n` is less than 2 or if `n` is divisible by any integer in the range [2, n). Otherwise, it returns False. Since the smallest prime number is 2 and prime numbers can only be divided by 1 and themselves, this approach correctly identifies non-prime numbers as per the given specification. 

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

Output hints: The function returns the value of the variable 'count', which is equal to the number of times a character at position 'i' in the string 's' is equal to a character at position 'j + 1' for some 'j' in the range '[i, len(s) - 2]'. This implies that 'count' represents the number of consecutive occurrences of identical characters in the string 's' that may form a substring with equal ending and beginning characters, excluding the last character of the string from this comparison.

Example Answer 2:
Explanation: The code seems to be incorrect and not follow the problem description. We also see that the output hints agree with the code and they also help prove that the code is incorrect.  The function returns the value of the variable `count`, which is equal to the number of times a character at position `i` in the string `s` is equal to a character at position `j + 1` for some `j` in the range `[i, len(s) - 2]`. This does not account for substrings of length 1, so it is incorrect.

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
Output hints: The function returns the index of the target number in the input list `arr` if it is present; otherwise, it returns -1. If the taget is at the last index it wont be found as the loop will break before reaching the last index.

Example answer 3:
Explanation: Originnaly the code looks correct but after confirming that the output hints agree with the code,we can see the function returns the index of the target number in the input list `arr` if it is present; otherwise, it returns -1. The function uses a binary search algorithm to find the target number in the list. However, the termination condition of the while loop is `left < right`, which may cause the loop to terminate prematurely when `left` is equal to `right`. This condition can lead to missing the target element if it is at the last index of the list. Also when left and right are adjacent then mid will always be left leading to infinate loop.
Correctness: **False**.

# Your task:
Problem description: {description}
Program:
```
{program}
```
Output hints: {postcondition}

Does the code do what  the problem description says,  for every potential case?
If the program does not follow the problem description for every potential case then  then Correctness **False**. The hints might provide such cases but make sure that the hints indeed agree with the code. Also the program description might have examples you need to make sure the program will give the correct output
But if you can't find an example where the program does not work as expected in the description and all the examples you think work correctly then then Correctness **True**
Also we assume that the input will be valid and will not cause any errors in the program. So for example if the program is supposed to accept a list but does not handle the case when the input is not a list or an empty list then the program isstill correct since we assume the user will always provide a valid input. The same if we expecta positive integer and the program does not handle the case when the input is negative or zero.
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