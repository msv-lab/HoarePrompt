def func_1(x):
    if x > 0:
        x += 1
    elif x == 0:
        x = 10
    elif x < -10:
        x -= 10
    else:
        x = 0
    return x