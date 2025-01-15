def calculate_balance(transaction):
    balance = 0
    penalty = 10
    
   
    balance += transaction
    if balance < 0:
        balance -= penalty  
        balance = 0  
    return balance
