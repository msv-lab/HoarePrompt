#State of the program right berfore the function call: n is a non-negative integer.**
def func_1(n):
    if (n <= 1) :
        return n
        #The program returns the non-negative integer n
    #State of the program after the if block has been executed: *n is a non-negative integer. If n is less than or equal to 1, the function returns n. Otherwise, there is no change to the state of n after the execution of the if statement.
    prev, curr = 0, 1
    for i in range(2, n + 1):
        prev, curr = curr, prev * curr
        
    #State of the program after the  for loop has been executed: `n` is a non-negative integer, `prev` is the last value of `curr` after the loop finishes, `curr` is the last value of `prev` after the loop finishes
    return curr
    #The program returns the last value of 'prev' after the loop finishes
#Overall this is what the function does:
The function `func_1` accepts a non-negative integer `n`. If `n` is less than or equal to 1, the function returns `n`. If `n` is greater than 1, the function calculates the Fibonacci sequence up to the `n`th element and returns the value at that position.

