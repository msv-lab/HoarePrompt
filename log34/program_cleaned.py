def func_1(numbers):
    total = 0
    count = 0
    if len(numbers) == 0:
        return None
    elif len(numbers) == 1:
        return numbers[0]
    else:
        return sum(numbers) / len(numbers)