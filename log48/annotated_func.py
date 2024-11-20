#State of the program right berfore the function call: n is a non-negative integer.**
def func_1(n):
    if (n <= 1) :
        x = 0
        return n
        #The program returns the non-negative integer 'n' which is less than or equal to 1
    else :
        x = 1
        temp = func_1(n - 1)
        print('n is greater than 1')
    #State of the program after the if-else block has been executed: n is a non-negative integer larger than 1, x is 1, temp is the result of func_1(n - 1), 'n is greater than 1' is printed
    return temp + func_1(n - 2)
    #The program returns the result of func_1(n - 1) added to the result of func_1(n - 2), where n is a non-negative integer larger than 1. The statement 'n is greater than 1' is printed during execution.
#Overall this is what the function does:
The function `func_1` recursively calculates the sum of the results of `func_1(n - 1)` and `func_1(n - 2)` for a non-negative integer `n`. If `n` is less than or equal to 1, the function returns `n`. If `n` is greater than 1, the function returns the sum of the results of `func_1(n - 1)` and `func_1(n - 2)`. During execution, the statement 'n is greater than 1' is printed.

