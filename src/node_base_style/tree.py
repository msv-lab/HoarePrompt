
from node_base_style.hoare_triple import pprint_cmd, Triple
# from node_base_style.helper import extract_result
import re

# The prompt as defined earlier

PROMPT = """
You are a program verifier responsible for summarizing the functionality of a Python function.

You are provided with:

1. Annotated Code: The function code with comments that include postconditions at various points.These annotations describe the state of the program at different stages of execution but they may not be accurate or complete. So make sure to consider the actual code as the truth.
2. Return Postconditions: The overall postcondition(s) of the function's execution.

Your Task:

- Analyze the annotated code and the return postconditions.
- Determine what parameters the function accepts and what it returns.
- Provide a concise summary of the function state after it concludes.Please avoid describing how the function operates or implementation details—focus on what the function does from the user's perspective and how it affects the input variables . What is the purpose of the function? what sort of actions does it perform? What is the final state of the progrma after it concludes?

You must adhere to the text format: Functionality: ** Your response here **

Your Task:
Annotated Code:
```
{code}
```

Return Postconditions: {returns}

Now, please think step by step: 
The anotation is there to help you understand the code but the code is the truth. Only include in the functionality, actions that the code actually performs, covering all potential cases.
Use Natural language easily understandable by humans and strictly reply with the format: Functionality: ** your response here **"""

# I am giving you some examples to understand the task better. Then I am giving you your task.


# Example 1:

# Annotated Code:
# ```
# def func(number):
#     if (number % 2 == 0) :
#         return True
#         #State of the program after the return statement: number is an integer
#     #State of the program after the if part has been executed: number is an integer
#     else :
#         return False
#         #State of the program after the return statement: `number` is an integer, and the function returns False
#     #State of the program after the else part has been executed: `number` is an integer, and the function returns False
#     #State of the program after the if-else block has been executed: number is an integer. If number is divisible by 2, the function returns True. Otherwise, the function returns False.
# #Overall this is what the function does: The function accepts a parameter `number` and returns `True` if `number` is divisible by 2. If `number` is not divisible by 2, it returns `False`.
# number is an integer. If number is divisible by 2, the function returns True. Otherwise, the function returns False.
# ```

# Return Postconditions: The function accepts a parameter `number` and returns True if `number` is even; otherwise, it returns False.

# Now, please think step by step: What are the parameters the function accepts, and what does it return? What is the functionality of the function? Make sure to notice any potential edge cases and missing logic. Make sure to adhere to the format Functionality: ** Your summary here **

# Example Answer 1:

# The function func accepts an integer parameter number. According to the annotations, if number is even, it returns True; otherwise, it returns False. Therefore, the functionality of the function is to check whether number is even and return True if it is, or False if it is odd.

# Functionality: ** The function accepts an integer number and returns True if it is even and False if it is odd. **




# Example 2:

