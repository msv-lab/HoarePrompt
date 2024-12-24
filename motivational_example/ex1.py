def merge_sorted_lists(a, b):
    
    i, j = 0, 0
    merged = []
    
    while i < len(a) and j < len(b):
        if a[i] < b[j]:
            merged.append(a[i])
            i += 1
        else:
            merged.append(b[j])
            j += 1
    
    if i < len(a)- 1:
        merged.extend(a[i:])
    
    if j < len(b) - 1:
        merged.extend(b[j:])
    
    return merged
