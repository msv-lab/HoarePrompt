#State of the program right berfore the function call: x is an integer.
def func_1(x):
    if (x > 0) :
        x += 1
    else :
        if (x < -10) :
            x -= 10
        #State of the program after the if block has been executed: *`x` is an integer less than or equal to 0. If `x` is less than -10, then `x` is decreased by 10. If `x` is greater than or equal to -10 but less than or equal to 0, then `x` remains unchanged.
    #State of the program after the if-else block has been executed: *`x` is an integer. If `x` is greater than 0, then `x` is increased by 1. If `x` is less than -10, then `x` is decreased by 10. If `x` is between -10 and 0 (inclusive), then `x` remains unchanged.
    return x
    #The program returns the integer value of x, which is either increased by 1 if greater than 0, remains unchanged if between -10 and 0 (inclusive), or decreased by 10 if less than -10.
#Overall this is what the function does:
The function accepts an integer `x` and returns `x` increased by 1 if `x` is greater than 0; if `x` is between -10 and 0 (inclusive), it returns `x` unchanged; if `x` is less than -10, it returns `x` decreased by 10.

