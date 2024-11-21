#State of the program right berfore the function call: x is an integer.
def func_1(x):
    if (x > 0) :
        x += 1
    else :
        if (x < 0) :
            x -= 1
        #State of the program after the if block has been executed: *`x` is an integer and initially less than or equal to 0. If `x` is less than 0, then after execution, `x` is less than -1. If `x` is equal to 0, `x` remains 0.
    #State of the program after the if-else block has been executed: *`x` is an integer. If `x` is greater than 0, then `x` is incremented by 1. If `x` is less than 0, then `x` is decremented by 1, resulting in `x` being less than -1. If `x` is equal to 0, then `x` remains 0.
    return x
    #The program returns the value of x, which has been adjusted according to its initial value: incremented by 1 if greater than 0, decremented by 1 if less than 0, or remains 0 if equal to 0.
#Overall this is what the function does:
The function accepts an integer `x` and returns `x` incremented by 1 if `x` is greater than 0, decremented by 1 if `x` is less than 0, and remains 0 if `x` is equal to 0.

