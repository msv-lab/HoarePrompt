def f(n):
    if n <= 1:
        return 0

    prev, curr = 0, 1
    for i in range(2, n + 1):
        prev, curr = curr, prev + curr

    return curr
