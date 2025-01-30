def func_1(xs):
    res = float('-inf')
    for i in range(len(xs)):
        value = 1
        for j in range(i, len(xs)):
            value *= xs[j]
        res = max(res, value)
    return res