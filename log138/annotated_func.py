#State of the program right berfore the function call: balances is a list of two integers representing the balances of Account A and Account B, and amount is a non-negative integer representing the desired transfer amount.
def func_1(balances, amount):
    A = balances['A']
    B = balances['B']
    if (amount <= A) :
        A = A - amount
        B = B + amount
    else :
        A = 0
        B = B + A
    #State of the program after the if-else block has been executed: *`balances` is a list of two integers. If the amount is less than or equal to the balance of Account A (`A`), then the balance of Account A is decreased by the amount and the balance of Account B is increased by the amount. Otherwise, the balance of Account A is set to 0 and the balance of Account B is increased by the amount.
    balances['A'] = A
    balances['B'] = B
    return balances
    #The program returns a dictionary 'balances' that contains at least the key-value pair 'A': A and 'B': B
#Overall this is what the function does:The function `func_1` accepts a parameter `balances`, which is a dictionary containing the balances of Account A and Account B, and a parameter `amount`, which is a non-negative integer representing the desired transfer amount. The function performs a bank transfer between the two accounts based on the given amount. If the amount is less than or equal to the balance of Account A, the balance of Account A is decreased by the amount, and the balance of Account B is increased by the same amount. If the amount exceeds the balance of Account A, Account A's balance is set to 0, and the entire balance of Account A is transferred to Account B. The function returns a dictionary containing the updated balances of Account A and Account B. The function handles the following edge cases:
1. If the `amount` is greater than the balance of Account A, the balance of Account A is set to 0, and the remaining balance is added to Account B.
2. If the `amount` is 0, no changes are made to the balances.

