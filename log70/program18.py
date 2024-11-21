def categorize_numbers(numbers):
    high, medium, low = 0, 0, 0
    for num in numbers:
        if num > 10:
            high += 1
        elif num > 0:
            medium += 1
        else:
            low += 1
    return high, medium, low
