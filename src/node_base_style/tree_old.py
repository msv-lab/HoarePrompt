
from node_base_style.hoare_triple import pprint_cmd, Triple
from node_base_style.helper import extract_result

# The prompt as defined earlier

PROMPT = """
You are a program verifier responsible for summarizing the functionality of a Python function.

You are provided with:

1. Annotated Code: The function code with comments that include postconditions at various points.
2. Return Postconditions: The overall postcondition(s) of the function's execution.

Your Task:

- Analyze the annotated code and the return postconditions.
- Determine what parameters the function accepts and what it returns.
- Provide a concise summary of the function's functionality.
- Keep in mind that some of the annotations may be redundant, irrelevant or missing some important edgecases so try to keep the context of the actual code in mind as well.
- Also if the annotations say that the code does something but the code has some missing functionality, make sure to include that missing functionality in your summary.
Please avoid describing how the function operates or implementation details—focus on what the function does from the user's perspective.

You must adhere to the text format: Functionality: ** Your summary here **
I am giving you some examples to understand the task better. Then I am giving you your task.


Example 1:

Annotated Code:
```
def func(number):
    if (number % 2 == 0) :
        return True
        #State of the program after the return statement: number is an integer
    #State of the program after the if part has been executed: number is an integer
    else :
        return False
        #State of the program after the return statement: `number` is an integer, and the function returns False
    #State of the program after the else part has been executed: `number` is an integer, and the function returns False
    #State of the program after the if-else block has been executed: number is an integer. If number is divisible by 2, the function returns True. Otherwise, the function returns False.
#Overall this is what the function does: The function accepts a parameter `number` and returns `True` if `number` is divisible by 2. If `number` is not divisible by 2, it returns `False`.
number is an integer. If number is divisible by 2, the function returns True. Otherwise, the function returns False.
```

Return Postconditions: The function accepts a parameter `number` and returns True if `number` is even; otherwise, it returns False.

Now, please think step by step: What are the parameters the function accepts, and what does it return? What is the functionality of the function? Make sure to notice any potential edge cases and missing logic. Make sure to adhere to the format Functionality: ** Your summary here **

Example Answer 1:

The function func accepts an integer parameter number. According to the annotations, if number is even, it returns True; otherwise, it returns False. Therefore, the functionality of the function is to check whether number is even and return True if it is, or False if it is odd.

Functionality: ** The function accepts an integer number and returns True if it is even and False if it is odd. **


Example 2:

Annotated Code:
```
def func(data):
    try:
        val = data['value']
        #State of the program here: data is a dictionary with a key 'value' containing an integer value, `val` is assigned the integer value from the dictionary
        if (val > 10) :
            return 'High'
            #State of the program after the return statement: data is a dictionary with a key 'value' containing an integer value, `val` is assigned that integer value, and the function returns 'High'
        #State of the program after the if part has been executed: data is a dictionary with a key 'value' containing an integer value, `val` is assigned that integer value, and the function returns 'High'
        else :
            return 'Low'
            #State of the program after the return statement: data is a dictionary with a key 'value' containing an integer value, `val` is assigned the integer value from the dictionary, and the function returns 'Low'
        #State of the program after the else part has been executed: data is a dictionary with a key 'value' containing an integer value, `val` is assigned the integer value from the dictionary, and the function returns 'Low'
        #State of the program after the if-else block has been executed: data is a dictionary with a key 'value' containing an integer value, `val` is assigned the integer value from the dictionary. If the value of `val` is greater than 10, the function returns 'High'. Otherwise, the function returns 'Low'.
    #State of the program after the try block has been executed: data is a dictionary with a key 'value' containing an integer value, `val` is assigned the integer value from the dictionary. If the value of `val` is greater than 10, the function returns 'High'. Otherwise, the function returns 'Low'.
    except (KeyError):
        return 'Key not found'
        #State of the program after the return statement: The function returns 'Key not found'
    #State of the program after the except block has been executed: The function returns 'Key not found'
    except (TypeError):
        return 'Invalid data type'
        #State of the program after the return statement: function returns 'Invalid data type'
    #State of the program after the except block has been executed: function returns 'Invalid data type'
    #State of the program after the try-except block has been executed: A `KeyError` could be triggered at `val = data['value']` if the key 'value' is not found in the dictionary. If a `TypeError` occurs, it would be due to the data type mismatch when trying to access the 'value' key. If neither exception occurs, the function checks the value of `val` and returns 'High' if it's greater than 10, otherwise 'Low'. Therefore, the output state is: **data is a dictionary with a key 'value' containing an integer value. If the key 'value' is not found, the function returns 'Key not found'. If there is a data type mismatch, the function returns 'Invalid data type'. If the value of 'value' is greater than 10, the function returns 'High', otherwise, it returns 'Low'.**
#Overall this is what the function does: data is a dictionary with a key 'value' containing an integer value. If the key 'value' is not found, the function returns 'Key not found'. If there is a data type mismatch, the function returns 'Invalid data type'. If the value of 'value' is greater than 10, the function returns 'High', otherwise, it returns 'Low'.
A `KeyError` could be triggered at `val = data['value']` if the key 'value' is not found in the dictionary. If a `TypeError` occurs, it would be due to the data type mismatch when trying to access the 'value' key. If neither exception occurs, the function checks the value of `val` and returns 'High' if it's greater than 10, otherwise 'Low'. Therefore, the output state is: **data is a dictionary with a key 'value' containing an integer value. If the key 'value' is not found, the function returns 'Key not found'. If there is a data type mismatch, the function returns 'Invalid data type'. If the value of 'value' is greater than 10, the function returns 'High', otherwise, it returns 'Low'.**

```

Return Postconditions: `data` is a dictionary that may contain a key `'value'` mapped to a comparable value. If the key `'value'` is not found, the function returns `'Key not found'`. If the value associated with `'value'` cannot be compared with an integer, the function returns `'Invalid data type'`. If the key exists and the value is comparable, the function returns `'High'` if the value is greater than 10, otherwise it returns `'Low'`.

Now, please think step by step: What are the parameters the function accepts, and what does it return? What is the functionality of the function? Make sure to notice any potential edge cases and missing logic. Make sure to adhere to the format Functionality: ** Your summary here **

Example Answer 2:  
The function func accepts a single parameter data, which should be a dictionary containing a key 'value' with an integer value. It then attempt to access data['value'] and checks if it is greater than 10. If yes, the function returns 'High'.If no,  the function returns 'Low'. By using exceptions if 'value' key is missing the function returns 'Key not found' and if value is not the correct type for the dictionary key , it returns 'Invalid data type'.
Functionality: The function accepts a dictionary data and returns 'High' if data['value'] is greater than 10, 'Low' if data['value'] is 10 or less, 'Key not found' if the key 'value' is absent, and 'Invalid data type' if a type error occurs.

Functionality: ** The function accepts a dictionary data and returns 'High' if data['value'] is greater than 10, 'Low' if data['value'] is 10 or less, 'Key not found' if the key 'value' is absent, and 'Invalid data type' if a type error occurs.**



Example 3:

Annotated Code:
```
def func(students):
    total = 0
    #State of the program here: `students` is a positive integer, `total` is 0
    while students >= 1:
        total += students
        students -= 1
        # In the following comments we are unrolling the loop 3 times to help you understand its functionality
         #state of the program after unrolled loop 1: `students` is 1 less than the initial value of `total` 
        #state of the program after unrolled loop 2: `students` is 1 less than the new value of `total` and greater or equal to 1; `total` is 2 times the initial value of `total` minus 1 
        #state of the program after unrolled loop 3: `students` is 2, `total` is 2 
    #State of the program after the loop has been executed: If students is a positive integer, the loop will be executed at least once, and total will be equal to the sum of all the numbers from 1 to students, while students will be 0. If students is 0 or negative, the loop will not be executed, and total will remain 0, and students will have the same value as initially.
    if (total > 100) :
        return 'not enough money'
        #State of the program after the return statement: If students is a positive integer, the loop will be executed at least once, and total will be equal to the sum of all the numbers from 1 to students, while students will be 0. If students is 0 or negative, the loop will not be executed, and total will remain 0, and students will have the same value as initially. The function returns 'not enough money'.
    #State of the program after the if part has been executed: If students is a positive integer, the loop will be executed at least once, and total will be equal to the sum of all the numbers from 1 to students, while students will be 0. If students is 0 or negative, the loop will not be executed, and total will remain 0, and students will have the same value as initially. The function returns 'not enough money'.
    #State of the program after the if block has been executed: If students is a positive integer, the loop will be executed at least once, and total will be equal to the sum of all the numbers from 1 to students, while students will be 0. If students is 0 or negative, the loop will not be executed, and total will remain 0, and students will have the same value as initially. Additionally, if the total is greater than 100, the function returns 'not enough money'.
    try:
        cost_per_student = total / students
        #State of the program here: If students is a positive integer, total will be equal to the sum of all numbers from 1 to students, cost_per_student will be calculated as the total divided by students. If students is 0 or negative, total will remain 0, and students will have the same value as initially.
        return cost_per_student
        #State of the program after the return statement: If students is a positive integer, total will be the sum from 1 to students, cost_per_student will be calculated accordingly. If students is 0 or negative, total will remain 0, and students will retain their initial value. The function returns cost_per_student.
    #State of the program after the try block has been executed: If students is a positive integer, total will be the sum from 1 to students, cost_per_student will be calculated accordingly. If students is 0 or negative, total will remain 0, and students will retain their initial value. The function returns cost_per_student.
    except (ZeroDivisionError):
        return 'Division by zero error'
        #State of the program after the return statement: unknown, and the function returns 'Division by zero error'
    #State of the program after the except block has been executed: unknown, and the function returns 'Division by zero error'
    #State of the program after the try-except block has been executed: If `students` is a positive integer, the function returns the cost per student calculated based on the sum from 1 to `students`. If `students` is 0 or negative, the function returns 'Division by zero error'.
#Overall this is what the function does: The function accepts a positive integer students and returns 'not enough money', cost per student, or 'Division by zero error' based on certain conditions.

```

Return Postconditions: 
Case_1: `students` is 0, `total` is the sum of all integers up to the initial value of `students`. If the total amount exceeds 100, the function returns 'not enough money'.

Case_2: A `ZeroDivisionError` could occur when trying to divide `total` by `students` since `students` is 0. In this case, the function will return 'Division by zero error'. Therefore, the output state is: **`students` is 0, `total` is 0. If the division by zero error occurs, the function returns 'Division by zero error'.**

Now, please think step by step: What are the parameters the function accepts, and what does it return? What is the functionality of the function? Make sure to notice any potential edge cases and missing logic. Make sure to Adhere to the format Functionality: ** Your summary here **

Example Answer 3: The function func accepts an integer n and calculates the sum of integers from n down to 0. It then checks if the sum exceeds 100 and returns 'not enough resources' in that case. Since n is 0 at the end of the loop there is always a division by zero error, and it returns 'Division by zero error'. The functionality of the function is to calculate the sum of integers from n to 0, return 'not enough resources' if the sum is bigger than 100 and an 'Division by 0' error otherwise.


Functionality: ** The function accepts an integer `n`, calculates the sum of integers from `n` to 0, and returns 'not enough resources' if the sum exceeds 100, or 'Division by zero error' otherwise **

Example 4:
Annotated Code:
```
def func(numbers):
    numbers.sort()
    #State of the program here: numbers is a sorted list of integers
    mid = len(numbers) // 2
    #State of the program here: numbers is a sorted list of integers, `mid` is the index of the middle element in the list
    return numbers[mid]
    #State of the program after the return statement: numbers is a sorted list of integers, mid is the index of the middle element in the list, and the function returns the element at the middle index
#Overall this is what the function does: The function accepts a list of integers, sorts the list, calculates the middle index, and returns the element at the middle index.
numbers is a sorted list of integers, mid is the index of the middle element in the list, and the function returns the element at the middle index

```
Return Postconditions: numbers list is sorted in ascending order, `mid` is the index of the middle element in the list, and the function returns the middle element

Now, please think step by step: What are the parameters the function accepts, and what does it return? What is the functionality of the function? Make sure to notice any potential edge cases and missing logic. Make sure to adhere to the format Functionality: ** Your summary here **

Example Answer 4:
The function func accepts a list of integers and sorts the list in ascending order. It then calculates the index of the middle element and returns that element. But if the function has an even number of elements at index mid, but the median should be the average of the two middle elements. Also if the list is empty an out ob bounds error will occur. The functionality of the function is to find and return the middle element of the sorted list of integers but if the number of elemnts is even it returns one of the middle elements instead of their average and if the list is empty an error occurs.

Functionality: ** The function accepts a list of integers, sorts it in ascending order, and returns the middle element. If the list has an even number of elements, it returns one of the middle elements. If the list is empty an error occurs **



The function func accepts a list of integers and sorts the list in ascending order. It then calculates the index of the middle element and returns that element. But if the function has an even number of elements at index mid, but the median should be the average of the two middle elements. The functionality of the function is to find and return the middle element of the sorted list of integers but if the number of elemnts is even it returns one of the middle elements instead of their average.

Functionality: **The function accepts a list of integers, sorts it in ascending order, and returns the middle element. If the list has an even number of elements, it returns one of the middle elements.**


Example 5:
Annotated Code:
```
def func(numbers):
    max_value = 0
    #State of the program here: `numbers` is a list of integers, `max_value` is 0
    iterator = iter(numbers)
    #State of the program here: `numbers` is a list of integers, `max_value` is 0, and an iterator is created
    while True:
        try:
            num = next(iterator)
            if num > max_value:
                max_value = num
        except StopIteration:
            break
        # In the following comments we are unrolling the loop 3 times to help you understand its functionality
         #state of the program after unrolled loop 1: `numbers` is a list of integers, `max_value` is the maximum value between its current value and the value of `num`, and an iterator has been created where `num` is assigned the next value from the iterator. If a `StopIteration` occurs, the program breaks without affecting any variables. 
        #state of the program after unrolled loop 2: `numbers` is a list of integers, `max_value` is the maximum value between its current value and the value of `num`, and `num` has been updated to the next value from the iterator. If `num` is greater than the current value of `max_value`, then `max_value` is updated to `num`. If a `StopIteration` exception is raised, the program breaks. 
        #state of the program after unrolled loop 3: `numbers` is a list of integers, `max_value` is the maximum value between its current value and the value of `num`, and `num` has been updated to the next value from the iterator. If a `StopIteration` exception occurs, the loop breaks. 
    #State of the program after the loop has been executed: Output State: `numbers` is a list of integers, `max_value` is the maximum value among all integers in the list, and the iterator has reached the end. If the list is empty, `max_value` remains 0 and the loop breaks without any changes to the variables. If the iterator is not properly initialized or the `next` function is called beyond the end of the list, an exception will occur.
    return max_value
    #State of the program after the return statement: `numbers` is a list of integers, `max_value` is the maximum value among all integers in the list, and the iterator has reached the end. If the list is empty, `max_value` remains 0 and the loop breaks without any changes to the variables. If the iterator is not properly initialized or the `next` function is called beyond the end of the list, an exception will occur. The function returns the `max_value`.
#Overall this is what the function does: The function accepts a parameter `numbers`, which is a list of integers, and returns the maximum value among all integers in the list. If the list is empty, the `max_value` remains 0.
`numbers` is a list of integers, `max_value` is the maximum value among all integers in the list, and the iterator has reached the end. If the list is empty, `max_value` remains 0 and the loop breaks without any changes to the variables. If the iterator is not properly initialized or the `next` function is called beyond the end of the list, an exception will occur. The function returns the `max_value`.

```
Return Postconditions: numbers` is a list of integers, `max_value` is either the maximum value in the list or 0

Now, please think step by step: What are the parameters the function accepts, and what does it return? What is the functionality of the function? Make sure to notice any potential edge cases and missing logic. Make sure to Adhere to the format Functionality: ** Your summary here **

Example Answer 5:
The function func accepts a list of integers and finds the maximum value in the list. It initializes max_value to 0 and iterates over the list to find the maximum value. If no number in the list is greater than 0 so if all the numbers are negative the function returns 0. The functionality of the function is to return the maximum value in the list. The function does not handle the case where the list is empty, which could be a potential edge case. And also if all the numbers are negative the function returns 0 which is not the maximum value in the list.

Functionality: ** The function accepts a list of integers and returns the maximum value in the list. If all the numbers are negative, it returns 0 instead of the maximum **


Your Task:
Annotated Code:
```
{code}
```

Return Postconditions: {returns}

Now, please think step by step: What are the parameters the function accepts, and what does it return? What is the functionality of the function? Make sure to notice any potential edge cases and missing logic. Make sure to adhere to the format Functionality: ** Your summary here **
Look if there is any missing logic or edge cases that the code is not handling. If the code does not do what the annotations say for every potential case make sure to include these potential cases in the functionality. 
You are trying to find any potential case that the porgram does not does what the descriptions says. 
Include all potential edge cases and missing functionality if it exists inside your summary with the format . Functionality: ** your summary here **"""



def summarize_functionality_tree(annotated_code, return_postconditions, model):
    prompt = PROMPT.format(code=annotated_code, returns=return_postconditions)
    response = model.query(prompt)
    post = extract_result(response, "Functionality")
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
