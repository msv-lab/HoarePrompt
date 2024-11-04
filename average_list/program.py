
# import os

# #get a division:
# # def get_division(number1, number2):
# #     return number1/number2

# # Calculate the average of positive numbers in a list
# def calculate_average(numbers):
#     total = 0
#     count = 0
    
#     # Iterate through the list
#     for num in numbers:
#         # Only consider positive numbers
#         if num > 1:
#             total += num
#             count += 1
#         else:
#             print("Skipping non-positive number:", num)

#     # Calculate average
#     try:
#         average = total/count
#     except ZeroDivisionError:
#         average = None  # Handle case where count is zero
    
#     return average
#This is the summary for the whole function and its postcondition is : The function accepts a list of integers, sorts the list in ascending order, calculates the index of the middle element, and returns the middle element.
#This is the summary for the whole function and its postcondition is : The function accepts a parameter numbers, returns the list of integers numbers, and the maximum value in the list or 0.
def func(numbers):
    #This is simple command and its postcondition is : `numbers` is a list of integers, `max_value` is 0
    max_value = 0
    #This is simple command and its postcondition is : `numbers` is a list of integers, `max_value` is 0, `iterator` is an iterator object for `numbers`
    for i in range(len(numbers)):
        #This is simple command and its postcondition is : `numbers` is a list of integers, `max_value` is 0, `iterator` is an iterator object for `numbers`, `num` is the ith element of `numbers`
        num = numbers[i]
        #This is simple command and its postcondition is : `numbers` is a list of integers, `max_value` is 0, `iterator` is an iterator object for `numbers`, `num` is the ith element of `numbers`, `max_value` is the maximum of `max_value` and `num`
        if num > max_value:
            max_value = num
    return max_value