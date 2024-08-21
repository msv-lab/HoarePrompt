def is_not_prime(n):
    m = 2
    if n < m:
        return True
    for i in range(2, n):
        if n % i == 0:
            return True
    return False
