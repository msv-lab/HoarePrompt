def apply_interest(account, daily_rate, monthly_rate):
   
    balance_before = account['balance']  # Original principal
    days = account['days_passed']

    # Case 1: Fewer than 30 days, apply daily interest only:
    if days < 30:
        # daily interest is compounding each day
        # for simplicity, do a naive 1-step compound approximation:
        # final = balance * (1 + daily_rate)^(days)
        daily_multiplier = (1 + daily_rate) ** days
        account['balance'] = balance_before * daily_multiplier
        

    # Case 2: 30 or more days, apply:
    #    1) 30 days of daily interest
    #    2) monthly interest on the result
    else:
        # Step A: apply 30 days of daily interest
        daily_multiplier = (1 + daily_rate) ** 30
        updated_balance = balance_before * daily_multiplier

        # BUG: monthly interest is incorrectly applied to balance_before
        #      Instead of updated_balance.
        # This might look okay at first glance: "we're applying monthly interest, right?"
        # But logically, we should be applying monthly interest to updated_balance.
        monthly_interest = balance_before * monthly_rate
        updated_balance += monthly_interest  # we add monthly interest computed off the old principal

        account['balance'] = updated_balance
    return account
