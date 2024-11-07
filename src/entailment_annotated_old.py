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

I am giving you some examples to understand the task better. Then I am giving you your task.
# Example 1

Problem description: Write a python function to identify non-prime numbers.
Annotated Program:
```
def func(n):
    if (n < 2) :
        return True
        #State of the program after the return statement: `n` is an integer greater than or equal to 1, and the function returns True
    #State of the program after the if part has been executed: `n` is an integer greater than or equal to 1, and the function returns True
    #State of the program after the if block has been executed: *`n` is an integer greater than or equal to 1. If `n` is less than 2, the function returns True. Otherwise, there is no change in the values of the variables.
    for i in range(2, n):
        if n % i == 0:
            return True
        
    #State of the program after the  for loop has been executed: If n is less than 2, the function returns True. If n is greater than or equal to 2 and is not divisible by any number in the range from 2 to n-1, then the function returns False. Otherwise, the function returns True.
    return False
    #State of the program after the return statement: The function returns False
```

Example Answer 1:
Explanation:The code originally looks correct. The function annotations agree with the code and with their help we determine that the code indeed follows the problem description. the function returns True if `n` is less than 2 or if `n` is divisible by any integer in the range [2, n). Otherwise, it returns False. Since the smallest prime number is 2 and prime numbers can only be divided by 1 and themselves, this approach correctly identifies non-prime numbers as per the given specification. 

Correctness: **True**.

# Example 2

Problem description: Write a python function to count all the substrings starting and ending with same characters.
Annotated Program:
```
def func(s):
    count = 0
    #State of the program here: `l`, `r`, and `k` are integers such that 1 <= l <= r < 10^18 and 1 <= k <= 10; `count` is 0
    for i in range(len(s) - 1):
        for j in range(i, len(s) - 1):
            if s[i] == s[j + 1]:
                count += 1
        
    #State of the program after the  for loop has been executed: If the length of string s is at least 2, the loop will execute and count will contain the number of times s[i] is equal to s[j + 1] for each iteration of the loop. If there are no repeating characters in s, count will remain 0. If the length of s is less than 2, the loop does not execute and count remains 0.
    return count
    #State of the program after the return statement: If the length of string s is at least 2, the loop will execute and count will contain the number of times s[i] is equal to s[j + 1] for each iteration of the loop. If there are no repeating characters in s, count will remain 0. If the length of s is less than 2, the loop does not execute and count remains 0.
#Overall this is what the function does: The function accepts a string s, counts the number of times a character is repeated in consecutive positions, and returns the total count. If the length of s is less than 2, it returns 0.

```

Example Answer 2:
Explanation: The code seems to be incorrect and not follow the problem description. We also see that the  code annotations agree with the code and they also help prove that the code is incorrect.  The function returns the value of the variable `count`, which is equal to the number of times a character at position `i` in the string `s` is equal to a character at position `j + 1` for some `j` in the range `[i, len(s) - 2]`. This does not account for substrings of length 1, so it is incorrect.

Correctness: **False**.

# Example 3

Problem description: Write a function to perform binary search of a number in an list
Annotated Program:
```
ef func(arr, target):
    left = 0
    #State of the program here: `l` and `r` are integers such that 1 <= l <= r < 10^18, `k` is an integer such that 1 <= k <= 10, `left` is 0
    right = len(arr) - 1
    #State of the program here: `l` and `r` are integers such that 1 <= l <= r < 10^18, `k` is an integer such that 1 <= k <= 10, `left` is 0, `right` is assigned the length of `arr` - 1
    while left < right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid
        else:
            right = mid - 1
        
    #State of the program after the loop has been executed: If the loop executes at least once, the values of `l`, `r`, `k`, `left`, `right`, and `mid` will be updated according to the conditions specified in the loop code. If `arr[mid]` equals `target`, the function will return `mid`. If `arr[mid]` is less than `target`, `left` will be updated to `mid`. If `arr[mid]` is greater than or equal to `target`, `right` will be updated to `mid - 1`. After the loop finishes, the final values of `l`, `r`, `k`, `left`, `right`, and `mid` will reflect the last iteration of the loop. Edge cases to consider are when `left` is equal to or greater than `right` before entering the loop, in which case the loop will not execute.
    if (arr[left] == target) :
        return left
        #State of the program after the return statement: If the loop does not execute, the function will return the initial value of `left`. If the loop does execute, the function will return the final value of `left` after the last iteration of the loop. The values of `l`, `r`, `k`, `left`, `right`, and `mid` will be updated according to the loop conditions.
    #State of the program after the if part has been executed: If the loop does not execute, the function will return the initial value of `left`. If the loop does execute, the function will return the final value of `left` after the last iteration of the loop. The values of `l`, `r`, `k`, `left`, `right`, and `mid` will be updated according to the loop conditions.
    #State of the program after the if block has been executed: *If the loop does not execute because `left` is equal to or greater than `right`, the function will return the initial value of `left`. If the loop does execute, the function will return the final value of `left` after the last iteration of the loop. In both cases, the values of `l`, `r`, `k`, `left`, `right`, and `mid` will be updated as per the loop conditions.
    return -1
    #State of the program after the return statement: The function returns -1
#Overall this is what the function does: The function accepts a list arr and an integer target, updates certain values based on loop conditions, and returns either the index of target, the initial value of left, or -1.
```
Example answer 3:
Explanation: Originally the code looks correct but after confirming that the code annotations agree with the code,we can see the function returns the index of the target number in the input list `arr` if it is present; otherwise, it returns -1. The function uses a binary search algorithm to find the target number in the list. However, the termination condition of the while loop is `left < right`, which may cause the loop to terminate prematurely when `left` is equal to `right`. This condition can lead to missing the target element if it is at the last index of the list. Also when left and right are adjacent then mid will always be left leading to infinate loop.
Correctness: **False**.

# Your task:
Problem description: {description}
Annotated Program:
```
{annotated_program}
```


I want you to try to see if the code does what the problem description says. The code must follow the problem description for it to be correct!!
You can also use the code annotations to understand the code better. Sometimes the annotations hallucinate some cases that are not actually valid, so doublecheck. Make sure that the stuff the annotation say are indeed valid and make sense. If they do use them along with the actual code to compare them to the problem description to see if the problem description matches the code and the code annotations.
Does the code follow the problem description for every potential case?
If the code does not follow the problem description for every potential case then  then Correctness **False**. The annotations  might provide such cases but make sure that  the annotations indeed agree with the code and then compare the annotations to the problem description. Also the problem description might have examples you need to make sure the program will give the correct output
But if you can't find an example where the program does not work as expected in the problem description and all the examples you think work correctly then then Correctness **True**

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