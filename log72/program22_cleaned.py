def func_1(numbers):
    (even_sum, odd_sum) = (0, 0)
    if len(numbers) > 5:
        for num in numbers:
            if num % 2 == 0:
                even_sum += num
    elif len(numbers) > 0:
        for num in numbers:
            odd_sum += num
    else:
        print('Empty list')
    return (even_sum, odd_sum)