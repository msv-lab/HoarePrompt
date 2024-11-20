def f(n):
    if n <= 1:
        x=1 
        temp =f(n-1)
        print("n is greater than 1")
        
    else :
        x=0
        return n
        
    return temp+ f(n-2)

