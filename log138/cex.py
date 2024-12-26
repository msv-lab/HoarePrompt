def func_1(balances, amount):
    A = balances['A']
    B = balances['B']
    if amount <= A:
        A = A - amount
        B = B + amount
    else:
        A = 0
        B = B + A
    balances['A'] = A
    balances['B'] = B
    return balances

from ex3 import func_1

def test_func_1():
    # Initial balances: A = 5, B = 10
    balances = {'A': 5, 'B': 10}
    amount = 7
    
    # Expected output: A = 0, B = 15 (since only 5 can be transferred)
    expected_output = {'A': 0, 'B': 15}
    
    # Actual output
    actual_output = func_1(balances.copy(), amount)
    
    # Asserting the expected output matches the actual output
    assert actual_output == expected_output, f"Expected {expected_output}, but got {actual_output}"
    
    # Additional checks to ensure the function works as expected in other scenarios
    balances = {'A': 10, 'B': 5}
    amount = 15
    expected_output = {'A': 0, 'B': 15}
    actual_output = func_1(balances.copy(), amount)
    assert actual_output == expected_output, f"Expected {expected_output}, but got {actual_output}"
    
    balances = {'A': 3, 'B': 8}
    amount = 2
    expected_output = {'A': 1, 'B': 9}
    actual_output = func_1(balances.copy(), amount)
    assert actual_output == expected_output, f"Expected {expected_output}, but got {actual_output}"
    
    balances = {'A': 10, 'B': 5}
    amount = 5
    expected_output = {'A': 0, 'B': 10}
    actual_output = func_1(balances.copy(), amount)
    assert actual_output == expected_output, f"Expected {expected_output}, but got {actual_output}"
    
    print("All tests passed!")

# Run the test function
test_func_1()

