#State of the program right berfore the function call: numbers is a list of integers, and all integers in the list should be non-negative.
def func_1(numbers):
    total = 0
    for num in numbers:
        if num > 0:
            total += num
        
    #State of the program after the  for loop has been executed: `total` is the sum of all positive integers in `numbers`, `numbers` is a list of integers.
    return total
    #The program returns the sum of all positive integers in the list 'numbers' represented by the variable 'total'
#Overall this is what the function does:
The function accepts a list of non-negative integers `numbers` and returns the sum of all positive integers in that list. It ignores any zeros and does not perform any error handling for negative integers, though the expectation is that all integers should be non-negative. If all integers are zero, the function will return 0.

