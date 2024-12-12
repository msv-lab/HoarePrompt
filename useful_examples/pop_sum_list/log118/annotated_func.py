#State of the program right berfore the function call: input_list is a list of integers.
def func_1(input_list):
    total_sum = 0
    while input_list:
        element = input_list.pop()
        
        if element > 0:
            total_sum += element
        
    #State of the program after the loop has been executed: `input_list` is empty, `total_sum` is the sum of all positive integers from the original `input_list`.
    return total_sum
    #The program returns total_sum, which is the sum of all positive integers from the original input_list, where input_list is empty and thus total_sum is 0.
#Overall this is what the function does:The function accepts a list of integers and returns the sum of all positive integers in that list. If the list is empty or contains no positive integers, it returns 0.

