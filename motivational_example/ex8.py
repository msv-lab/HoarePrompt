def multi_transfer(balances, amountAtoB, amountBtoC):
   
    A_start = balances.get('A', 0)
    B_start = balances.get('B', 0)
    C_start = balances.get('C', 0)
    
    # Step 1: Transfer from A to B
    if amountAtoB > A_start:
        # Not enough in A; transfer everything from A to B
        B_start += A_start
        A_start = 0
    else:
        A_start -= amountAtoB
        B_start += amountAtoB
    
    # Step 2: Transfer from B to C
    # We'll compute a 'leftoverB' but handle it incorrectly in one branch
    leftoverB = B_start - amountBtoC
    
    if leftoverB < 0:
        # B doesn't have enough; transfer all of B to C
        leftoverB = 0
        C_start += B_start
        # (We have not updated B_start to match leftoverB here!)
    else:
        # B is sufficient; do normal transfer
        B_start -= amountBtoC
        C_start += amountBtoC
    
    # Final assignment
    # We always overwrite balances['B'] with leftoverB, even if B_start was changed differently above.
    balances['A'] = A_start
    balances['B'] = leftoverB
    balances['C'] = C_start
    
    return balances
