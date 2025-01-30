
def func_1(xs):
    if not xs:
        return float('-inf')  
    
    min_ending_here = xs[0]
    max_ending_here = xs[0]
    best_so_far = xs[0]
    
    for num in xs[1:]:
       
        temp = max_ending_here * num
        
        max_ending_here = max(num, temp, min_ending_here * num)

        min_ending_here = min(num, temp, min_ending_here * num)
    
    if max_ending_here > best_so_far:
        best_so_far = max_ending_here
    
    return best_so_far