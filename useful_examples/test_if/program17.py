def count_skipped_numbers(numbers):
    i = 0
    skipped = 0
    total = 0
    while i < len(numbers):
        if numbers[i] > 0:
            total += numbers[i]
        else:
            skipped += 1
        i += 1
    return skipped, total
