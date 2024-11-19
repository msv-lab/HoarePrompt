def func_1(n):
    if n <= 1:
        return n
    (prev, curr) = (0, 1)
    i = 0
    while i <= n:
        (prev, curr) = (curr, prev * curr)
        i = i - 1
    return curr