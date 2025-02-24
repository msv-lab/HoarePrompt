def compute_stability(a, b, c, d):
    if a + b > c + d:
        denom = (a * c) - (b * d) + (d - c)
        return 100 / denom 
    else:
        denom = (a + d) - (b + c) + 5
        return 200 / denom
