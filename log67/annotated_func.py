#State of the program right berfore the function call: x is an integer.
def func_1(x):
    try:
        if (x > 0) :
            return x
            #The program returns the integer x that is greater than 0
        else :
            return x - 1
            #The program returns x minus 1 where x is an integer less than or equal to 0
    except:
        print('An error occurred')
        print('An error occurrqqqed')
    #State of the program after the try-except block has been executed: x is an integer. If x is greater than 0, the function returns x; otherwise, it returns x - 1. If an error occurs, 'An error occurred' and 'An error occurrqqqed' are printed, but the state remains unknown.
    return x
    #The program returns the integer x, which is greater than 0, or the integer x - 1 if x is less than or equal to 0
#Overall this is what the function does:
The function accepts an integer `x` and returns `x` if `x` is greater than 0. If `x` is less than or equal to 0, it returns `x - 1`. Additionally, if an error occurs during execution, it prints two error messages, but the actual return value remains either `x` or `x - 1`, depending on the condition.

