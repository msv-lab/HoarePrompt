def sum_positive_numbers(input_list):
    total_sum = 0
    while input_list:  # Continue until the list is empty
        element = input_list.pop()
        if element > 0:
            total_sum += element
    return total_sum
