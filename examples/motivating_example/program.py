def func_1(xs):
    if not xs:
        return float('-inf')

    min_end_here = xs[0]
    max_end_here = xs[0]
    best_so_far = xs[0]

    for num in xs[1:]:
        temp = max_end_here * num
        max_end_here = max(num, temp, min_end_here * num)
        min_end_here = min(num, temp, min_end_here * num)

    if max_end_here > best_so_far:  
        best_so_far = max_end_here  

    return best_so_far
