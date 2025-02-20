def transfer_funds(balances, amount):
 
    A = balances['A']
    B = balances['B']
    
    if amount <= A:
        print(F"Amount: {amount} IS LESS THAN OR EQUAL TO A: {A}")
        A = A - amount
        B = B + amount
    else:
        A = 0
        B = B + A  
    balances['A'] = A
    balances['B'] = B
    print(balances['A'])