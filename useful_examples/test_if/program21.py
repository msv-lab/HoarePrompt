def sum_if_not_empty(numbers):
    if len(numbers) > 0:
        total = 0
        for num in numbers:
            total += num
        return total
    return 0
