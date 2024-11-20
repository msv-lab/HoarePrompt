#State of the program right berfore the function call: n is a non-negative integer.**
def func_1(n):
    if (n <= 1) :
        return n
        #The program returns the non-negative integer n, which is less than or equal to 1
    else :
        return func_1(n - 1) + func_1(n - 2)
        #The program returns the sum of the results of calling `func_1` with arguments `n - 1` and `n - 2`.
#Overall this is what the function does:
The function func_1 accepts a non-negative integer n as a parameter and recursively calculates the sum of the results of calling func_1 with arguments n-1 and n-2. The function returns the result of this summation.

