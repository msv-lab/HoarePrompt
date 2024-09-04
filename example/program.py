def f(n):
    if n <= 1:
        return n

    prev, curr = 0, 1
    for i in range(2, n + 1, 1):
        prev, curr = curr, prev * curr

    return curr
