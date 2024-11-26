#State of the program right berfore the function call: x is an integer.
def func_1(x):
    if (x > 0) :
        x += 1
    else :
        x -= 1
    #State of the program after the if-else block has been executed: *`x` is an integer. If `x` is greater than 0, it is increased by 1. If `x` is less than or equal to 0, it is decreased by 1, resulting in `x` being either -1 or -2 if it was originally 0, or 0 if it was originally -1.
    return x
    #The program returns x, which is either increased by 1 if initially greater than 0, or decreased by 1, resulting in -1 or -2 if it was originally 0, or 0 if it was originally -1.
#Overall this is what the function does:
The function accepts an integer `x` and returns `x + 1` if `x` is greater than 0. If `x` is 0, it returns -1, and if `x` is -1, it returns 0. For any other negative integer, it decreases `x` by 1. Therefore, the function effectively increments positive integers, sets 0 to -1, sets -1 to 0, and decrements any other negative integers by 1.

