def f(n):
    if n <= 1:
        x=0
        return n
    else :
        x=1 
        temp =f(n-1)
        print("n is greater than 1")
        
    return temp+ f(n-2)

