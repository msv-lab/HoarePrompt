#State of the program right berfore the function call: x is an integer.
def func_1(x):
    if (x > 0) :
        if (x > 10) :
            x += 10
        #State of the program after the if block has been executed: *`x` is an integer greater than 0. If `x` is greater than 10, then `x` is increased by 10. If `x` is between 1 and 10 (inclusive), it remains unchanged.
    #State of the program after the if block has been executed: *`x` is an integer. If `x` is greater than 10, then `x` is increased by 10. If `x` is between 1 and 10 (inclusive), it remains unchanged. If `x` is less than or equal to 0, the value of `x` is unchanged.
    return x
    #The program returns the value of x, which remains unchanged if x is between 1 and 10 (inclusive), or unchanged if x is less than or equal to 0, or increased by 10 if x is greater than 10.
#Overall this is what the function does:
The function accepts an integer `x` and returns `x` unchanged if it is between 1 and 10 (inclusive) or if `x` is less than or equal to 0. If `x` is greater than 10, it returns `x` increased by 10.

