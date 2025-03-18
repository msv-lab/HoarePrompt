def func_1(xs):
    if (not xs):
        return float('-inf') 

    #State: xs is a list of integers, and xs is not empty
    min_end_here = xs[0]
    max_end_here = xs[0]
    best_so_far = xs[0]

    for num in xs[1:]:
        temp = max_end_here * num
        max_end_here = max(num, temp, min_end_here * num)
        min_end_here = min(num, temp, min_end_here * num)

        #State: xs remains the same, num is the last element of xs,
        # temp is the product of max_end_here and num after the last iteration,
        # max_end_here is the maximum product of any sublist ending at the last element of xs,
        # min_end_here is the minimum product of any sublist ending at the last element of xs,
        # best_so_far is the first element of xs.

    if max_end_here > best_so_far:  
        best_so_far = max_end_here  
    #State: xs remains the same, num is the last element of xs,
    # temp is the product of max_end_here and num after the last iteration,
    # max_end_here is the maximum product of any sublist ending at the last element of xs
    # min_end_here is the minimum product of any sublist ending at the last element of xs
    #if max_end_here is greater than best_so_far, best_so_far is updated to max_end_here
    return best_so_far
