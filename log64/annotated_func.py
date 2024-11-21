#State of the program right berfore the function call: x is an integer.
def func_1(x):
    if (x > 0) :
        x += 1
    else :
        if (x < 0) :
            if (x < -10) :
                x -= 10
            #State of the program after the if block has been executed: *`x` is an integer. If `x` is less than -10, it is decreased by 10. If `x` is between -10 and 0 (exclusive), it remains unchanged. Overall, `x` is either less than or equal to -10 and decreased by 10, or remains less than 0 but greater than or equal to -10.
        #State of the program after the if block has been executed: *`x` is an integer and less than or equal to 0. If `x` is less than -10, it is decreased by 10, resulting in a value less than or equal to -20. If `x` is between -10 and 0 (exclusive), it remains unchanged and is therefore in the range (-10, 0). In all cases, `x` remains less than or equal to 0.
    #State of the program after the if-else block has been executed: *`x` is an integer. If `x` is greater than 0, then `x` is incremented by 1. If `x` is less than or equal to 0, and if `x` is less than -10, then `x` is decreased by 10, resulting in a value less than or equal to -20. If `x` is between -10 and 0 (exclusive), it remains unchanged and is therefore in the range (-10, 0). In all cases, after execution, `x` is less than or equal to 0.
    return x
    #The program returns x which is less than or equal to 0
#Overall this is what the function does:
The function accepts an integer `x` and returns `x + 1` if `x` is greater than 0. If `x` is less than or equal to 0 and less than -10, it returns `x - 10`, which results in a value less than or equal to -20. If `x` is between -10 and 0 (exclusive), it returns `x` unchanged. Thus, the output is always less than or equal to 0.