# Annotated Code:
# ```
# def func(students):
#     total = 0
#     #State of the program here: `students` is a positive integer, `total` is 0
#     while students >= 1:
#         total += students
#         students -= 1
#     #State of the program after the loop has been executed: If students is a positive integer, the loop will be executed at least once, and total will be equal to the sum of all the numbers from 1 to students, while students will be 0. If students is 0 or negative, the loop will not be executed, and total will remain 0, and students will have the same value as initially.
#     if (total > 100) :
#         return 'not enough money'
#         #State of the program after the return statement: If students is a positive integer, the loop will be executed at least once, and total will be equal to the sum of all the numbers from 1 to students, while students will be 0. If students is 0 or negative, the loop will not be executed, and total will remain 0, and students will have the same value as initially. The function returns 'not enough money'.
#     #State of the program after the if part has been executed: If students is a positive integer, the loop will be executed at least once, and total will be equal to the sum of all the numbers from 1 to students, while students will be 0. If students is 0 or negative, the loop will not be executed, and total will remain 0, and students will have the same value as initially. The function returns 'not enough money'.
#     #State of the program after the if block has been executed: If students is a positive integer, the loop will be executed at least once, and total will be equal to the sum of all the numbers from 1 to students, while students will be 0. If students is 0 or negative, the loop will not be executed, and total will remain 0, and students will have the same value as initially. Additionally, if the total is greater than 100, the function returns 'not enough money'.
#     try:
#         cost_per_student = total / students
#         #State of the program here: If students is a positive integer, total will be equal to the sum of all numbers from 1 to students, cost_per_student will be calculated as the total divided by students. If students is 0 or negative, total will remain 0, and students will have the same value as initially.
#         return cost_per_student
#         #State of the program after the return statement: If students is a positive integer, total will be the sum from 1 to students, cost_per_student will be calculated accordingly. If students is 0 or negative, total will remain 0, and students will retain their initial value. The function returns cost_per_student.
#     #State of the program after the try block has been executed: If students is a positive integer, total will be the sum from 1 to students, cost_per_student will be calculated accordingly. If students is 0 or negative, total will remain 0, and students will retain their initial value. The function returns cost_per_student.
#     except (ZeroDivisionError):
#         return 'Division by zero error'
#         #State of the program after the return statement: unknown, and the function returns 'Division by zero error'
#     #State of the program after the except block has been executed: unknown, and the function returns 'Division by zero error'
#     #State of the program after the try-except block has been executed: If `students` is a positive integer, the function returns the cost per student calculated based on the sum from 1 to `students`. If `students` is 0 or negative, the function returns 'Division by zero error'.
# #Overall this is what the function does: The function accepts a positive integer students and returns 'not enough money', cost per student, or 'Division by zero error' based on certain conditions.

# ```

# Return Postconditions: 
# Case_1: `students` is 0, `total` is the sum of all integers up to the initial value of `students`. If the total amount exceeds 100, the function returns 'not enough money'.

# Case_2: A `ZeroDivisionError` could occur when trying to divide `total` by `students` since `students` is 0. In this case, the function will return 'Division by zero error'. Therefore, the output state is: **`students` is 0, `total` is 0. If the division by zero error occurs, the function returns 'Division by zero error'.**

# Now, please think step by step: What are the parameters the function accepts, and what does it return? What is the functionality of the function? Make sure to notice any potential edge cases and missing logic. Make sure to Adhere to the format Functionality: ** Your summary here **

# Example Answer 3: The function func accepts an integer n and calculates the sum of integers from n down to 0. It then checks if the sum exceeds 100 and returns 'not enough resources' in that case. Since n is 0 at the end of the loop there is always a division by zero error, and it returns 'Division by zero error'. The functionality of the function is to calculate the sum of integers from n to 0, return 'not enough resources' if the sum is bigger than 100 and an 'Division by 0' error otherwise.


# Functionality: ** The function accepts an integer `n`, calculates the sum of integers from `n` to 0, and returns 'not enough resources' if the sum exceeds 100, or 'Division by zero error' otherwise **
def extract_result(s: str, keyword: str):
    pattern = fr"{keyword}:\s*\*\*(.*?)\*\*"
    matches = re.findall(pattern, s, re.DOTALL)
    if matches:
        # Select the last match
        res = matches[-1]
        # Clean up the beginning and end of the string for any weird characters like * or newlines
        return res.strip(), True
    return s, False

def summarize_functionality_tree(annotated_code, return_postconditions, model, retry= True):
    prompt = PROMPT.format(code=annotated_code, returns=return_postconditions)
    response = model.query(prompt)
    post, found = extract_result(response, "Functionality")
    if retry and not found:
        return  summarize_functionality_tree(annotated_code, return_postconditions, model, retry=False)
    return post

def extract_functionality(response):
    # This function extracts the functionality summary from the response
    # It looks for the line starting with 'Functionality:'
    for line in response.split('\n'):
        if line.strip().startswith('Functionality:'):
            # Return everything after 'Functionality:'
            return line.partition('Functionality:')[2].strip() , True
    # If not found, return the whole response or handle as needed
    return response.strip(), False

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
