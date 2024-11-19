#State of the program right berfore the function call: n is a non-negative integer.**
def func_1(n):
    if (n <= 1) :
        return n
        #The program returns the non-negative integer n
    #State of the program after the if block has been executed: *n is a non-negative integer. If n is less than or equal to 1, the program returns n. In all other cases where n is greater than 1, there is no change to n.
    prev, curr = 0, 1
    i = 0
    while i <= n:
        prev, curr = curr, prev * curr
        
        i = i + 1
        
    #State of the program after the loop has been executed: `prev` is the Fibonacci number at index n, `curr` is the Fibonacci number at index n+1, `i` is n+1
    return curr
    #The program returns the Fibonacci number at index n+1, which is stored in variable `curr`
#Overall this is what the function does:
The function `func_1` accepts a non-negative integer `n`. If `n` is less than or equal to 1, the function returns `n`. For all other cases where `n` is greater than 1, the function calculates the Fibonacci number at index n+1 and returns that value. The function correctly computes the Fibonacci sequence, updating `prev` and `curr` variables accordingly in a loop.

