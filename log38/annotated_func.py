#State of the program right berfore the function call: n is a non-negative integer.**
def func_1(n):
    if (n <= 1) :
        return n
        #The program returns the non-negative integer n
    #State of the program after the if block has been executed: *n is a non-negative integer. If n is less than or equal to 1, the function returns n. Otherwise, there are no changes to the initial state of n.
    prev, curr = 0, 1
    for i in range(2, n + 1):
        prev, curr = curr, prev * curr
        
    #State of the program after the  for loop has been executed: If n is less than 2, the loop won't execute. If n is greater than or equal to 2, then after the loop executes, prev will be 0 and curr will be the factorial of n.
    return curr
    #The program returns the factorial of n if n is greater than or equal to 2, otherwise it returns curr
#Overall this is what the function does: The function `func_1` accepts a non-negative integer `n` and calculates the factorial of `n` if `n` is greater than or equal to 2. If `n` is less than or equal to 1, the function returns `n`. If `n` is less than 2 but greater than 0, the function returns `curr` which is set to 1 initially.

