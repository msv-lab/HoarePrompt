#State of the program right berfore the function call: x is an integer.**
def func_1(x):
    if (x > 0) :
        x += 1
    #State of the program after the if block has been executed: *x is an integer. If x is greater than 0, then x is incremented by 1.
    return x
    #The program returns the integer x, which is either incremented by 1 if x is greater than 0 or remains the same if x is less than or equal to 0.
#Overall this is what the function does:
The function accepts an integer parameter x and returns x incremented by 1 if x is greater than 0; otherwise, it returns x as it is.

