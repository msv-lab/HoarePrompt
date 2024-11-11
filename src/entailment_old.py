import re

# This is the final step after the final post condition has been generated. This is the prompt template that will be filled in with the problem description, the program,
# and the final output hints (postcondition). It instructs the model to determine whether the program
# satisfies the description and output specification, and asks it to return either "True" or "False".

ENTAILMENT_CHECKING_PROMPT_TEMPLATE = """
You have been assigned the role of a program verifier. Your task is to determineg the correctness of a given Python program based on the provided problem description and the description of program's output. If the program is correct, that is it meets the requirements in the problem description, print "True"; otherwise, print "False". Partially correct programs should be considered incorrect. You have to use the source code and the Output hints to try to understand if there is any missing logic or edge cases that the code is not handling. 
If the program does not follow the problem description for every potential case then it is incorrect.Since if for at least one input or potential case the program does not work then Correctness **False**.
You are trying to find any potential case that the porgram does not does what the descriptions says. The output hints might give you examples of some of the cases that the code is not working corectly.
If those output hints describes certain edge cases that you think the code does not indeed cover then the code is incorrect. If you can't think of an example of the ocde not working as expected then the code is correct.
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
Explanation: According to the output hints, the function returns True if `n` is less than 2 or if `n` is divisible by any integer in the range [2, n). Otherwise, it returns False. Since the smallest prime number is 2 and prime numbers can only be divided by 1 and themselves, this approach correctly identifies non-prime numbers as per the given specification. 

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
Explanation: According to the output hints, the function returns the value of the variable `count`, which is equal to the number of times a character at position `i` in the string `s` is equal to a character at position `j + 1` for some `j` in the range `[i, len(s) - 2]`. This does not account for substrings of length 1, so it is incorrect.

Correctness: **False**.

# Example 3

Problem description: Write a python function to check whether the given number can be represented as difference of two squares or not.
Program:
```
import math
def dif_Square(n):
    for i in range(int(math.sqrt(n)), -1, -1):
        for j in range(i, -1, -1):
            if i*i - j*j == n:
                return True
    return False
```

Output hints: The function `dif_Square(n)` returns True if and only if there exist integers i and j, where i is in the range [⌈√n⌉, 0] (inclusive) and j is in the range [i, 0] (inclusive), such that i * i - j * j equals n. If no such i and j exist, then the function returns False. Furthermore, the loop invariant holds for both loops: for all i in the range [⌈√n⌉, 1] and for all j in the range [i, 1], i * i - j * j is not equal to n. This invariant implies that if the function returns False, then there is no i and j in the specified ranges for which i * i - j * j is equal to n. Additionally, the function does not modify any external state, and its behavior is solely determined by the input n. Precondition: n is an integer.

Example answer 3:
Explanation: According to the output hints, i is in the range [⌈√n⌉, 0] (inclusive) and j is in the range [i, 0] (inclusive), this range is incorrect. It can only detect the case when n is a perfect square, i.e., when √n * √n - 0 = n, therefore it does not meet the specification.

Correctness: **False**.

# Example 4

Problem description: Write a python function to find the minimum number of rotations (greater than 0) required to get the same string.
Code:
```
def find_Rotations(str1):
    n = len(str1)
    for i in range(1,n+1):
        if str1[i:] + str1[:i] == str1:
            return i
```

Output hints: If the string is a palindrome, the function does not return a value and the variable n remains unchanged, holding the length of the string str1. If the string is not a palindrome, then the function returns an integer i such that 0 < i < n, where n is the length of the string str1, and i represents the length of the shortest non-empty rotation of str1 to return to its original state.. If no such rotation exists, then the function does not return a value.

Example answer 4:
Explanation: According to the explanation, if the string is a palindrome, the function does not return a value, and the variable `n` remains unchanged, holding the length of the string `str1`. This behavior is correct as the specification states that the rotation count must be greater than 0. If the string is not a palindrome, then the function returns an integer `i` such that `0 < i < n`, where `n` is the length of the string `str1`. The value `i` represents the length of the shortest non-empty rotation of str1 to return to its original state.. However, the code iterates from `1` to `n-1`, meaning it does not include `n`. This omission is problematic because it fails to check the complete rotation case, where `i` could be equal to `n`. Consequently, the function does not meet the specification as it should return the rotation count up to `n` times. Therefore, it does not meet the specification.

Correctness: **False**.

# Example 5

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

Example answer 5:
Explanation: According to the output hints, the function returns the index of the target number in the input list `arr` if it is present; otherwise, it returns -1. The function uses a binary search algorithm to find the target number in the list. However, the termination condition of the while loop is `left < right`, which may cause the loop to terminate prematurely when `left` is equal to `right`. This condition can lead to missing the target element if it is at the last index of the list. Also when left and right are adjacent then mid will always be left leading to infinate loop.
Correctness: **False**.

# Your task:
Problem description: {description}
Program:
```
{program}
```
Output hints: {postcondition}


Do the ouput hints agree with the code? If they do use them along with the actual code to determine if the code is correct or not.
Does the code follow the problem description for every potential case?
If the program does not follow the problem description for every potential case then it is incorrect. they hints might provide such cases but make sure that the hints indeed agree with the code.
Then if even for one input or potential case the program does not agree with the description then Correctness **False**.
But if you can't find an example where the program does not work as expected in the description and all the examples you think work correctly then then Correctness **True**
The output hints might give you examples of some of the cases that the code is not working corectly, but make sure that the stuff the output hints says are indeed valid and make sense. Sometimes the output hints hallucinate some cases that are not actually valid, so doublecheck.
You need to strictly follow the format Correctness: **True or False**. Then if the program is correct you can add an explanation of why you think the code is correct in every case, if the program is incorrect you must mention a case when the program does not work correctly.
"""

# Parses the model response to see if it responded True or False
def extract_correctness_from_response(response_content: str) -> str:
    pattern = r"Correctness:\s*\*\*(.*?)\*\*|Correctness:\s*(True|False)"
    match = re.search(pattern, response_content)
    if match:
        if match.group(1):
            return match.group(1).strip()
        elif match.group(2):
            return match.group(2).strip()
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