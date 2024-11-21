#State of the program right berfore the function call: numbers is a list of integers.
def func_1(numbers):
    if (len(numbers) > 0) :
        total = 0
        for num in numbers:
            total += num
            
        #State of the program after the  for loop has been executed: `total` is equal to the sum of all integers in `numbers`, `numbers` is a list of integers with length greater than 0.
        return total
        #The program returns the total, which is equal to the sum of all integers in the list 'numbers'
    #State of the program after the if block has been executed: *`numbers` is a list of integers, and `numbers` is an empty list.
    return 0
    #The program returns 0
#Overall this is what the function does:
The function accepts a list of integers and returns the sum of all integers in the list if it is not empty. If the list is empty, it returns 0.

