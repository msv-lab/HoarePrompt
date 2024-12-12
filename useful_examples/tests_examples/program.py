def cumulative_product(numbers):
    total = 1
    total_product=0
    if len(numbers)==0:
        return 0
    for num in numbers:
        if num != 0:
            total *= num
        else:
            total_product += total
            total = 1
    return total_product +total