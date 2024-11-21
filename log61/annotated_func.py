#State of the program right berfore the function call: x is an integer.
def func_1(x):
    if (x > 0) :
        return x + 1
        #The program returns an integer value that is x plus 1, where x is greater than 0.
    else :
        if (x < 0) :
            return x - 1
            #The program returns x minus 1, where x is an integer less than 0, resulting in a value less than -1.
        else :
            return 0
            #The program returns 0
#Overall this is what the function does:
The function accepts an integer `x` and returns `x + 1` if `x` is greater than 0, returns `x - 1` if `x` is less than 0, and returns `0` if `x` is equal to 0. It handles all integer values of `x`, including positive, negative, and zero.

