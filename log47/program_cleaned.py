def func_1(n):
    if n <= 1:
        return n
    else:
        return func_1(n - 1) + func_1(n - 2)