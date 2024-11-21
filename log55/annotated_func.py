#State of the program right berfore the function call: x is an integer.
def func_1(x):
    if (x > 0) :
        x += 1
    else :
        if (x < 0) :
            x -= 1
        else :
            x = 0
        #State of the program after the if-else block has been executed: *`x` is an integer and `x` is less than or equal to 0. If `x` is less than 0, it is decreased by 1, resulting in a value that is strictly less than its original value. If `x` is exactly 0, it remains 0 after execution.
    #State of the program after the if-else block has been executed: *`x` is an integer. If `x` is greater than 0, then `x` is increased by 1, resulting in a value greater than 1. If `x` is less than 0, then `x` is decreased by 1, resulting in a value that is strictly less than its original value. If `x` is exactly 0, then `x` remains 0 after execution.
    return x
    #The program returns the integer value of x, which can be greater than 1 if initially greater than 0, strictly less than its original value if initially less than 0, or remains 0 if initially exactly 0.
#Overall this is what the function does:
The function accepts an integer `x` and returns an integer greater than `x` if `x` is greater than 0, strictly less than `x` if `x` is less than 0, or returns 0 if `x` is exactly 0. Specifically, if `x` is positive, it increments `x` by 1. If `x` is negative, it decrements `x` by 1, making it closer to zero but still negative. If `x` is zero, it remains zero after execution.

