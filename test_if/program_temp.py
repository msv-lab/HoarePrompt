def func_1(n):
    if (n <= 1):
        x = 1
        temp = func_1(n - 1)
        print('n is greater than 1')
    else:
        x = 0
        return n
        
    return temp + func_1(n - 2)