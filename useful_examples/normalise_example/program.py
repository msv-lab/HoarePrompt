def normalize(numbers):
    total = sum(numbers)
    return [x / total for x in numbers]