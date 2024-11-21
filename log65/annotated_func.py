#State of the program right berfore the function call: x is an integer.
def func_1(x):
    if (x > 0) :
        x += 1
    else :
        if (x == 0) :
            x = 10
        else :
            if (x < -10) :
                x -= 10
            else :
                x = 0
            #State of the program after the if-else block has been executed: *`x` is an integer and less than 0. If `x` is less than -10, then `x` is decreased by 10, resulting in `x` being less than -20. If `x` is greater than or equal to -10, the execution leads to a contradiction as `x` cannot be both less than or equal to 0 and greater than or equal to -10. Hence, in the valid case, `x` will always be less than -10 after execution.
        #State of the program after the if-else block has been executed: *`x` is an integer and less than or equal to 0. If `x` is 0, then `x` is set to 10. If `x` is less than -10, then `x` is decreased by 10, resulting in `x` being less than -20. If `x` is greater than or equal to -10 but less than 0, the execution leads to a contradiction, and thus `x` will be set to 0. This ensures that after execution, `x` will either be 10 (if it was originally 0), less than -20 (if it was less than -10), or 0 (if it was in the range -10 to -1).
    #State of the program after the if-else block has been executed: *`x` is an integer. If `x` is greater than 0, then `x` is increased by 1. If `x` is 0, then `x` is set to 10. If `x` is less than -10, then `x` is decreased by 10, resulting in `x` being less than -20. If `x` is between -10 and 0 (inclusive of -1), then `x` is set to 0. Thus, after execution, `x` will be either greater than 1 (if it started greater than 0), equal to 10 (if it started at 0), less than -20 (if it started less than -10), or exactly 0 (if it started between -10 and 0).
    return x
    #The program returns a value for x which is either greater than 1 (if it started greater than 0), equal to 10 (if it started at 0), less than -20 (if it started less than -10), or exactly 0 (if it started between -10 and 0)
#Overall this is what the function does:
The function accepts an integer `x` and modifies it based on the following rules: If `x` is greater than 0, it returns `x + 1`. If `x` is equal to 0, it returns 10. If `x` is less than -10, it returns `x - 10`, resulting in a value less than -20. If `x` is between -10 and 0 (inclusive), it returns 0. Therefore, the function returns a value greater than 1 for positive `x`, 10 for `x` equal to 0, a value less than -20 for `x` less than -10, and 0 for `x` in the range [-10, 0).

