#State of the program right berfore the function call: x is an integer.
def func_1(x):
    if (x > 0) :
        x += 1
    else :
        if (x < 0) :
            return x - 1
            #The program returns x minus 1, where x is an integer less than 0
        else :
            x = 0
        #State of the program after the if-else block has been executed: `x` is an integer, `x` is less than or equal to 0, and `x` is equal to 0
    #State of the program after the if-else block has been executed: *`x` is an integer. If `x` is greater than 0, then `x` is increased by 1. If `x` is less than 0, the function returns `x - 1`. If `x` is equal to 0, then `x` remains 0.
    return x
    #The program returns the value of x, which is either x + 1 if x > 0, x - 1 if x < 0, or 0 if x = 0.
#Overall this is what the function does:
The function accepts an integer `x` and modifies its value based on the following conditions: if `x` is greater than 0, it returns `x + 1`; if `x` is less than 0, it returns `x - 1`; and if `x` is equal to 0, it returns 0. Thus, the function effectively increments positive integers, decrements negative integers, and returns 0 for zero.

