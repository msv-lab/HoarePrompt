def test_function_calls():
    x = 10
    y = 20
    print("Sum:", x + y)
    try :
        z = max(x, y)
    except Exception as e:
        print(e)
    print("Max:", z)
    pass
