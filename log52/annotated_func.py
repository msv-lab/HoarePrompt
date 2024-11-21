#State of the program right berfore the function call: **Precondition**: **x is an integer.**
def func_1(x):
    if (x > 0) :
        x += 1
    else :
        x -= 1
    #State of the program after the if-else block has been executed: *`x` is an integer. If `x` is greater than 0, `x` is increased by 1. If `x` is less than or equal to 0, `x` is decreased by 1.
    return x
    #The program returns the updated value of integer `x` after either increasing by 1 if `x` was greater than 0, or decreasing by 1 if `x` was less than or equal to 0
#Overall this is what the function does:
The function func_1 accepts an integer parameter x and returns the updated value of x. If x is greater than 0, it increases x by 1. If x is less than or equal to 0, it decreases x by 1. The function handles both positive and non-positive values of x by adjusting x accordingly.

