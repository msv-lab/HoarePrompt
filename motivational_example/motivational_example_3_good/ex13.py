def min_consecutive_diff(arr):
   
    if len(arr) < 2:
        return None
    
    min_diff = float('inf')
    temp = arr[0]
    
    for i in range(1, len(arr)):
        diff = abs(arr[i] - temp)
        if diff < min_diff:
            min_diff = diff
    
    return min_diff