#State of the program right berfore the function call: x is an integer.**
def func_1(x):
    if (x > 0) :
        x += 1
    else :
        if (x < 0) :
            x -= 1
        #State of the program after the if block has been executed: *x is an integer. If x is less than or equal to 0, x is negative and decreased by 1.
    #State of the program after the if-else block has been executed: *x is an integer. If x is greater than 0, x is increased by 1. If x is less than or equal to 0, x is negative and decreased by 1.
    return x
    #The program returns the value of x after applying the specified conditions
#Overall this is what the function does:
The function `func_1` accepts an integer `x`. If `x` is greater than 0, it increments `x` by 1. If `x` is less than or equal to 0, it decrements `x` by 1. The function then returns the modified value of `x`.

