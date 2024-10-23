
from node_base_style.hoare_triple import pprint_cmd, Triple
from node_base_style.helper import extract_result

# The prompt as defined earlier

PROMPT = """
You are a program verifier responsible for summarizing the functionality of a Python function.

You are provided with:

1. **Annotated Code**: The function code with comments that include postconditions at various points.
2. **Return Postconditions**: The overall postcondition(s) of the function's execution.

**Your Task:**

- Analyze the annotated code and the return postconditions.
- Determine what parameters the function accepts and what it returns.
- Provide a concise summary of the function's functionality.

Please avoid describing how the function operates or implementation details—focus on what the function does from the user's perspective.

You must adhere to the text format: Functionality: **Your summary here**


Example 1:

Annotated Code:
```
# This is a function and its postcondition is: The function accepts a parameter `number`, returns True if `number` is even; otherwise, it returns False.
def func(number):
    # This is an if statement and its postcondition is: If `number` is even, the function returns True.
    if number % 2 == 0:
        # This is a return statement in the if part and its postcondition is: Returns True if `number` is even.
        return True
    # This is an else statement and its postcondition is: If `number` is not even, the function returns False.
    else:
        # This is a return statement in the else part and its postcondition is: Returns False if `number` is not even.
        return False
```

Return Postconditions: The function accepts a parameter `number` and returns True if `number` is even; otherwise, it returns False.

Now, please think step by step: What are the parameters the function accepts, and what does it return? What is the functionality of the function? Make sure to notice any potential edge cases and missing logic. Make sure to Adhere to the format Functionality: **Your summary here**

Example Answer 1:

The function func accepts an integer parameter number. According to the annotations, if number is even, it returns True; otherwise, it returns False. Therefore, the functionality of the function is to check whether number is even and return True if it is, or False if it is odd.

Functionality: **The function accepts an integer number and returns True if it is even and False if it is odd.**


Example 2:

Annotated Code:
```
#This is the summary for the whole function and its postcondition is : The function accepts a dictionary `data`, returns `'Key not found'` if the key `'value'` is missing. If the value is not comparable, returns `'Invalid data type'`. If the value is greater than 10, returns `'High'`; otherwise, returns `'Low'`.
def func(data):
    #This is a summary of the whole try-except block and its total postcondition is : `data` is a dictionary that may contain a key `'value'` mapped to a comparable value. If the key `'value'` is not found, the function returns `'Key not found'`. If the value associated with `'value'` cannot be compared with an integer, the function returns `'Invalid data type'`. If the key exists and the value is comparable, the function returns `'High'` if the value is greater than 10, otherwise it returns `'Low'`.
    #This is the try block and its postcondition is : `data` is a dictionary that may contain a key 'value' mapped to a comparable value, and `val` is the value associated with the key 'value' in `data`. If `val` is greater than 10, the function returns 'High'. Otherwise, the function returns 'Low'.
    try:
        #This is simple command in try block and its postcondition is : `data` is a dictionary that may contain a key 'value' mapped to a comparable value, `val` is the value associated with the key 'value' in `data`
        val = data['value']
        #This is a summary of the whole if-else block and its total postcondition is : `data` is a dictionary that may contain a key 'value' mapped to a comparable value, and `val` is the value associated with the key 'value' in `data`. If `val` is greater than 10, the function returns 'High'. Otherwise, the function returns 'Low'.
        #This is the if part of the statement and its postcondition is : `data` is a dictionary that may contain a key 'value' mapped to a comparable value, `val` is the value associated with the key 'value' in `data`, and the function returns 'High'
        if (val > 10) :
            #This is return statement in if part and its postcondition is : `data` is a dictionary that may contain a key 'value' mapped to a comparable value, `val` is the value associated with the key 'value' in `data`, and the function returns 'High'
            return 'High'
        #This is the else statement of the if-else block and its postcondition is : `data` is a dictionary that may contain a key 'value' mapped to a comparable value, `val` is the value associated with the key 'value' in `data`, and the function returns 'Low'
        else :
            #This is return statement in else part and its postcondition is : `data` is a dictionary that may contain a key 'value' mapped to a comparable value, `val` is the value associated with the key 'value' in `data`, and the function returns 'Low'
            return 'Low'
    #This is the except block 1 and its postcondition is : the function returns 'Key not found'
    except (KeyError):
        #This is return statement in except block_1 and its postcondition is : the function returns 'Key not found'
        return 'Key not found'
    #This is the except block 2 and its postcondition is : the state is unknown, and the function returns 'Invalid data type'
    except (TypeError):
        #This is return statement in except block_2 and its postcondition is : the state is unknown, and the function returns 'Invalid data type'
        return 'Invalid data type'
```

Return Postconditions: `data` is a dictionary that may contain a key `'value'` mapped to a comparable value. If the key `'value'` is not found, the function returns `'Key not found'`. If the value associated with `'value'` cannot be compared with an integer, the function returns `'Invalid data type'`. If the key exists and the value is comparable, the function returns `'High'` if the value is greater than 10, otherwise it returns `'Low'`.

Now, please think step by step: What are the parameters the function accepts, and what does it return? What is the functionality of the function? Make sure to notice any potential edge cases and missing logic. Make sure to Adhere to the format Functionality: **Your summary here**

Example Answer 2:  
The function func accepts a single parameter data, which should be a dictionary containing a key 'value' with an integer value. It then attempt to access data['value'] and checks if it is greater than 10. If yes, the function returns 'High'.If no,  the function returns 'Low'. By using exceptions if 'value' key is missing the function returns 'Key not found' and if data is not a dictionary or not subscriptable, returns 'Invalid data type'.
Functionality: The function accepts a dictionary data and returns 'High' if data['value'] is greater than 10, 'Low' if data['value' is 10 or less, 'Key not found' if the key 'value' is absent, and 'Invalid data type' if a type error occurs.

Functionality: **he function accepts a dictionary data and returns 'High' if data['value'] is greater than 10, 'Low' if data['value'] is 10 or less, 'Key not found' if the key 'value' is absent, and 'Invalid data type' if a type error occurs.**



Example 3:

Annotated Code:
```
#This is the summary for the whole function and its postcondition is : The function accepts an integer `n`, calculates the sum of integers from `n` to 0, and decrements `n` to -1. It returns 'not enough resources' if the sum exceeds 100, or 'Division by zero error' if a division by zero occurs.
def func(n):
    #This is simple command and its postcondition is : `n` is an integer, `total` is 0
    total = 0
    #This is a summary of the total loop and its postcondition is : `total` is the sum of integers from the original `n` down to 0, and `n` is decremented to -1.
    while n >= 0:
        total += n
        n -= 1

        # In the following comments we are unrolling the loop 3 times to help you understand its functionality
    #This is a summary of the  whole if block and its total postcondition is : `total` is the sum of integers from the original `n` down to 0, and `n` is decremented to -1. If `total` is greater than 100, the function returns 'not enough resources'.
        #This is Unrolled Loop 1
        #This is simple command in unrolled_loop_1 and its postcondition is : `n` is an integer, `total` is `n`
        total += n
        #This is simple command in unrolled_loop_1 and its postcondition is : `n` is decremented by 1, `total` is the unchanged original value of `n`
        n -= 1
        #This is the summary of unrolled_loop_1 and its total postcondition is : `n` is decremented by 1, `total` is the unchanged original value of `n`
        #This is Unrolled Loop 2
        #This is simple command in unrolled_loop_2 and its postcondition is : `n` is decremented by 1, `total` is increased by `n`
        total += n
        #This is simple command in unrolled_loop_2 and its postcondition is : `n` is decremented by a total of 2, `total` is increased by `n`
        n -= 1
        #This is the summary of unrolled_loop_2 and its total postcondition is : `n` is decremented by a total of 2, `total` is increased by `n`
        #This is Unrolled Loop 3
        #This is simple command in unrolled_loop_3 and its postcondition is : `n` is at least 2, `total` is increased by `2n`
        total += n
        #This is simple command in unrolled_loop_3 and its postcondition is : `n` is at least 1, `total` is increased by `2n`
        n -= 1
        #This is the summary of unrolled_loop_3 and its total postcondition is : `n` is at least 1, `total` is increased by `2n`
    #This is the if part of the statement and its postcondition is : `total` is the sum of integers from the original `n` down to 0, and `n` is decremented to -1, and the function returns 'not enough resources'
    if (total > 100) :
        #This is return statement in if part and its postcondition is : `total` is the sum of integers from the original `n` down to 0, and `n` is decremented to -1, and the function returns 'not enough resources'
        return 'not enough resources'
    #This is a summary of the whole try-except block and its total postcondition is : `total` is the sum of integers from the original `n` down to 0, `n` is decremented to -1, and the function returns 'Division by zero error' due to a division by zero error.
    #This is the try block and its postcondition is : `total` is the sum of integers from the original `n` down to 0, `n` is decremented to -1, a division by zero error occurs, and the function attempts to return an undefined `result`
    try:
        #This is simple command in try block and its postcondition is : `total` is the sum of integers from the original `n` down to 0, and `n` is decremented to -1, and a division by zero error occurs
        result = total / n
        #This is return statement in try block and its postcondition is : `total` is the sum of integers from the original `n` down to 0, `n` is decremented to -1, a division by zero error occurs, and the function attempts to return an undefined `result`
        return result
    #This is the except block 1 and its postcondition is : the state is unknown, and the function returns 'Division by zero error'
    except (ZeroDivisionError):
        #This is return statement in except block_1 and its postcondition is : the state is unknown, and the function returns 'Division by zero error'
        return 'Division by zero error'

```

Return Postconditions: 

Now, please think step by step: What are the parameters the function accepts, and what does it return? What is the functionality of the function? Make sure to notice any potential edge cases and missing logic. Make sure to Adhere to the format Functionality: **Your summary here**

Example Answer 3: The function func accepts an integer n and calculates the sum of integers from n down to 0. It then checks if the sum exceeds 100 and returns 'not enough resources' in that case. Since n is 0 at the end of the loop there is always a division by zero error, and it returns 'Division by zero error'. The functionality of the function is to calculate the sum of integers from n to 0, return 'not enough resources' if the sum is bigger than 100 and an 'Division by 0' error otherwise.


Functionality: **The function accepts an integer `n`, calculates the sum of integers from `n` to 0, and returns 'not enough resources' if the sum exceeds 100, or 'Division by zero error' otherwise**

Example 4:
Annotated Code:
```
#This is the summary for the whole function and its postcondition is : The function accepts a list of integers, sorts the list in ascending order, calculates the index of the middle element, and returns the middle element.
def func(numbers):
    #This is simple command and its postcondition is : numbers list is sorted in ascending order
    numbers.sort()
    #This is simple command and its postcondition is : numbers list is sorted in ascending order, `mid` is the index of the middle element in the list
    mid = len(numbers) // 2
    #This is return statement and its postcondition is : numbers list is sorted in ascending order, `mid` is the index of the middle element in the list, and the function returns the middle element
    return numbers[mid]
```
Return Postconditions: numbers list is sorted in ascending order, `mid` is the index of the middle element in the list, and the function returns the middle element

Now, please think step by step: What are the parameters the function accepts, and what does it return? What is the functionality of the function? Make sure to notice any potential edge cases and missing logic. Make sure to Adhere to the format Functionality: **Your summary here**

Example Answer 4:
The function func accepts a list of integers and sorts the list in ascending order. It then calculates the index of the middle element and returns that element. But if the function has an even number of elements at index mid, but the median should be the average of the two middle elements. The functionality of the function is to find and return the middle element of the sorted list of integers but if the number of elemnts is even it returns one of the middle elements instead of their average.

Functionality: **The function accepts a list of integers, sorts it in ascending order, and returns the middle element. If the list has an even number of elements, it returns one of the middle elements.**


Example 5:
Annotated Code:
```
#This is the summary for the whole function and its postcondition is : The function accepts a parameter numbers, returns the list of integers numbers, and the maximum value in the list or 0.
def func(numbers):
    #This is simple command and its postcondition is : `numbers` is a list of integers, `max_value` is 0
    max_value = 0
    #This is simple command and its postcondition is : `numbers` is a list of integers, `max_value` is 0, `iterator` is an iterator object for `numbers`
    iterator = iter(numbers)
    #This is a summary of the total loop and its postcondition is : `numbers` is a list of integers, `max_value` is either the maximum value in the list or 0. If any `num` in the list is greater than `max_value`, `max_value` is updated to `num`. If a `StopIteration` exception is raised, the program breaks out of the loop.
    while True:
        try:
            num = next(iterator)
            if num > max_value:
                max_value = num
        except StopIteration:
            break
    # In the following comments we are unrolling the loop 1 times to help you understand its functionality
        #This is Unrolled Loop 1
        #This is a summary of the whole try-except block and its total postcondition is : numbers is a list of integers, max_value is the maximum value in the list, iterator is an iterator object for numbers, and num is the first element of the list. If the first element of the list is greater than the current max_value, max_value is updated to be equal to the first element of the list.
        #This is the try block and its postcondition is : `numbers` is a list of integers, `max_value` is the maximum value in the list, `iterator` is an iterator object for `numbers`, and `num` is the first element of the list. If the first element of the list is greater than the current `max_value`, `max_value` is updated to be equal to the first element of the list.
        try:
            #This is simple command in try block and its postcondition is : `numbers` is a list of integers, `max_value` is 0, `iterator` is an iterator object for `numbers`, and `num` is the first element of the list
            num = next(iterator)
            #This is a summary of the  whole if block and its total postcondition is : `numbers` is a list of integers, `max_value` is the maximum value in the list, `iterator` is an iterator object for `numbers`, and `num` is the first element of the list. If the first element of the list is greater than the current `max_value` of  0, `max_value` is updated to be equal to the first element of the list.
            #This is the if part of the statement and its postcondition is : `numbers` is a list of integers, `max_value` is 0, `iterator` is an iterator object for `numbers`, and `num` is the first element of the list
            if (num > max_value) :
                #This is simple command in if part and its postcondition is : `numbers` is a list of integers, `max_value` is the first element of the list, `iterator` is an iterator object for `numbers`, and `num` is the first element of the list
                max_value = num
        #This is the except block 1 and its postcondition is : Unknown
        except (StopIteration):
            #This is simple command in except block_1 and its postcondition is : Unknown
            break
        #This is the summary of unrolled_loop_1 and its total postcondition is : numbers is a list of integers, max_value is the maximum value in the list, iterator is an iterator object for numbers, and num is the first element of the list. If the first element of the list is greater than the current max_value, max_value is updated to be equal to the first element of the list.
     #This is return statement and its postcondition is : `numbers` is a list of integers, `max_value` is either the maximum value in the list or 0
    return max_value
```
Return Postconditions: numbers` is a list of integers, `max_value` is either the maximum value in the list or 0

Now, please think step by step: What are the parameters the function accepts, and what does it return? What is the functionality of the function? Make sure to notice any potential edge cases and missing logic. Make sure to Adhere to the format Functionality: **Your summary here**

Example Answer 5:
The function func accepts a list of integers and finds the maximum value in the list. It initializes max_value to 0 and iterates over the list to find the maximum value. If no number in the list is greater than 0 so if all the numbers are negative the function returns 0. The functionality of the function is to return the maximum value in the list. The function does not handle the case where the list is empty, which could be a potential edge case. And also if all the numbers are negative the function returns 0 which is not the maximum value in the list.

Functionality: **The function accepts a list of integers and returns the maximum value in the list. If all the numbers are negative, it returns 0.**

"""

