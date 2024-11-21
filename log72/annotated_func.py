#State of the program right berfore the function call: numbers is a list of integers.
def func_1(numbers):
    even_sum, odd_sum = 0, 0
    if (len(numbers) > 5) :
        for num in numbers:
            if num % 2 == 0:
                even_sum += num
            
        #State of the program after the  for loop has been executed: `even_sum` is the sum of all even integers in `numbers`, `odd_sum` remains 0, and `numbers` is a list of integers with length greater than 5.
    else :
        if (len(numbers) > 0) :
            for num in numbers:
                odd_sum += num
                
            #State of the program after the  for loop has been executed: `numbers` is a list of integers with length between 1 and 5, `even_sum` is 0, `odd_sum` is equal to the sum of all integers in `numbers`.
        else :
            print('Empty list')
        #State of the program after the if-else block has been executed: *`numbers` is a list of integers with a length between 0 and 5. If `numbers` is not empty, `odd_sum` is the sum of all integers in `numbers` and `even_sum` remains 0. If `numbers` is empty, `odd_sum` stays 0, `even_sum` is 0, and 'Empty list' is printed.
    #State of the program after the if-else block has been executed: *`numbers` is a list of integers. If the length of `numbers` is greater than 5, `even_sum` is the sum of all even integers in `numbers`, and `odd_sum` remains 0. If the length of `numbers` is between 1 and 5, `odd_sum` is the sum of all integers in `numbers`, while `even_sum` remains 0. If `numbers` is empty, both `even_sum` and `odd_sum` stay 0, and 'Empty list' is printed.
    return even_sum, odd_sum
    #The program returns the values of even_sum (the sum of all even integers in the list 'numbers' if its length is greater than 5) and odd_sum (the sum of all integers in 'numbers' if its length is between 1 and 5, otherwise 0)
#Overall this is what the function does:
The function accepts a list of integers `numbers`. If the length of the list is greater than 5, it returns the sum of all even integers in the list and 0 for the odd sum. If the length is between 1 and 5, it returns 0 for the even sum and the sum of all integers in the list for the odd sum. If the list is empty, it prints 'Empty list' and returns (0, 0) for both sums.

