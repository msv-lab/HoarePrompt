def func_1(numbers):
    total = 0
    count = 0
    while numbers:
        num = numbers.pop()
        if num > 1:
            total += num
            count += 1
        else:
            print('Skipping non-positive number:', num)
    if count == 0:
        return None
    else:
        average = total / count
    return average