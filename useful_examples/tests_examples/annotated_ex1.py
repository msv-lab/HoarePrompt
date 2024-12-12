#State of the program right berfore the function call: numbers is a list of integers.
def func_1(numbers):
    total = 1
    total_product = 0
    if (len(numbers) == 0) :
        return 0
        #The program returns 0
    #State of the program after the if block has been executed: *`numbers` is a list of integers, `total` is 1, `total_product` is 0, and the length of `numbers` is greater than 0
    for num in numbers:
        if num != 0:
            total *= num
        else:
            total_product += total
            total = 1
        
    #State of the program after the  for loop has been executed: `total_product` is the sum of the products of all sequences of non-zero integers in `numbers`, `total` is the last product of a sequence of non-zero integers in 'numbers' or 1, and `numbers` is a list of integers.
    return total_product + total
    #The program returns the sum of total_product, which is the sum of the products of all sequences of non-zero integers in 'numbers', and total, which is the last product of a sequence of non-zero integers in 'numbers' or 1.
#Overall this is what the function does: The function accepts a list of integers, returning 0 if the list is empty. If the list contains integers, the function calculates the sum of the products of all contiguous sequences of non-zero integers, adding 1 (the initial value of `total`) to this sum for the final result. If the list contains zeros, those reset the product calculation for the current sequence.