def summarize_functionality_tree(annotated_code, return_postconditions, model):
    prompt = PROMPT.format(code=annotated_code, returns=return_postconditions)
    response = model.query(prompt)
    post = extract_result(response, "Output State")
    return post

def extract_functionality(response):
    # This function extracts the functionality summary from the response
    # It looks for the line starting with 'Functionality:'
    for line in response.split('\n'):
        if line.strip().startswith('Functionality:'):
            # Return everything after 'Functionality:'
            return line.partition('Functionality:')[2].strip()
    # If not found, return the whole response or handle as needed
    return response.strip()

# # Example usage
# def main():
#     # VariableA (Annotated Code)
#     annotated_code = """
#     # This is a function and its postcondition is: The function accepts a parameter `age` and returns 'adult' if `age` is 18 or older; otherwise, it returns 'minor'.
#     def determine_age_group(age):
#         # This is an if statement and its postcondition is: If `age` is greater than or equal to 18, the function returns 'adult'.
#         if age >= 18:
#             # This is a return statement in the if part and its postcondition is: Returns 'adult' when `age` >= 18.
#             return 'adult'
#         # This is an else statement and its postcondition is: If `age` is less than 18, the function returns 'minor'.
#         else:
#             # This is a return statement in the else part and its postcondition is: Returns 'minor' when `age` < 18.
#             return 'minor'
#     """

#     # VariableB (Return Postconditions)
#     return_postconditions = "The function accepts a parameter `age` and returns 'adult' if `age` is 18 or older; otherwise, it returns 'minor'."

#     # Initialize your model (this is pseudocode)
#     model = YourLLMModel()

#     # Get the functionality summary
#     functionality_summary = summarize_functionality_tree(annotated_code, return_postconditions, model)

#     print("Functionality Summary:")
#     print(functionality_summary)

# if __name__ == "__main__":
#     main()
