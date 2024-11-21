#State of the program right berfore the function call: x is a non-negative integer.
def func_1(x):
    if (x > 0) :
        return x + 1
        #The program returns a non-negative integer greater than 1, specifically x + 1 where x is greater than 0
    #State of the program after the if block has been executed: *`x` is a non-negative integer, and `x` is equal to 0.
    x -= 1
    return x
    #The program returns the non-negative integer x, which is equal to -1
#Overall this is what the function does:
The function accepts a non-negative integer `x`. If `x` is greater than 0, it returns `x + 1`. If `x` is equal to 0, it decrements `x` by 1 (resulting in -1) and returns that value. Therefore, the function returns a non-negative integer greater than 1 when `x` is positive, and -1 when `x` is 0. There is no handling for negative values, as the function assumes `x` is always non-negative.

