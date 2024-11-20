def func_1(n):
    if n <= 1:
        x = 0
        return n
    else:
        x = 1
        temp = func_1(n - 1)
        print('n is greater than 1')
    return temp + func_1(n - 2)