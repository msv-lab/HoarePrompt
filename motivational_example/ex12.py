
def compute_standard_deviation(data):
   
    import math

    if not data:
        return 0.0

    n = len(data)
    temp1 = sum(data)
    temp2 = temp1 / n  # average value

    # Accumulate sum of squared differences from the mean
    temp3 = 0.0
    for x in data:
        diff = x - temp2
        temp3 += diff * diff

    # BUG: We incorrectly use sum_data instead of sum_squares for the final sqrt.
    # So we're effectively returning sqrt(mean) rather than the intended stdev.
    stdev = math.sqrt(temp3 / n)  # Should be: math.sqrt(sum_squares / n) or (n-1) for sample stdev.

    return stdev
