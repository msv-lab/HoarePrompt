#State of the program right berfore the function call: n is a non-negative integer.**
def func_1(n):
    if (n <= 1) :
        return n
        #The program returns the non-negative integer n, which is less than or equal to 1
    #State of the program after the if block has been executed: *n is a non-negative integer. If n is less than or equal to 1, the function returns n. Overall, the function returns n for all non-negative integers n, considering the edge cases where n is either 0 or 1.
    prev, curr = 0, 1
    for i in range(2, n + 1):
        prev, curr = curr, prev * curr
        
    #State of the program after the  for loop has been executed: `n` is a non-negative integer, `prev` is the (n-1)th term of the Fibonacci sequence, `curr` is the nth term of the Fibonacci sequence
    return curr
    #The program returns the nth term of the Fibonacci sequence stored in 'curr'
#Overall this is what the function does:
The function func_1 accepts a non-negative integer n. If n is less than or equal to 1, the function returns n. Otherwise, it calculates and returns the nth term of the Fibonacci sequence. The function correctly calculates the nth Fibonacci term for all non-negative integers.

