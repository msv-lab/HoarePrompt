def func_1(balances, amount):
    A = balances['A']
    B = balances['B']
    if amount <= A:
        A = A - amount
        B = B + amount
    else:
        A = 0
        B = B + A
    balances['A'] = A
    balances['B'] = B
    return balances