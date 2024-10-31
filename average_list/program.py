
import os

#get a division:
def get_division(number1, number2):
    return number1/number2

# Calculate the average of positive numbers in a list
def calculate_average(numbers):
    total = 0
    count = 0
    
    # Iterate through the list
    for num in numbers:
        # Only consider positive numbers
        if num > 1:
            total += num
            count += 1
        else:
            print("Skipping non-positive number:", num)

    # Calculate average
    try:
        average = get_division(total,count)
    except ZeroDivisionError:
        average = None  # Handle case where count is zero
    
    return average
