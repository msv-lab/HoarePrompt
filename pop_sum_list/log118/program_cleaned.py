def func_1(input_list):
    total_sum = 0
    while input_list:
        element = input_list.pop()
        if element > 0:
            total_sum += element
    return total_sum