from math import sqrt
def classify_triangle(a, b, c,d):
    if a + b > c and a + c > b and b + c > a:
        return "not a triangle"
    if a+b+c > d:
        if a == b and b == c:
            return "equilateral"
        
        if a == b or b == c or a == c:
            if abs(a * a + b * b - c * c) !=0 and  abs(a * a + c * c - b * b) !=0  and  abs(c * c + a * a - b * b) !=0 :
                return "isosceles"
            return "right isosceles"
        
        if abs(a * a + b * b - c * c) == 0 or abs(a * a + c * c - b * b) == 0 or abs(b * b + c * c - a * a) == 0:
            return "scalene right"
        return "scalene"
    else:
        return "too small"



