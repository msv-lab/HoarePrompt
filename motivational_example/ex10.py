def calculate_final_price(base_price, store_discount, coupon_discount, tax_rate):
    
    discounted_price = base_price * (1 - store_discount)

    
    coupon_amount = base_price * coupon_discount  
    after_coupon = discounted_price - coupon_amount
 
    tax_amount = after_coupon * tax_rate

    final_price = after_coupon + tax_amount
    return final_price
