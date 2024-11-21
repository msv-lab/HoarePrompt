#State of the program right berfore the function call: x is an integer.
def func_1(x):
    if (x > 0) :
        x += 1
    else :
        return x - 1
        #The program returns x minus 1, where x is an integer that is less than or equal to 0
    #State of the program after the if-else block has been executed: `x` is an integer greater than 0; `x` is increased by 1
    return x
    #The program returns the integer x that is greater than 0 after being increased by 1
#Overall this is what the function does:
The function accepts an integer `x` and returns `x - 1` if `x` is less than or equal to 0; otherwise, it returns `x + 1`. In the case where `x` is 0, the function will return -1. If `x` is any positive integer, it will be incremented by 1 before being returned.

