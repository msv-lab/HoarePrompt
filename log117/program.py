MOD = 998244353
def count_numbers(l, r, k):
    dp = {}
    return (count(r, k, dp) - count(l-1, k, dp)) % MOD
l, r, k = map(int, input().split())
def count(n, k, dp):
    if k == 0:
        return 0
    if (n, k) in dp:
        return dp[(n, k)]
    if n < 10**k:
        dp[(n, k)] = n
    else:
        dp[(n, k)] = 9
        for i in range(1, k):
            dp[(n, k)] += 9 * 10**(i-1) * (10**(k-i) - 10**(i-1))
        dp[(n, k)] += (10**(k-1) - 10**(k-2)) * (n // 10**(k-1) - 1)
        dp[(n, k)] %= MOD
    return dp[(n, k)]
    

# print(count_numbers(l, r, k))


# def is_divisible(number1, number2):
#     if number1 % number2 == 0:
#         return True


# def is_not_prime(n):
#     if n < 2:
#         return True
#     for i in range(2, n):
#         if is_divisible(n,i):
#             return True
#     return False

# import ast



# # def get_list_size(list):
# #     return len(list)

# # def find_Rotations(str1):
# #     n = get_list_size(str1)
# #     for i in range(1,n+1):
# #         if str1[i:] + str1[:i] == str1:
# #             return i
 
# def count_Primes_nums(n: int) -> int:
#     def is_prime(num: int) -> bool:
#         if num < 2:
#             return False
#         for i in range(2, int(num**0.5) + 1):
#                if num % i == 0:
#                    return False
#         return True
   
#     count = 0
#     for num in range(2, n):
#         if is_prime(num):
#             count += 1
#     return count

# print("SAA")
# import re

# print(count_Primes_nums(10))
# # def func_1(n: int) -> int:
# #     def func_2(num: int) -> bool:
# #         if num < 2:
# #             return False
# #         for i in range(2, int(num**0.5) + 1):
# #             if num % i == 0:
# #                 return False
# #         return True
# #     count = 0
# #     for num in range(2, n):
# #         if func_2(num):
# #             count += 1
# #     return count