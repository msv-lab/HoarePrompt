def contains_greater_than(numbers, target):
    i = 0
    while i < len(numbers):
        if numbers[i] > target:
            return True
        i += 1
    return False
